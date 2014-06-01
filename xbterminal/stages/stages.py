from decimal import Decimal
import logging
import os.path
import time
import unicodedata

logger = logging.getLogger(__name__)

import xbterminal
from xbterminal import defaults
from xbterminal.stages import payment

import xbterminal.bitcoinaverage
import xbterminal.blockchain.blockchain
import xbterminal.helpers.configs
import xbterminal.helpers.nfcpy
import xbterminal.helpers.qr
import xbterminal.helpers.wireless
import xbterminal.gui.gui


def bootup(run):
    if not run['stage_init']:
        run['main_window'].showScreen('load_indefinite')
        run['stage_init'] = True
        return defaults.STAGES['bootup']

    if not run['init']['internet']:
        if xbterminal.helpers.wireless.is_wifi_available():
            try:
                if ('wifi_ssid' in xbterminal.local_state
                    and xbterminal.local_state['wifi_ssid'] != ''
                    and 'wifi_pass' in xbterminal.local_state
                    and xbterminal.local_state['wifi_pass'] != ''):
                    logger.debug('trying to connect to cached wifi,  '
                        'ssid "{wifi_ssid}" '
                        'password "{wifi_pass}" '.format(wifi_ssid=xbterminal.local_state['wifi_ssid'],
                                                         wifi_pass=xbterminal.local_state['wifi_pass']))
                    if isinstance(xbterminal.local_state['wifi_pass'], unicode):
                        xbterminal.local_state['wifi_pass'] = unicodedata.normalize('NFKD', xbterminal.local_state['wifi_pass']).encode('ascii','ignore')
                    run['wifi']['connected'] = xbterminal.helpers.wireless.connect(xbterminal.local_state['wifi_ssid'],
                                                                                   xbterminal.local_state['wifi_pass'])
                    if run['wifi']['connected']:
                        run['init']['internet'] = True
                        logger.debug('cached wifi connected')
                    else:
                        del xbterminal.local_state['wifi_ssid']
                        del xbterminal.local_state['wifi_pass']
                        xbterminal.helpers.configs.save_local_state()
                        logger.debug('cached wifi connection failed, wifi setup needed')
            except KeyError as error:
                logger.exception(error)

            if not run['wifi']['connected']:
                run['wifi']['networks_last_listed_timestamp'] = 0
                run['wifi']['networks_list_selected_index'] = 0
                run['wifi']['networks_list_length'] = 0
                run['stage_init'] = False
                if 'wifi_ssid' in xbterminal.local_state:
                    return defaults.STAGES['wifi']['enter_passkey']
                else:
                    return defaults.STAGES['wifi']['choose_ssid']
        else:
            logger.warning('no wifi found, hoping for preconfigured wired connection')
            run['init']['internet'] = True
        run['main_window'].advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['wifi_init'])
        return defaults.STAGES['bootup']

    else:
        if (not run['init']['remote_config']
            or (run['init']['remote_config_last_update'] is not None
                and run['init']['remote_config_last_update']+defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time())):
            try:
                xbterminal.helpers.configs.load_remote_config()
                run['main_window'].setText('merchant_name_lbl', "{} \n{} ".format(xbterminal.remote_config['MERCHANT_NAME'],
                                                               xbterminal.remote_config['MERCHANT_DEVICE_NAME'])) #trailing space required
                run['init']['remote_config'] = True
                run['init']['remote_config_last_update'] = int(time.time())
            except ConfigLoadError as error:
                logger.error('remote config load failed, exiting')
                raise error
            return defaults.STAGES['bootup']

        if not run['init']['blockchain']:
            xbterminal.blockchain.blockchain.init()
            run['init']['blockchain'] = True
            run['main_window'].advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['blockchain_init'])
            run['main_window'].advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['finish'])
            return defaults.STAGES['bootup']

    if run['init']['internet'] and run['init']['remote_config'] and run['init']['blockchain']:
        run['stage_init'] = False
        return defaults.STAGES['idle']


def idle(run):
    if not run['stage_init']:
        run['main_window'].showScreen('idle')
        run['stage_init'] = True
        return defaults.STAGES['idle']

    if run['keypad'].last_key_pressed is not None:
        run['stage_init'] = False
        return defaults.STAGES['payment']['enter_amount']


