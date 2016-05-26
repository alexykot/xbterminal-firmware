from decimal import Decimal
import logging
import time

logger = logging.getLogger(__name__)

import xbterminal
from xbterminal import defaults
from xbterminal.stages import activation, amounts, payment, withdrawal

import xbterminal.helpers.bt
import xbterminal.helpers.camera
import xbterminal.helpers.clock
import xbterminal.helpers.configs
import xbterminal.helpers.host
import xbterminal.helpers.nfcpy
import xbterminal.helpers.qr
import xbterminal.gui.gui
from xbterminal.exceptions import NetworkError, ServerError


def bootup(run, ui):
    ui.showScreen('load_indefinite')

    # Check system clock
    # BBB has no battery, so system time gets reset after every reboot and may be wildly incorrect
    while True:
        internet_time = xbterminal.helpers.clock.get_internet_time()
        time_delta = abs(time.time() - internet_time)
        if time_delta < 60:  # 1 minute
            logger.info('clock synchronized')
            run['init']['clock_synchronized'] = True
            run['local_config']['last_started'] = time.time()
            xbterminal.helpers.configs.save_local_config(run['local_config'])
            break
        logger.warning('machine time differs from internet time: {0}'.format(time_delta))
        time.sleep(5)

    # Initialize bluetooth and NFC servers
    run['host_system'] = xbterminal.helpers.host.HostSystem(
        use_mock=run['local_config'].get('use_cctalk_mock', True))
    run['bluetooth_server'] = xbterminal.helpers.bt.BluetoothServer()
    run['nfc_server'] = xbterminal.helpers.nfcpy.NFCServer()
    run['qr_scanner'] = xbterminal.helpers.camera.QRScanner(backend='fswebcam')

    # Check registration
    if not activation.is_registered():
        try:
            run['local_config']['activation_code'] = activation.register_device()
        except Exception as error:
            # Registration error
            logger.exception(error)
            return defaults.STAGES['application_halt']
        xbterminal.helpers.configs.save_local_config(run['local_config'])
    run['init']['registration'] = True

    # Wait for remote config
    while True:
        if run['init']['remote_config']:
            break
        time.sleep(1)

    logger.info('working with {0}'.format(
        run['remote_config']['bitcoin_network']))

    if run['remote_config']['status'] == 'active':
        return defaults.STAGES['idle']
    else:
        return defaults.STAGES['activate']


def activate(run, ui):
    ui.showScreen('activation')
    ui.setText('activation_server_lbl',
               run['remote_server'].split('//')[1])
    ui.setText('activation_code_lbl',
               run['local_config']['activation_code'])
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
        if run['host_system'].get_payout():
            return defaults.STAGES['selection']
        time.sleep(0.1)


