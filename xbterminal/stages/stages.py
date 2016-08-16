from decimal import Decimal
import logging
import time

from xbterminal import defaults
from xbterminal.stages import amounts
from xbterminal.helpers import qr
from xbterminal.exceptions import NetworkError, ServerError

logger = logging.getLogger(__name__)


def bootup(run, ui):
    ui.showScreen('load_indefinite')

    ui.retranslateUi(
        run['remote_config']['language']['code'],
        run['remote_config']['currency']['prefix'])

    if run['remote_config']['status'] == 'active':
        return defaults.STAGES['idle']
    else:
        return defaults.STAGES['activate']


def activate(run, ui):
    ui.showScreen('activation')
    ui.setText('activation_server_lbl',
               run['remote_config']['remote_server'].split('//')[1])
    activation_code = run['client'].get_activation_code()
    ui.setText('activation_code_lbl', activation_code)
    while True:
        if run['remote_config']['status'] == 'active':
            return defaults.STAGES['idle']
        time.sleep(0.1)


def idle(run, ui):
    ui.showScreen('idle')
    while True:
        if run['screen_buttons']['idle_begin_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['idle_begin_btn'] = False
            return defaults.STAGES['payment']['pay_amount']
        # Communicate with the host system
        if run['client'].host_get_payout():
            return defaults.STAGES['selection']
        time.sleep(0.1)


def selection(run, ui):
    ui.showScreen('selection')
    current_credit = run['client'].host_get_payout()
    ui.setText('sel_amount_lbl',
               amounts.format_fiat_amount_pretty(current_credit, prefix=True))
    while True:
        if run['screen_buttons']['sel_pay_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['sel_pay_btn'] = False
            return defaults.STAGES['payment']['pay_amount']
        if run['screen_buttons']['sel_withdraw_btn'] or \
                run['keypad'].last_key_pressed == 'alt':
            run['screen_buttons']['sel_withdraw_btn'] = False
            run['withdrawal']['fiat_amount'] = current_credit
            return defaults.STAGES['withdrawal']['withdraw_loading1']
        time.sleep(0.1)


def pay_amount(run, ui):
    ui.showScreen('pay_amount')
    current_credit = run['client'].host_get_payout()
    ui.setText('pamount_credit_lbl',
               amounts.format_fiat_amount_pretty(current_credit, prefix=True))
    options = {
        'pamount_opt1_btn': Decimal('1.00'),
        'pamount_opt2_btn': Decimal('2.50'),
        'pamount_opt3_btn': Decimal('10.00'),
    }
    for button, amount in options.items():
        ui.setText(button, amounts.format_fiat_amount_pretty(amount, prefix=True))
    while True:
        if run['screen_buttons']['pamount_opt1_btn'] or \
                run['keypad'].last_key_pressed == 1:
            run['screen_buttons']['pamount_opt1_btn'] = False
            run['payment']['fiat_amount'] = options['pamount_opt1_btn']
            return defaults.STAGES['payment']['pay_confirm']
        elif run['screen_buttons']['pamount_opt2_btn'] or \
                run['keypad'].last_key_pressed == 2:
            run['screen_buttons']['pamount_opt2_btn'] = False
            run['payment']['fiat_amount'] = options['pamount_opt2_btn']
            return defaults.STAGES['payment']['pay_confirm']
        elif run['screen_buttons']['pamount_opt3_btn'] or \
                run['keypad'].last_key_pressed == 3:
            run['screen_buttons']['pamount_opt3_btn'] = False
            run['payment']['fiat_amount'] = options['pamount_opt3_btn']
            return defaults.STAGES['payment']['pay_confirm']
        elif run['screen_buttons']['pamount_opt4_btn'] or \
                run['keypad'].last_key_pressed == 4:
            run['screen_buttons']['pamount_opt4_btn'] = False
            run['payment']['fiat_amount'] = Decimal('0.00')
            return defaults.STAGES['payment']['pay_confirm']
        elif run['screen_buttons']['pamount_cancel_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['pamount_cancel_btn'] = False
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_confirm(run, ui):
    ui.showScreen('pay_confirm')
    assert run['payment']['fiat_amount'] >= 0
    current_credit = run['client'].host_get_payout()
    ui.setText('pconfirm_credit_lbl',
               amounts.format_fiat_amount_pretty(current_credit, prefix=True))
    ui.setText('pconfirm_amount_lbl',
               amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
    while True:
        if run['screen_buttons']['pconfirm_decr_btn'] or \
                run['keypad'].last_key_pressed == 1:
            run['screen_buttons']['pconfirm_decr_btn'] = False
            run['keypad'].resetKey()
            run['payment']['fiat_amount'] -= Decimal('0.05')
            if run['payment']['fiat_amount'] < 0:
                run['payment']['fiat_amount'] = Decimal('0.00')
            ui.setText(
                'pconfirm_amount_lbl',
                amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
        if run['screen_buttons']['pconfirm_incr_btn'] or \
                run['keypad'].last_key_pressed == 2:
            run['screen_buttons']['pconfirm_incr_btn'] = False
            run['keypad'].resetKey()
            run['payment']['fiat_amount'] += Decimal('0.05')
            ui.setText(
                'pconfirm_amount_lbl',
                amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
        if run['screen_buttons']['pconfirm_confirm_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['pconfirm_confirm_btn'] = False
            if run['payment']['fiat_amount'] > 0:
                return defaults.STAGES['payment']['pay_loading']
        if run['screen_buttons']['pconfirm_goback_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['pconfirm_goback_btn'] = False
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['payment']['pay_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_loading(run, ui):
    ui.showScreen('load_indefinite')

    if run['payment']['fiat_amount'] is None:
        return defaults.STAGES['payment']['pay_amount']

    while True:
        try:
            payment_info = run['client'].create_payment_order(
                fiat_amount=run['payment']['fiat_amount'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        else:
            # Payment parameters loaded
            run['payment'].update(payment_info)
            return defaults.STAGES['payment']['pay_info']


def pay_info(run, ui):
    ui.showScreen('pay_info')
    ui.setText('pinfo_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
    ui.setText('pinfo_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['payment']['btc_amount']))
    ui.setText('pinfo_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(run['payment']['exchange_rate']))
    while True:
        if run['screen_buttons']['pinfo_pay_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['pinfo_pay_btn'] = False
            # Prepare QR image
            qr.qr_gen(run['payment']['payment_uri'],
                      defaults.QR_IMAGE_PATH)
            return defaults.STAGES['payment']['pay_wait']
        if run['screen_buttons']['pinfo_cancel_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['pinfo_cancel_btn'] = False
            _clear_payment_runtime(run, ui, cancel_order=True)
            return defaults.STAGES['payment']['pay_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui, cancel_order=True)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_wait(run, ui):
    ui.showScreen('pay_wait')
    ui.setText('pwait_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['payment']['btc_amount'], prefix=True))
    ui.setImage('pwait_qr_img', defaults.QR_IMAGE_PATH)
    logger.info(
        'local payment requested, '
        'amount fiat: {amount_fiat}, '
        'amount btc: {amount_btc}, '
        'rate: {effective_rate}'.format(
            amount_fiat=run['payment']['fiat_amount'],
            amount_btc=run['payment']['btc_amount'],
            effective_rate=run['payment']['exchange_rate']))
    logger.info('payment uri: {}'.format(run['payment']['payment_uri']))
    run['client'].start_bluetooth_server(payment_uid=run['payment']['uid'])
    run['client'].start_nfc_server(message=run['payment']['payment_uri'])
    while True:
        if run['screen_buttons']['pwait_cancel_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['pwait_cancel_btn'] = False
            _clear_payment_runtime(run, ui, cancel_order=True)
            run['client'].stop_nfc_server()
            run['client'].stop_bluetooth_server()
            return defaults.STAGES['payment']['pay_amount']

        payment_status = run['client'].get_payment_status(
            uid=run['payment']['uid'])
        if payment_status in ['notified', 'confirmed']:
            run['payment']['receipt_url'] = run['client'].get_payment_receipt(
                uid=run['payment']['uid'])
            logger.debug('payment received, receipt: {}'.format(run['payment']['receipt_url']))
            run['client'].host_add_credit(fiat_amount=run['payment']['fiat_amount'])
            run['client'].stop_nfc_server()
            run['client'].stop_bluetooth_server()
            return defaults.STAGES['payment']['pay_success']

        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui, cancel_order=True)
            run['client'].stop_nfc_server()
            run['client'].stop_bluetooth_server()
            return defaults.STAGES['payment']['pay_cancel']

        time.sleep(0.5)


def pay_success(run, ui):
    assert run['payment']['receipt_url']
    ui.showScreen('pay_success')
    ui.setText('psuccess_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['payment']['btc_amount']))
    while True:
        if run['screen_buttons']['psuccess_yes_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['psuccess_yes_btn'] = False
            qr.qr_gen(run['payment']['receipt_url'],
                      defaults.QR_IMAGE_PATH)
            return defaults.STAGES['payment']['pay_receipt']
        if run['screen_buttons']['psuccess_no_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['psuccess_no_btn'] = False
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_receipt(run, ui):
    assert run['payment']['receipt_url']
    ui.showScreen('pay_receipt')
    ui.setImage('preceipt_receipt_qr_img', defaults.QR_IMAGE_PATH)
    run['client'].start_nfc_server(message=run['payment']['receipt_url'])
    while True:
        if run['screen_buttons']['preceipt_goback_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['preceipt_goback_btn'] = False
            run['client'].stop_nfc_server()
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['client'].stop_nfc_server()
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_cancel(run, ui):
    ui.showScreen('pay_cancel')
    while True:
        if run['keypad'].last_key_pressed is not None:
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['payment']['pay_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_loading1(run, ui):
    ui.showScreen('load_indefinite')
    assert run['withdrawal']['fiat_amount'] > 0
    while True:
        try:
            withdrawal_info = run['client'].create_withdrawal_order(
                fiat_amount=run['withdrawal']['fiat_amount'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        else:
            run['withdrawal'].update(withdrawal_info)
            return defaults.STAGES['withdrawal']['withdraw_scan']


def withdraw_scan(run, ui):
    ui.showScreen('withdraw_scan')
    assert run['withdrawal']['uid'] is not None
    ui.setText(
        'wscan_fiat_amount_lbl',
        amounts.format_fiat_amount_pretty(run['withdrawal']['fiat_amount'], prefix=True))
    ui.setText(
        'wscan_btc_amount_lbl',
        amounts.format_btc_amount_pretty(run['withdrawal']['btc_amount'], prefix=True))
    ui.setText(
        'wscan_xrate_amount_lbl',
        amounts.format_exchange_rate_pretty(run['withdrawal']['exchange_rate']))
    run['client'].start_qr_scanner()
    while True:
        default_address = run['gui_config'].get('default_withdrawal_address')
        address = run['client'].get_scanned_address() or default_address
        if address:
            logger.debug('address scanned: {0}'.format(address))
            run['client'].stop_qr_scanner()
            run['withdrawal']['address'] = address
            return defaults.STAGES['withdrawal']['withdraw_confirm']
        if run['screen_buttons']['wscan_goback_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['wscan_goback_btn'] = False
            run['client'].stop_qr_scanner()
            _clear_withdrawal_runtime(run, ui, clear_amount=False, cancel_order=True)
            return defaults.STAGES['selection']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['client'].stop_qr_scanner()
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_confirm(run, ui):
    ui.showScreen('withdraw_confirm')
    assert run['withdrawal']['address'] is not None
    ui.setText('wconfirm_address_lbl', run['withdrawal']['address'])
    ui.setText('wconfirm_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(run['withdrawal']['fiat_amount'], prefix=True))
    ui.setText('wconfirm_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['withdrawal']['btc_amount']))
    ui.setText('wconfirm_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(run['withdrawal']['exchange_rate']))
    while True:
        if run['screen_buttons']['wconfirm_confirm_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['wconfirm_confirm_btn'] = False
            return defaults.STAGES['withdrawal']['withdraw_loading2']
        elif run['screen_buttons']['wconfirm_cancel_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['wconfirm_cancel_btn'] = False
            _clear_withdrawal_runtime(run, ui, cancel_order=True)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_loading2(run, ui):
    ui.showScreen('load_indefinite')
    assert run['withdrawal']['address'] is not None
    while True:
        withdrawal_status = run['client'].get_withdrawal_status(
            uid=run['withdrawal']['uid'])
        if withdrawal_status == 'new':
            try:
                withdrawal_info = run['client'].confirm_withdrawal(
                    uid=run['withdrawal']['uid'],
                    address=run['withdrawal']['address'])
            except NetworkError:
                logger.warning('network error, retry in 5 seconds')
                time.sleep(5)
                continue
            except ServerError:
                _clear_withdrawal_runtime(run, ui)
                return defaults.STAGES['idle']
            run['withdrawal'].update(withdrawal_info)
            continue
        elif withdrawal_status == 'completed':
            run['withdrawal']['receipt_url'] = run['client'].get_withdrawal_receipt(
                uid=run['withdrawal']['uid'])
            logger.debug('withdrawal finished, receipt: {}'.format(
                run['withdrawal']['receipt_url']))
            run['client'].host_withdraw(
                fiat_amount=run['withdrawal']['fiat_amount'])
            return defaults.STAGES['withdrawal']['withdraw_success']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.5)


def withdraw_success(run, ui):
    ui.showScreen('withdraw_success')
    assert run['withdrawal']['receipt_url']
    ui.setText('wsuccess_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['withdrawal']['btc_amount']))
    while True:
        if run['screen_buttons']['wsuccess_yes_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['wsuccess_yes_btn'] = False
            qr.qr_gen(run['withdrawal']['receipt_url'],
                      defaults.QR_IMAGE_PATH)
            return defaults.STAGES['withdrawal']['withdraw_receipt']
        if run['screen_buttons']['wsuccess_no_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['wsuccess_no_btn'] = False
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_receipt(run, ui):
    ui.showScreen('withdraw_receipt')
    assert run['withdrawal']['receipt_url']
    ui.setImage('wreceipt_receipt_qr_img', defaults.QR_IMAGE_PATH)
    run['client'].start_nfc_server(message=run['withdrawal']['receipt_url'])
    while True:
        if run['screen_buttons']['wreceipt_goback_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['wreceipt_goback_btn'] = False
            run['client'].stop_nfc_server()
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['client'].stop_nfc_server()
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def _clear_payment_runtime(run, ui, cancel_order=False):
    logger.debug('clearing payment runtime')
    ui.showScreen('load_indefinite')

    if cancel_order:
        run['client'].cancel_payment(uid=run['payment']['uid'])

    run['payment']['uid'] = None
    run['payment']['fiat_amount'] = None
    run['payment']['btc_amount'] = None
    run['payment']['exchange_rate'] = None
    run['payment']['payment_uri'] = None
    run['payment']['receipt_url'] = None

    ui.setText('pinfo_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(Decimal(0), prefix=True))
    ui.setText('pinfo_btc_amount_lbl',
               amounts.format_btc_amount_pretty(Decimal(0)))
    ui.setText('pinfo_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(Decimal(0)))
    ui.setText('pwait_btc_amount_lbl',
               amounts.format_btc_amount_pretty(Decimal(0), prefix=True))
    ui.setImage('pwait_qr_img', None)
    ui.setImage('preceipt_receipt_qr_img', None)


def _clear_withdrawal_runtime(run, ui, clear_amount=True, cancel_order=False):
    logger.debug('clearing withdrawal runtime')
    ui.showScreen('load_indefinite')

    if cancel_order:
        run['client'].cancel_withdrawal(uid=run['withdrawal']['uid'])

    if clear_amount:
        run['withdrawal']['fiat_amount'] = None

    run['withdrawal']['uid'] = None
    run['withdrawal']['btc_amount'] = None
    run['withdrawal']['exchange_rate'] = None
    run['withdrawal']['address'] = None
    run['withdrawal']['receipt_url'] = None

    ui.setText('wscan_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(Decimal(0), prefix=True))
    ui.setText('wscan_btc_amount_lbl',
               amounts.format_btc_amount_pretty(Decimal(0), prefix=True))
    ui.setText('wscan_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(Decimal(0)))
    ui.setText('wconfirm_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(Decimal(0), prefix=True))
    ui.setText('wconfirm_btc_amount_lbl',
               amounts.format_btc_amount_pretty(Decimal(0), prefix=True))
    ui.setText('wconfirm_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(Decimal(0)))
    ui.setImage('wreceipt_receipt_qr_img', None)