def enter_amount(run):
    if not run['stage_init']:
        run['main_window'].showScreen('enter_amount')
        run['main_window'].setText('amount_input', payment.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES))
        run['stage_init'] = True
        return defaults.STAGES['payment']['enter_amount']

    if (isinstance(run['keypad'].last_key_pressed, (int, long)) or run['keypad'].last_key_pressed == 'backspace'):
        if run['keypad'].last_key_pressed == 'backspace' and run['display_value_unformatted'] == '':
            run['stage_init'] = False
            return defaults.STAGES['idle']

        run['main_window'].setStyle('amount_input', 'background: #FFF')
        run['main_window'].setText('error_text_lbl', '')
        run['display_value_unformatted'] = payment.processKeyInput(run['display_value_unformatted'], run['keypad'].last_key_pressed)

        run['display_value_formatted'] = payment.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)

        run['main_window'].setText('amount_input', run['display_value_formatted'])
    elif run['keypad'].last_key_pressed == 'enter':
        run['amounts']['amount_to_pay_fiat'] = payment.inputToDecimal(run['display_value_unformatted'])
        if run['amounts']['amount_to_pay_fiat'] > 0:
            run['stage_init'] = False
            return defaults.STAGES['payment']['pay_loading']
        else:
            run['main_window'].setStyle('amount_input', 'background: #B33A3A')
            run['main_window'].setText('error_text_lbl', "no amount entered ") #trailing space here is needed, otherwise last letter if halfcut


def pay_loading(run):
    if not run['stage_init']:
        run['main_window'].showScreen('load_indefinite')
        run['main_window'].setText('indefinite_load_lbl', 'preparing payment')
        run['stage_init'] = True
        return defaults.STAGES['payment']['pay_loading']

    if run['amounts']['amount_to_pay_fiat'] is None:
        run['stage_init'] = False
        return defaults.STAGES['payment']['enter_amount']

    if run['amounts']['amount_to_pay_btc'] is None:
        run['received_payment'] = False
        run['invoice_paid'] = False

        run['transactions_addresses'] = {}
        run['transactions_addresses']['local'] = xbterminal.blockchain.blockchain.getFreshAddress()
        run['transactions_addresses']['merchant'] = xbterminal.remote_config['MERCHANT_BITCOIN_ADDRESS']
        run['transactions_addresses']['fee'] = xbterminal.remote_config['OUR_FEE_BITCOIN_ADDRESS']

        if (xbterminal.remote_config['MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE'] is not None
            and xbterminal.remote_config['MERCHANT_INSTANTFIAT_SHARE'] > 0):
            (run['amounts']['instantfiat_fiat_amount'],
             run['amounts']['instantfiat_btc_amount'],
             run['instantfiat_invoice_id'],
             run['transactions_addresses']['instantfiat'],
             run['exchange_rate']) = payment.createInvoice(run['amounts']['amount_to_pay_fiat'])
        else:
            run['amounts']['instantfiat_fiat_amount'] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
            run['amounts']['instantfiat_btc_amount'] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
            run['instantfiat_invoice_id'] = None
            run['transactions_addresses']['instantfiat'] = None
            run['exchange_rate'] = xbterminal.bitcoinaverage.getExchangeRate(xbterminal.remote_config['MERCHANT_CURRENCY'])

        run['amounts']['our_fee_btc_amount'] = payment.getOurFeeBtcAmount(run['amounts']['amount_to_pay_fiat'], run['exchange_rate'])
        run['amounts']['merchants_btc_amount'] = payment.getMerchantBtcAmount(run['amounts']['amount_to_pay_fiat'], run['exchange_rate'])

        run['amounts']['amount_to_pay_btc'] = (run['amounts']['our_fee_btc_amount']
                                    + run['amounts']['instantfiat_btc_amount']
                                    + run['amounts']['merchants_btc_amount']
                                    + defaults.BTC_DEFAULT_FEE) #tx fee to be paid for forwarding transaction from device to merchant and/or instantfiat
        run['effective_rate_btc'] = run['amounts']['amount_to_pay_fiat'] / run['amounts']['amount_to_pay_btc']

        run['payment_requested_timestamp'] = time.time()
        run['transaction_bitcoin_uri'] = payment.getBitcoinURI(run['transactions_addresses']['local'],
                                                              run['amounts']['amount_to_pay_btc'])

        run['stage_init'] = False
        return defaults.STAGES['payment']['pay_rates']


def pay_rates(run):
    if not run['stage_init']:
        run['main_window'].showScreen('pay_rates')
        run['main_window'].setText('fiat_amount', payment.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
        run['main_window'].setText('btc_amount', payment.formatBitcoin(run['amounts']['amount_to_pay_btc']))
        run['main_window'].setText('exchange_rate_amount', payment.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                             defaults.EXCHANGE_RATE_DEC_PLACES))
        run['stage_init'] = True

    if run['keypad'].last_key_pressed == 'enter':
        run['stage_init'] = False
        return defaults.STAGES['payment']['pay']
    if run['keypad'].last_key_pressed == 'backspace':
        payment.clearPaymentRuntime(False)
        run['stage_init'] = False
        return defaults.STAGES['payment']['enter_amount']