def selection(run, ui):
    ui.showScreen('selection')
    current_credit = run['host_system'].get_payout()
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
    current_credit = run['host_system'].get_payout()
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
    current_credit = run['host_system'].get_payout()
    ui.setText('pconfirm_credit_lbl',
               amounts.format_fiat_amount_pretty(current_credit, prefix=True))
    ui.setText('pconfirm_amount_lbl', amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
    while True:
        if run['screen_buttons']['pconfirm_decr_btn'] or \
                run['keypad'].last_key_pressed == 1:
            run['screen_buttons']['pconfirm_decr_btn'] = False
            run['keypad'].resetKey()
            run['payment']['fiat_amount'] -= Decimal('0.05')
            if run['payment']['fiat_amount'] < 0:
                run['payment']['fiat_amount'] = Decimal('0.00')
            ui.setText('pconfirm_amount_lbl', amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
        if run['screen_buttons']['pconfirm_incr_btn'] or \
                run['keypad'].last_key_pressed == 2:
            run['screen_buttons']['pconfirm_incr_btn'] = False
            run['keypad'].resetKey()
            run['payment']['fiat_amount'] += Decimal('0.05')
            ui.setText('pconfirm_amount_lbl', amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
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
            run['payment']['order'] = payment.Payment.create_order(run['payment']['fiat_amount'],
                                                                   run['bluetooth_server'].mac_address)
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        else:
            # Payment parameters loaded
            return defaults.STAGES['payment']['pay_info']


def pay_info(run, ui):
    ui.showScreen('pay_info')
    ui.setText('pinfo_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(run['payment']['fiat_amount'], prefix=True))
    ui.setText('pinfo_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['payment']['order'].btc_amount))
    ui.setText('pinfo_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(run['payment']['order'].exchange_rate))
    while True:
        if run['screen_buttons']['pinfo_pay_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['pinfo_pay_btn'] = False
            # Prepare QR image
            run['payment']['qr_image_path'] = defaults.QR_IMAGE_PATH
            xbterminal.helpers.qr.qr_gen(run['payment']['order'].payment_uri,
                                         run['payment']['qr_image_path'])
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
               amounts.format_btc_amount_pretty(run['payment']['order'].btc_amount, prefix=True))
    ui.setImage('pwait_qr_img', run['payment']['qr_image_path'])
    logger.info(
        'local payment requested, '
        'amount fiat: {amount_fiat}, '
        'amount btc: {amount_btc}, '
        'rate: {effective_rate}'.format(
            amount_fiat=run['payment']['fiat_amount'],
            amount_btc=run['payment']['order'].btc_amount,
            effective_rate=run['payment']['order'].exchange_rate))
    logger.info('payment uri: {}'.format(run['payment']['order'].payment_uri))
    run['bluetooth_server'].start(run['payment']['order'])
    while True:
        if run['screen_buttons']['pwait_cancel_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['pwait_cancel_btn'] = False
            _clear_payment_runtime(run, ui, cancel_order=True)
            run['nfc_server'].stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['pay_amount']

        if not run['nfc_server'].is_active():
            run['nfc_server'].start(run['payment']['order'].payment_uri)
            time.sleep(0.5)

        run['payment']['receipt_url'] = run['payment']['order'].check()
        if run['payment']['receipt_url'] is not None:
            logger.debug('payment received, receipt: {}'.format(run['payment']['receipt_url']))
            run['host_system'].add_credit(run['payment']['fiat_amount'])
            run['nfc_server'].stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['pay_success']

        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui, cancel_order=True)
            run['nfc_server'].stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['pay_cancel']

        time.sleep(0.5)


def pay_success(run, ui):
    assert run['payment']['receipt_url']
    ui.showScreen('pay_success')
    ui.setText('psuccess_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['payment']['order'].btc_amount))
    while True:
        if run['screen_buttons']['psuccess_yes_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['psuccess_yes_btn'] = False
            run['payment']['qr_image_path'] = defaults.QR_IMAGE_PATH
            xbterminal.helpers.qr.qr_gen(run['payment']['receipt_url'],
                                         run['payment']['qr_image_path'])
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
    ui.setImage('preceipt_receipt_qr_img', run['payment']['qr_image_path'])
    while True:
        if not run['nfc_server'].is_active():
            run['nfc_server'].start(run['payment']['receipt_url'])
            time.sleep(0.5)
        if run['screen_buttons']['preceipt_goback_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['preceipt_goback_btn'] = False
            run['nfc_server'].stop()
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['nfc_server'].stop()
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
            run['withdrawal']['order'] = withdrawal.Withdrawal.create_order(
                run['withdrawal']['fiat_amount'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        else:
            return defaults.STAGES['withdrawal']['withdraw_scan']


def withdraw_scan(run, ui):
    ui.showScreen('withdraw_scan')
    assert run['withdrawal']['order'] is not None
    ui.setText('wscan_fiat_amount_lbl', amounts.format_fiat_amount_pretty(run['withdrawal']['fiat_amount'], prefix=True))
    ui.setText('wscan_btc_amount_lbl', amounts.format_btc_amount_pretty(run['withdrawal']['order'].btc_amount, prefix=True))
    ui.setText('wscan_xrate_amount_lbl', amounts.format_exchange_rate_pretty(run['withdrawal']['order'].exchange_rate))
    run['qr_scanner'].start()
    while True:
        default_address = run['local_config'].get('default_withdrawal_address')
        address = withdrawal.get_bitcoin_address(
            run['qr_scanner'].get_data() or '') or default_address
        if address:
            logger.debug('address scanned: {0}'.format(address))
            run['qr_scanner'].stop()
            run['withdrawal']['address'] = address
            return defaults.STAGES['withdrawal']['withdraw_confirm']
        if run['screen_buttons']['wscan_goback_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['wscan_goback_btn'] = False
            run['qr_scanner'].stop()
            _clear_withdrawal_runtime(run, ui, clear_amount=False, cancel_order=True)
            return defaults.STAGES['selection']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['qr_scanner'].stop()
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
               amounts.format_btc_amount_pretty(run['withdrawal']['order'].btc_amount))
    ui.setText('wconfirm_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(run['withdrawal']['order'].exchange_rate))
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
        if not run['withdrawal']['order'].confirmed:
            try:
                run['withdrawal']['order'].confirm(run['withdrawal']['address'])
            except NetworkError:
                logger.warning('network error, retry in 5 seconds')
                time.sleep(5)
                continue
            except ServerError:
                _clear_withdrawal_runtime(run, ui)
                return defaults.STAGES['idle']
        run['withdrawal']['receipt_url'] = run['withdrawal']['order'].check()
        if run['withdrawal']['receipt_url'] is not None:
            logger.debug('withdrawal finished, receipt: {}'.format(run['withdrawal']['receipt_url']))
            run['host_system'].withdraw(run['withdrawal']['fiat_amount'])
            return defaults.STAGES['withdrawal']['withdraw_success']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.5)


def withdraw_success(run, ui):
    ui.showScreen('withdraw_success')
    assert run['withdrawal']['receipt_url']
    ui.setText('wsuccess_btc_amount_lbl',
               amounts.format_btc_amount_pretty(run['withdrawal']['order'].btc_amount))
    while True:
        if run['screen_buttons']['wsuccess_yes_btn'] or \
                run['keypad'].last_key_pressed == 'enter':
            run['screen_buttons']['wsuccess_yes_btn'] = False
            run['withdrawal']['qr_image_path'] = defaults.QR_IMAGE_PATH
            xbterminal.helpers.qr.qr_gen(run['withdrawal']['receipt_url'],
                                         run['withdrawal']['qr_image_path'])
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
    assert run['withdrawal']['qr_image_path'] is not None
    ui.setImage('wreceipt_receipt_qr_img', run['withdrawal']['qr_image_path'])
    while True:
        if not run['nfc_server'].is_active():
            run['nfc_server'].start(run['withdrawal']['receipt_url'])
            time.sleep(0.5)
        if run['screen_buttons']['wreceipt_goback_btn'] or \
                run['keypad'].last_key_pressed == 'backspace':
            run['screen_buttons']['wreceipt_goback_btn'] = False
            run['nfc_server'].stop()
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['nfc_server'].stop()
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def _clear_payment_runtime(run, ui, cancel_order=False):
    logger.debug('clearing payment runtime')
    ui.showScreen('load_indefinite')

    if cancel_order:
        run['payment']['order'].cancel()

    run['payment']['fiat_amount'] = None
    run['payment']['order'] = None
    run['payment']['receipt_url'] = None
    run['payment']['qr_image_path'] = None

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
        run['withdrawal']['order'].cancel()

    if clear_amount:
        run['withdrawal']['fiat_amount'] = None

    run['withdrawal']['order'] = None
    run['withdrawal']['address'] = None
    run['withdrawal']['receipt_url'] = None
    run['withdrawal']['qr_image_path'] = None

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
