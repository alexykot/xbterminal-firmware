from decimal import Decimal
import logging
import time

from xbterminal.gui import settings
from xbterminal.gui.gui import PAYMENT_STATUSES
from xbterminal.gui.utils import amounts, qr
from xbterminal.gui.exceptions import (
    NetworkError,
    ServerError,
    StageTimeout)

logger = logging.getLogger(__name__)


def bootup(state, ui):
    ui.showScreen('load_indefinite')

    ui.retranslateUi(
        state['remote_config']['language']['code'],
        state['remote_config']['currency']['prefix'])

    if state['remote_config']['status'] in ['active', 'suspended']:
        return settings.STAGES['idle']
    else:
        return settings.STAGES['activate']


def activate(state, ui):
    ui.showScreen('activation')
    ui.setText('activation_server_lbl',
               state['remote_config']['remote_server'].split('//')[1])
    activation_code = state['client'].get_activation_code()
    ui.setText('activation_code_lbl', activation_code)
    while True:
        if state['remote_config']['status'] == 'active':
            return settings.STAGES['idle']
        time.sleep(settings.STAGE_LOOP_PERIOD)


def idle(state, ui):
    ui.showScreen('idle')
    state['client'].start_nfc_server(message=settings.HELP_PAGE_URL)
    standby_screen_last_refresh = 0
    while True:
        if state['remote_config']['status'] == 'suspended':
            if not state['is_suspended']:
                state['client'].disable_display()
                state['is_suspended'] = True
                logger.warning('device suspended')
            # Freeze GUI if device is suspended
            time.sleep(settings.STAGE_LOOP_PERIOD)
            continue
        elif state['remote_config']['status'] == 'active':
            if state['is_suspended']:
                state['client'].enable_display()
                state['is_suspended'] = False
                logger.warning('device reenabled')

        if state['screen_buttons']['idle_begin_btn'] or \
                state['screen_buttons']['standby_wake_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['idle_begin_btn'] = False
            state['screen_buttons']['standby_wake_btn'] = False
            state['client'].stop_nfc_server()
            return settings.STAGES['payment']['pay_amount']
        elif state['screen_buttons']['idle_help_btn']:
            state['screen_buttons']['idle_help_btn'] = False
            state['client'].stop_nfc_server()
            return settings.STAGES['help']

        # Communicate with the host system
        payout = state['client'].host_get_payout()
        if state['keypad'].last_key_pressed == 'alt':
            payout = Decimal(state['gui_config'].get(
                'default_withdrawal_amount', '0.1'))
        if payout:
            state['withdrawal']['fiat_amount'] = payout
            state['client'].stop_nfc_server()
            return settings.STAGES['withdrawal']['withdraw_wait']

        # Show standby screen when idle for a long time
        current_time = time.time()
        if state['last_activity_timestamp'] + settings.STANDBY_SCREEN_TIMEOUT < current_time and \
                standby_screen_last_refresh + settings.STANDBY_SCREEN_REFRESH_CYCLE < current_time:
            standby_screen_last_refresh = current_time
            ui.showStandByScreen()
        time.sleep(settings.STAGE_LOOP_PERIOD)


def help(state, ui):
    ui.showScreen('help')
    ui.setText('help_url_lbl', settings.HELP_PAGE_URL)
    ui.setImage('help_qr_img', qr.qr_gen(settings.HELP_PAGE_URL))
    state['client'].start_nfc_server(message=settings.HELP_PAGE_URL)
    while True:
        if state['screen_buttons']['help_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['help_goback_btn'] = False
            state['client'].stop_nfc_server()
            return settings.STAGES['idle']
        try:
            _wait_for_screen_timeout(state, ui, 'help')
        except StageTimeout:
            return settings.STAGES['idle']
        time.sleep(settings.STAGE_LOOP_PERIOD)


def pay_amount(state, ui):
    ui.showScreen('pay_amount')
    options = {
        'pamount_opt1_btn': Decimal(
            state['remote_config']['settings']['amount_1']),
        'pamount_opt2_btn': Decimal(
            state['remote_config']['settings']['amount_2']),
        'pamount_opt3_btn': Decimal(
            state['remote_config']['settings']['amount_3']),
    }
    for button, amount in options.items():
        ui.setText(button, amounts.format_fiat_amount_pretty(amount, prefix=True))
    while True:
        if state['screen_buttons']['pamount_opt1_btn'] or \
                state['keypad'].last_key_pressed == 1:
            state['screen_buttons']['pamount_opt1_btn'] = False
            state['payment']['fiat_amount'] = options['pamount_opt1_btn']
            return settings.STAGES['payment']['pay_loading']
        elif state['screen_buttons']['pamount_opt2_btn'] or \
                state['keypad'].last_key_pressed == 2:
            state['screen_buttons']['pamount_opt2_btn'] = False
            state['payment']['fiat_amount'] = options['pamount_opt2_btn']
            return settings.STAGES['payment']['pay_loading']
        elif state['screen_buttons']['pamount_opt3_btn'] or \
                state['keypad'].last_key_pressed == 3:
            state['screen_buttons']['pamount_opt3_btn'] = False
            state['payment']['fiat_amount'] = options['pamount_opt3_btn']
            return settings.STAGES['payment']['pay_loading']
        elif state['keypad'].last_key_pressed == 'backspace':
            _clear_payment_runtime(state, ui)
            return settings.STAGES['idle']

        payout = state['client'].host_get_payout()
        if payout:
            _clear_payment_runtime(state, ui)
            state['withdrawal']['fiat_amount'] = payout
            return settings.STAGES['withdrawal']['withdraw_wait']

        try:
            _wait_for_screen_timeout(state, ui, 'pay_amount')
        except StageTimeout:
            _clear_payment_runtime(state, ui)
            return settings.STAGES['idle']

        time.sleep(settings.STAGE_LOOP_PERIOD)


# TODO: remove stage
def pay_confirm(state, ui):
    ui.showScreen('pay_confirm')
    assert state['payment']['fiat_amount'] >= 0
    amount_shift = Decimal(state['remote_config']['settings']['amount_shift'])
    ui.setText('pconfirm_decr_btn',
               '-{}'.format(amounts.format_fiat_amount_pretty(amount_shift)))
    ui.setText('pconfirm_incr_btn',
               '+{}'.format(amounts.format_fiat_amount_pretty(amount_shift)))
    ui.setText('pconfirm_amount_lbl',
               amounts.format_fiat_amount_pretty(state['payment']['fiat_amount'], prefix=True))
    while True:
        if state['screen_buttons']['pconfirm_decr_btn'] or \
                state['keypad'].last_key_pressed == 1:
            state['screen_buttons']['pconfirm_decr_btn'] = False
            state['keypad'].reset_key()
            state['payment']['fiat_amount'] -= Decimal(amount_shift)
            if state['payment']['fiat_amount'] < 0:
                state['payment']['fiat_amount'] = Decimal('0.00')
            ui.setText(
                'pconfirm_amount_lbl',
                amounts.format_fiat_amount_pretty(state['payment']['fiat_amount'], prefix=True))
        if state['screen_buttons']['pconfirm_incr_btn'] or \
                state['keypad'].last_key_pressed == 2:
            state['screen_buttons']['pconfirm_incr_btn'] = False
            state['keypad'].reset_key()
            state['payment']['fiat_amount'] += Decimal(amount_shift)
            ui.setText(
                'pconfirm_amount_lbl',
                amounts.format_fiat_amount_pretty(state['payment']['fiat_amount'], prefix=True))
        if state['screen_buttons']['pconfirm_confirm_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['pconfirm_confirm_btn'] = False
            if state['payment']['fiat_amount'] > 0:
                return settings.STAGES['payment']['pay_loading']
        if state['screen_buttons']['pconfirm_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['pconfirm_goback_btn'] = False
            _clear_payment_runtime(state, ui)
            return settings.STAGES['payment']['pay_amount']

        try:
            _wait_for_screen_timeout(state, ui, 'pay_confirm')
        except StageTimeout:
            _clear_payment_runtime(state, ui)
            return settings.STAGES['idle']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def pay_loading(state, ui):
    ui.showScreen('pay_loading')

    if state['payment']['fiat_amount'] is None:
        return settings.STAGES['payment']['pay_amount']

    while True:
        try:
            payment_info = state['client'].create_payment_order(
                fiat_amount=state['payment']['fiat_amount'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            ui.showErrorScreen('SERVER_ERROR')
            time.sleep(300)
            _clear_payment_runtime(state, ui)
            return settings.STAGES['idle']
        else:
            # Payment parameters loaded
            state['payment'].update(payment_info)
            # Prepare QR image
            state['payment']['qrcode'] = qr.qr_gen(state['payment']['payment_uri'])
            return settings.STAGES['payment']['pay_info']


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
            return settings.STAGES['payment']['pay_wait']
        if state['screen_buttons']['pinfo_cancel_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['pinfo_cancel_btn'] = False
            _clear_payment_runtime(state, ui, cancel_order=True)
            return settings.STAGES['payment']['pay_amount']

        payout = state['client'].host_get_payout()
        if payout:
            _clear_payment_runtime(state, ui, cancel_order=True)
            state['withdrawal']['fiat_amount'] = payout
            return settings.STAGES['withdrawal']['withdraw_wait']

        try:
            _wait_for_screen_timeout(state, ui, 'pay_info')
        except StageTimeout:
            _clear_payment_runtime(state, ui, cancel_order=True)
            return settings.STAGES['idle']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def pay_wait(state, ui):
    ui.showScreen('pay_wait')
    ui.setText('pwait_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['payment']['btc_amount'], prefix=True))
    ui.setImage('pwait_qr_img', state['payment']['qrcode'])
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
                state['screen_buttons']['pwait_cancel_refund_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['pwait_cancel_btn'] = False
            state['screen_buttons']['pwait_cancel_refund_btn'] = False
            _clear_payment_runtime(state, ui, cancel_order=True)
            state['client'].stop_nfc_server()
            state['client'].stop_bluetooth_server()
            return settings.STAGES['payment']['pay_amount']

        payment_status = state['client'].get_payment_status(
            uid=state['payment']['uid'])
        if payment_status['status'] == 'underpaid':
            ui.setText(
                'pwait_paid_btc_amount_lbl',
                amounts.format_btc_amount_pretty(
                    payment_status['paid_btc_amount'], prefix=True))
            ui.showWidget('pwait_paid_lbl')
            ui.showWidget('pwait_paid_btc_amount_lbl')
            ui.showWidget('pwait_cancel_refund_btn')
            ui.hideWidget('pwait_cancel_btn')
        elif payment_status['status'] == 'received':
            state['client'].stop_nfc_server()
            state['client'].stop_bluetooth_server()
            return settings.STAGES['payment']['pay_progress']

        try:
            _wait_for_screen_timeout(state, ui, 'pay_wait', timeout=450)
        except StageTimeout:
            _clear_payment_runtime(state, ui, cancel_order=True)
            state['client'].stop_nfc_server()
            state['client'].stop_bluetooth_server()
            return settings.STAGES['payment']['pay_cancel']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def pay_progress(state, ui):
    ui.showScreen('pay_progress')
    ui.setText('pprogress_status_lbl', PAYMENT_STATUSES.RECEIVED)
    ui.setText('pprogress_amount_val_lbl',
               amounts.format_btc_amount_pretty(state['payment']['btc_amount'], prefix=True))
    time.sleep(2)
    ui.setText('pprogress_status_lbl', PAYMENT_STATUSES.WAITING)
    while True:
        payment_status = state['client'].get_payment_status(
            uid=state['payment']['uid'])
        if payment_status['status'] in ['notified', 'confirmed']:
            state['payment']['receipt_url'] = state['client'].get_payment_receipt(
                uid=state['payment']['uid'])
            logger.debug('payment received, receipt: {}'.format(state['payment']['receipt_url']))
            state['payment']['qrcode'] = qr.qr_gen(state['payment']['receipt_url'])
            state['client'].host_add_credit(fiat_amount=state['payment']['fiat_amount'])
            ui.setText('pprogress_status_lbl', PAYMENT_STATUSES.DONE)
            state['client'].beep()
            time.sleep(3)
            return settings.STAGES['payment']['pay_receipt']

        try:
            _wait_for_screen_timeout(state, ui, 'pay_progress', timeout=900)
        except StageTimeout:
            _clear_payment_runtime(state, ui, cancel_order=True)
            state['client'].stop_nfc_server()
            state['client'].stop_bluetooth_server()
            return settings.STAGES['payment']['pay_cancel']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def pay_receipt(state, ui):
    assert state['payment']['receipt_url']
    ui.showScreen('pay_receipt')
    ui.setText('preceipt_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['payment']['btc_amount']))
    ui.setImage('preceipt_receipt_qr_img', state['payment']['qrcode'])
    state['client'].start_nfc_server(message=state['payment']['receipt_url'])
    while True:
        if state['screen_buttons']['preceipt_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['preceipt_goback_btn'] = False
            state['client'].stop_nfc_server()
            _clear_payment_runtime(state, ui)
            return settings.STAGES['idle']

        payout = state['client'].host_get_payout()
        if payout:
            state['client'].stop_nfc_server()
            _clear_payment_runtime(state, ui)
            state['withdrawal']['fiat_amount'] = payout
            return settings.STAGES['withdrawal']['withdraw_wait']

        try:
            _wait_for_screen_timeout(state, ui, 'pay_receipt')
        except StageTimeout:
            state['client'].stop_nfc_server()
            _clear_payment_runtime(state, ui)
            return settings.STAGES['idle']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def pay_cancel(state, ui):
    ui.showScreen('pay_cancel')
    while True:
        if state['screen_buttons']['pcancel_goback_btn'] or \
                state['keypad'].last_key_pressed is not None:
            state['screen_buttons']['pcancel_goback_btn'] = False
            _clear_payment_runtime(state, ui)
            return settings.STAGES['payment']['pay_amount']

        payout = state['client'].host_get_payout()
        if payout:
            _clear_payment_runtime(state, ui)
            state['withdrawal']['fiat_amount'] = payout
            return settings.STAGES['withdrawal']['withdraw_wait']

        if state['last_activity_timestamp'] + settings.SCREEN_TIMEOUT < time.time():
            return settings.STAGES['idle']
        time.sleep(settings.STAGE_LOOP_PERIOD)


def withdraw_select(state, ui):
    assert state['withdrawal']['fiat_amount'] > 0
    ui.showScreen('withdraw_select')
    ui.setText(
        'wselect_fiat_amount_lbl',
        amounts.format_fiat_amount_pretty(
            state['withdrawal']['fiat_amount'], prefix=True))

    while True:
        if state['screen_buttons']['wselect_fiat_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['wselect_fiat_btn'] = False
            state['client'].host_pay_cash(
                fiat_amount=state['withdrawal']['fiat_amount'])
            _clear_withdrawal_runtime(state, ui)
            return settings.STAGES['idle']
        if state['screen_buttons']['wselect_bitcoin_btn'] or \
                state['keypad'].last_key_pressed == 'alt':
            state['screen_buttons']['wselect_bitcoin_btn'] = False
            return settings.STAGES['withdrawal']['withdraw_wait']
        if state['keypad'].last_key_pressed == 'backspace':
            _clear_withdrawal_runtime(state, ui)
            return settings.STAGES['idle']
        time.sleep(settings.STAGE_LOOP_PERIOD)


def withdraw_wait(state, ui):
    ui.showScreen('withdraw_wait')
    ui.setText(
        'wwait_fiat_amount_lbl',
        amounts.format_fiat_amount_pretty(state['withdrawal']['fiat_amount'], prefix=True))
    while True:
        if state['keypad'].last_key_pressed == 'backspace':
            _clear_withdrawal_runtime(state, ui)
            return settings.STAGES['idle']
        elif state['screen_buttons']['wwait_scan_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['wwait_scan_btn'] = False
            return settings.STAGES['withdrawal']['withdraw_scan']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def withdraw_scan(state, ui):
    ui.showScreen('withdraw_scan')
    state['client'].start_qr_scanner()
    while True:
        default_address = state['gui_config'].get('default_withdrawal_address')
        address = state['client'].get_scanned_address() or default_address
        if address:
            logger.debug('address scanned: {0}'.format(address))
            state['client'].stop_qr_scanner()
            state['withdrawal']['address'] = address
            return settings.STAGES['withdrawal']['withdraw_loading1']

        try:
            _wait_for_screen_timeout(state, ui, 'withdraw_scan', timeout=30)
        except StageTimeout:
            state['client'].stop_qr_scanner()
            return settings.STAGES['withdrawal']['withdraw_wait']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def withdraw_loading1(state, ui):
    assert state['withdrawal']['fiat_amount'] > 0
    ui.showScreen('withdraw_loading')
    ui.setText(
        'wload_amount_val_lbl',
        amounts.format_fiat_amount_pretty(
            state['withdrawal']['fiat_amount'], prefix=True))
    while True:
        try:
            withdrawal_info = state['client'].create_withdrawal_order(
                fiat_amount=state['withdrawal']['fiat_amount'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError as error:
            if error.contains('Amount exceeds max payout for current device.'):
                ui.showErrorScreen('MAX_PAYOUT_ERROR')
            else:
                ui.showErrorScreen('SERVER_ERROR')
            time.sleep(300)
            _clear_withdrawal_runtime(state, ui, clear_amount=False)
            return settings.STAGES['withdrawal']['withdraw_wait']
        else:
            state['withdrawal'].update(withdrawal_info)
            return settings.STAGES['withdrawal']['withdraw_confirm']


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
    ui.setText(
        'wconfirm_fee_amount_lbl',
        amounts.format_btc_amount_pretty(
            state['withdrawal']['tx_fee_btc_amount']))
    while True:
        if state['screen_buttons']['wconfirm_confirm_btn'] or \
                state['keypad'].last_key_pressed == 'enter':
            state['screen_buttons']['wconfirm_confirm_btn'] = False
            return settings.STAGES['withdrawal']['withdraw_loading2']
        elif state['screen_buttons']['wconfirm_cancel_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['wconfirm_cancel_btn'] = False
            _clear_withdrawal_runtime(state, ui, clear_amount=False,
                                      cancel_order=True)
            return settings.STAGES['withdrawal']['withdraw_wait']

        try:
            _wait_for_screen_timeout(state, ui, 'withdraw_confirm', timeout=300)
        except StageTimeout:
            _clear_withdrawal_runtime(state, ui, clear_amount=False,
                                      cancel_order=True)
            return settings.STAGES['withdrawal']['withdraw_wait']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def withdraw_loading2(state, ui):
    assert state['withdrawal']['address'] is not None
    ui.showScreen('withdraw_loading')
    ui.setText(
        'wload_amount_val_lbl',
        amounts.format_btc_amount_pretty(
            state['withdrawal']['btc_amount'], prefix=True))
    while True:
        try:
            withdrawal_info = state['client'].confirm_withdrawal(
                uid=state['withdrawal']['uid'],
                address=state['withdrawal']['address'])
        except NetworkError:
            logger.warning('network error, retry in 5 seconds')
            time.sleep(5)
            continue
        except ServerError:
            ui.showErrorScreen('SERVER_ERROR')
            time.sleep(300)
            return settings.STAGES['withdrawal']['withdraw_confirm']
        state['withdrawal'].update(withdrawal_info)
        logger.info('withdrawal {} confirmed'.format(
            state['withdrawal']['uid']))
        break
    while True:
        withdrawal_status = state['client'].get_withdrawal_status(
            uid=state['withdrawal']['uid'])
        if withdrawal_status == 'completed':
            state['withdrawal']['receipt_url'] = state['client'].get_withdrawal_receipt(
                uid=state['withdrawal']['uid'])
            logger.debug('withdrawal finished, receipt: {}'.format(
                state['withdrawal']['receipt_url']))
            state['withdrawal']['qrcode'] = qr.qr_gen(state['withdrawal']['receipt_url'])
            return settings.STAGES['withdrawal']['withdraw_receipt']

        try:
            _wait_for_screen_timeout(state, ui, 'withdraw_loading', timeout=300)
        except StageTimeout:
            _clear_withdrawal_runtime(state, ui)
            return settings.STAGES['idle']

        time.sleep(settings.STAGE_LOOP_PERIOD)


def withdraw_receipt(state, ui):
    ui.showScreen('withdraw_receipt')
    assert state['withdrawal']['receipt_url']
    ui.setImage('wreceipt_receipt_qr_img', state['withdrawal']['qrcode'])
    ui.setText('wreceipt_btc_amount_lbl',
               amounts.format_btc_amount_pretty(state['withdrawal']['btc_amount']))
    state['client'].start_nfc_server(message=state['withdrawal']['receipt_url'])
    while True:
        if state['screen_buttons']['wreceipt_goback_btn'] or \
                state['keypad'].last_key_pressed == 'backspace':
            state['screen_buttons']['wreceipt_goback_btn'] = False
            state['client'].stop_nfc_server()
            _clear_withdrawal_runtime(state, ui)
            return settings.STAGES['idle']

        try:
            _wait_for_screen_timeout(state, ui, 'withdraw_receipt')
        except StageTimeout:
            state['client'].stop_nfc_server()
            _clear_withdrawal_runtime(state, ui)
            return settings.STAGES['idle']

        time.sleep(settings.STAGE_LOOP_PERIOD)


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
    state['payment']['qrcode'] = None

    ui.hideWidget('pwait_paid_lbl')
    ui.hideWidget('pwait_paid_btc_amount_lbl')
    ui.hideWidget('pwait_cancel_refund_btn')
    ui.showWidget('pwait_cancel_btn')

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
    state['withdrawal']['qrcode'] = None

    ui.setText('wwait_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(Decimal(0), prefix=True))
    ui.setText('wconfirm_fiat_amount_lbl',
               amounts.format_fiat_amount_pretty(Decimal(0), prefix=True))
    ui.setText('wconfirm_btc_amount_lbl',
               amounts.format_btc_amount_pretty(Decimal(0)))
    ui.setText('wconfirm_xrate_amount_lbl',
               amounts.format_exchange_rate_pretty(Decimal(0)))
    ui.setText('wconfirm_fee_amount_lbl',
               amounts.format_btc_amount_pretty(Decimal(0)))
    ui.setImage('wreceipt_receipt_qr_img', None)


def _wait_for_screen_timeout(state, ui, current_screen,
                             timeout=settings.SCREEN_TIMEOUT):
    if state['last_activity_timestamp'] + \
            timeout - settings.SCREEN_TIMEOUT_CONFIRMATION_TIME < time.time():
        if not state['timeout']:
            state['client'].beep()
            state['timeout'] = True
        if state['last_activity_timestamp'] + timeout < time.time():
            raise StageTimeout
