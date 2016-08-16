from decimal import Decimal
import logging
import time

from xbterminal import defaults
from xbterminal.stages import amounts
from xbterminal.helpers import qr
from xbterminal.exceptions import NetworkError, ServerError

logger = logging.getLogger(__name__)


def bootup(state, ui):
    ui.showScreen('load_indefinite')

    ui.retranslateUi(
        state['remote_config']['language']['code'],
        state['remote_config']['currency']['prefix'])

    if state['remote_config']['status'] == 'active':
        return defaults.STAGES['idle']
    else:
        return defaults.STAGES['activate']


def activate(state, ui):
    ui.showScreen('activation')
    ui.setText('activation_server_lbl',
               state['remote_config']['remote_server'].split('//')[1])
    activation_code = state['client'].get_activation_code()
    ui.setText('activation_code_lbl', activation_code)
    while True:
        if state['remote_config']['status'] == 'active':
            return defaults.STAGES['idle']
        time.sleep(0.1)


def idle(state, ui):
    ui.showScreen('idle')
    while True:
        if state['screen_buttons']['idle_begin_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['idle_begin_btn'] = False
            return defaults.STAGES['payment']['pay_amount']
        # Communicate with the host system
        if state['client'].host_get_payout():
            return defaults.STAGES['selection']
        time.sleep(0.1)


def selection(state, ui):
    ui.showScreen('selection')
    current_credit = state['client'].host_get_payout()
    ui.setText('sel_amount_lbl',
               amounts.format_fiat_amount_pretty(current_credit, prefix=True))
    while True:
        if state['screen_buttons']['sel_pay_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['sel_pay_btn'] = False
            return defaults.STAGES['payment']['pay_amount']
        if state['screen_buttons']['sel_withdraw_btn'] or \
                state['keypad'].last_key_pressed == 'alt':
            state['screen_buttons']['sel_withdraw_btn'] = False
            state['withdrawal']['fiat_amount'] = current_credit
            return defaults.STAGES['withdrawal']['withdraw_loading1']
        time.sleep(0.1)


def pay_amount(state, ui):
    ui.showScreen('pay_amount')
    current_credit = state['client'].host_get_payout()
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
        if state['screen_buttons']['pamount_opt1_btn'] or \
                state['keypad'].last_key_pressed == 1:
            state['screen_buttons']['pamount_opt1_btn'] = False
            state['payment']['fiat_amount'] = options['pamount_opt1_btn']
            return defaults.STAGES['payment']['pay_confirm']
        elif state['screen_buttons']['pamount_opt2_btn'] or \
                state['keypad'].last_key_pressed == 2:
            state['screen_buttons']['pamount_opt2_btn'] = False
            state['payment']['fiat_amount'] = options['pamount_opt2_btn']
            return defaults.STAGES['payment']['pay_confirm']
        elif state['screen_buttons']['pamount_opt3_btn'] or \
                state['keypad'].last_key_pressed == 3:
            state['screen_buttons']['pamount_opt3_btn'] = False
            state['payment']['fiat_amount'] = options['pamount_opt3_btn']
            return defaults.STAGES['payment']['pay_confirm']
        elif state['screen_buttons']['pamount_opt4_btn'] or \
                state['keypad'].last_key_pressed == 4:
            state['screen_buttons']['pamount_opt4_btn'] = False
            state['payment']['fiat_amount'] = Decimal('0.00')
            return defaults.STAGES['payment']['pay_confirm']
        elif state['screen_buttons']['pamount_cancel_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['pamount_cancel_btn'] = False
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_confirm(state, ui):
    ui.showScreen('pay_confirm')
    assert state['payment']['fiat_amount'] >= 0
    current_credit = state['client'].host_get_payout()
    ui.setText('pconfirm_credit_lbl',
               amounts.format_fiat_amount_pretty(current_credit, prefix=True))
    ui.setText('pconfirm_amount_lbl',
               amounts.format_fiat_amount_pretty(state['payment']['fiat_amount'], prefix=True))
    while True:
        if state['screen_buttons']['pconfirm_decr_btn'] or \
                state['keypad'].last_key_pressed == 1:
            state['screen_buttons']['pconfirm_decr_btn'] = False
            state['keypad'].resetKey()
            state['payment']['fiat_amount'] -= Decimal('0.05')
            if state['payment']['fiat_amount'] < 0:
                state['payment']['fiat_amount'] = Decimal('0.00')
            ui.setText(
                'pconfirm_amount_lbl',
                amounts.format_fiat_amount_pretty(state['payment']['fiat_amount'], prefix=True))
        if state['screen_buttons']['pconfirm_incr_btn'] or \
                state['keypad'].last_key_pressed == 2:
            state['screen_buttons']['pconfirm_incr_btn'] = False
            state['keypad'].resetKey()
            state['payment']['fiat_amount'] += Decimal('0.05')
            ui.setText(
                'pconfirm_amount_lbl',
                amounts.format_fiat_amount_pretty(state['payment']['fiat_amount'], prefix=True))
        if state['screen_buttons']['pconfirm_confirm_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['pconfirm_confirm_btn'] = False
            if state['payment']['fiat_amount'] > 0:
                return defaults.STAGES['payment']['pay_loading']
        if state['screen_buttons']['pconfirm_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['pconfirm_goback_btn'] = False
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['payment']['pay_amount']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_loading(state, ui):
    ui.showScreen('load_indefinite')

    if state['payment']['fiat_amount'] is None:
        return defaults.STAGES['payment']['pay_amount']

    while True:
        try:
            payment_info = state['client'].create_payment_order(
                fiat_amount=state['payment']['fiat_amount'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        else:
            # Payment parameters loaded
            state['payment'].update(payment_info)
            return defaults.STAGES['payment']['pay_info']


def pay_info(state, ui):
    ui.showScreen('pay_info')
    ui.setText('pinfo_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(state['payment']['fiat_amount'], prefix=True))
    ui.setText('pinfo_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['payment']['btc_amount']))
    ui.setText('pinfo_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(state['payment']['exchange_rate']))
    while True:
        if state['screen_buttons']['pinfo_pay_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['pinfo_pay_btn'] = False
            # Prepare QR image
            qr.qr_gen(state['payment']['payment_uri'],
                      defaults.QR_IMAGE_PATH)
            return defaults.STAGES['payment']['pay_wait']
        if state['screen_buttons']['pinfo_cancel_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['pinfo_cancel_btn'] = False
            _clear_payment_runtime(state, ui, cancel_order=True)
            return defaults.STAGES['payment']['pay_amount']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(state, ui, cancel_order=True)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_wait(state, ui):
    ui.showScreen('pay_wait')
    ui.setText('pwait_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['payment']['btc_amount'], prefix=True))
    ui.setImage('pwait_qr_img', defaults.QR_IMAGE_PATH)
    logger.info(
        'local payment requested, '
        'amount fiat: {amount_fiat}, '
        'amount btc: {amount_btc}, '
        'rate: {effective_rate}'.format(
            amount_fiat=state['payment']['fiat_amount'],
            amount_btc=state['payment']['btc_amount'],
            effective_rate=state['payment']['exchange_rate']))
    logger.info('payment uri: {}'.format(state['payment']['payment_uri']))
    state['client'].start_bluetooth_server(payment_uid=state['payment']['uid'])
    state['client'].start_nfc_server(message=state['payment']['payment_uri'])
    while True:
        if state['screen_buttons']['pwait_cancel_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['pwait_cancel_btn'] = False
            _clear_payment_runtime(state, ui, cancel_order=True)
            state['client'].stop_nfc_server()
            state['client'].stop_bluetooth_server()
            return defaults.STAGES['payment']['pay_amount']

        payment_status = state['client'].get_payment_status(
            uid=state['payment']['uid'])
        if payment_status in ['notified', 'confirmed']:
            state['payment']['receipt_url'] = state['client'].get_payment_receipt(
                uid=state['payment']['uid'])
            logger.debug('payment received, receipt: {}'.format(state['payment']['receipt_url']))
            state['client'].host_add_credit(fiat_amount=state['payment']['fiat_amount'])
            state['client'].stop_nfc_server()
            state['client'].stop_bluetooth_server()
            return defaults.STAGES['payment']['pay_success']

        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(state, ui, cancel_order=True)
            state['client'].stop_nfc_server()
            state['client'].stop_bluetooth_server()
            return defaults.STAGES['payment']['pay_cancel']

        time.sleep(0.5)


def pay_success(state, ui):
    assert state['payment']['receipt_url']
    ui.showScreen('pay_success')
    ui.setText('psuccess_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['payment']['btc_amount']))
    while True:
        if state['screen_buttons']['psuccess_yes_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['psuccess_yes_btn'] = False
            qr.qr_gen(state['payment']['receipt_url'],
                      defaults.QR_IMAGE_PATH)
            return defaults.STAGES['payment']['pay_receipt']
        if state['screen_buttons']['psuccess_no_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['psuccess_no_btn'] = False
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_receipt(state, ui):
    assert state['payment']['receipt_url']
    ui.showScreen('pay_receipt')
    ui.setImage('preceipt_receipt_qr_img', defaults.QR_IMAGE_PATH)
    state['client'].start_nfc_server(message=state['payment']['receipt_url'])
    while True:
        if state['screen_buttons']['preceipt_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['preceipt_goback_btn'] = False
            state['client'].stop_nfc_server()
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            state['client'].stop_nfc_server()
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_cancel(state, ui):
    ui.showScreen('pay_cancel')
    while True:
        if state['keypad'].last_key_pressed is not None:
            _clear_payment_runtime(state, ui)
            return defaults.STAGES['payment']['pay_amount']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_loading1(state, ui):
    ui.showScreen('load_indefinite')
    assert state['withdrawal']['fiat_amount'] > 0
    while True:
        try:
            withdrawal_info = state['client'].create_withdrawal_order(
                fiat_amount=state['withdrawal']['fiat_amount'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        else:
            state['withdrawal'].update(withdrawal_info)
            return defaults.STAGES['withdrawal']['withdraw_scan']


def withdraw_scan(state, ui):
    ui.showScreen('withdraw_scan')
    assert state['withdrawal']['uid'] is not None
    ui.setText(
        'wscan_fiat_amount_lbl',
        amounts.format_fiat_amount_pretty(state['withdrawal']['fiat_amount'], prefix=True))
    ui.setText(
        'wscan_btc_amount_lbl',
        amounts.format_btc_amount_pretty(state['withdrawal']['btc_amount'], prefix=True))
    ui.setText(
        'wscan_xrate_amount_lbl',
        amounts.format_exchange_rate_pretty(state['withdrawal']['exchange_rate']))
    state['client'].start_qr_scanner()
    while True:
        default_address = state['gui_config'].get('default_withdrawal_address')
        address = state['client'].get_scanned_address() or default_address
        if address:
            logger.debug('address scanned: {0}'.format(address))
            state['client'].stop_qr_scanner()
            state['withdrawal']['address'] = address
            return defaults.STAGES['withdrawal']['withdraw_confirm']
        if state['screen_buttons']['wscan_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['wscan_goback_btn'] = False
            state['client'].stop_qr_scanner()
            _clear_withdrawal_runtime(state, ui, clear_amount=False, cancel_order=True)
            return defaults.STAGES['selection']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            state['client'].stop_qr_scanner()
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_confirm(state, ui):
    ui.showScreen('withdraw_confirm')
    assert state['withdrawal']['address'] is not None
    ui.setText('wconfirm_address_lbl', state['withdrawal']['address'])
    ui.setText('wconfirm_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(state['withdrawal']['fiat_amount'], prefix=True))
    ui.setText('wconfirm_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['withdrawal']['btc_amount']))
    ui.setText('wconfirm_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(state['withdrawal']['exchange_rate']))
    while True:
        if state['screen_buttons']['wconfirm_confirm_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['wconfirm_confirm_btn'] = False
            return defaults.STAGES['withdrawal']['withdraw_loading2']
        elif state['screen_buttons']['wconfirm_cancel_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['wconfirm_cancel_btn'] = False
            _clear_withdrawal_runtime(state, ui, cancel_order=True)
            return defaults.STAGES['idle']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_loading2(state, ui):
    ui.showScreen('load_indefinite')
    assert state['withdrawal']['address'] is not None
    while True:
        withdrawal_status = state['client'].get_withdrawal_status(
            uid=state['withdrawal']['uid'])
        if withdrawal_status == 'new':
            try:
                withdrawal_info = state['client'].confirm_withdrawal(
                    uid=state['withdrawal']['uid'],
                    address=state['withdrawal']['address'])
            except NetworkError:
                logger.warning('network error, retry in 5 seconds')
                time.sleep(5)
                continue
            except ServerError:
                _clear_withdrawal_runtime(state, ui)
                return defaults.STAGES['idle']
            state['withdrawal'].update(withdrawal_info)
            continue
        elif withdrawal_status == 'completed':
            state['withdrawal']['receipt_url'] = state['client'].get_withdrawal_receipt(
                uid=state['withdrawal']['uid'])
            logger.debug('withdrawal finished, receipt: {}'.format(
                state['withdrawal']['receipt_url']))
            state['client'].host_withdraw(
                fiat_amount=state['withdrawal']['fiat_amount'])
            return defaults.STAGES['withdrawal']['withdraw_success']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.5)


def withdraw_success(state, ui):
    ui.showScreen('withdraw_success')
    assert state['withdrawal']['receipt_url']
    ui.setText('wsuccess_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['withdrawal']['btc_amount']))
    while True:
        if state['screen_buttons']['wsuccess_yes_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['wsuccess_yes_btn'] = False
            qr.qr_gen(state['withdrawal']['receipt_url'],
                      defaults.QR_IMAGE_PATH)
            return defaults.STAGES['withdrawal']['withdraw_receipt']
        if state['screen_buttons']['wsuccess_no_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['wsuccess_no_btn'] = False
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_receipt(state, ui):
    ui.showScreen('withdraw_receipt')
    assert state['withdrawal']['receipt_url']
    ui.setImage('wreceipt_receipt_qr_img', defaults.QR_IMAGE_PATH)
    state['client'].start_nfc_server(message=state['withdrawal']['receipt_url'])
    while True:
        if state['screen_buttons']['wreceipt_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['wreceipt_goback_btn'] = False
            state['client'].stop_nfc_server()
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        if state['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            state['client'].stop_nfc_server()
            _clear_withdrawal_runtime(state, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def _clear_payment_runtime(state, ui, cancel_order=False):
    logger.debug('clearing payment runtime')
    ui.showScreen('load_indefinite')

    if cancel_order:
        state['client'].cancel_payment(uid=state['payment']['uid'])

    state['payment']['uid'] = None
    state['payment']['fiat_amount'] = None
    state['payment']['btc_amount'] = None
    state['payment']['exchange_rate'] = None
    state['payment']['payment_uri'] = None
    state['payment']['receipt_url'] = None

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


def _clear_withdrawal_runtime(state, ui, clear_amount=True, cancel_order=False):
    logger.debug('clearing withdrawal runtime')
    ui.showScreen('load_indefinite')

    if cancel_order:
        state['client'].cancel_withdrawal(uid=state['withdrawal']['uid'])

    if clear_amount:
        state['withdrawal']['fiat_amount'] = None

    state['withdrawal']['uid'] = None
    state['withdrawal']['btc_amount'] = None
    state['withdrawal']['exchange_rate'] = None
    state['withdrawal']['address'] = None
    state['withdrawal']['receipt_url'] = None

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
