import os

VERSION = '0.9.6'

STAGES = {
    'bootup': 'bootup',
    'activate': 'activate',
    'idle': 'idle',
    'payment': {
        'pay_amount': 'pay_amount',
        'pay_confirm': 'pay_confirm',
        'pay_loading': 'pay_loading',
        'pay_info': 'pay_info',
        'pay_wait': 'pay_wait',
        'pay_success': 'pay_success',
        'pay_receipt': 'pay_receipt',
        'pay_cancel': 'pay_cancel',
    },
    'withdrawal': {
        'withdraw_select': 'withdraw_select',
        'withdraw_loading1': 'withdraw_loading1',
        'withdraw_scan': 'withdraw_scan',
        'withdraw_confirm': 'withdraw_confirm',
        'withdraw_loading2': 'withdraw_loading2',
        'withdraw_success': 'withdraw_success',
        'withdraw_receipt': 'withdraw_receipt',
    },
    'application_halt': 'application_halt',
}

SCREENS = {
    'load_indefinite': 0,
    'activation': 1,
    'idle': 2,
    'standby': 3,
    'pay_amount': 4,
    'pay_confirm': 5,
    'pay_info': 6,
    'pay_wait': 7,
    'pay_success': 8,
    'pay_receipt': 9,
    'pay_cancel': 10,
    'withdraw_select': 11,
    'withdraw_scan': 12,
    'withdraw_confirm': 13,
    'withdraw_success': 14,
    'withdraw_receipt': 15,
    'errors': 16,
    'timeout': 17,
}

BUTTONS = [
    'idle_begin_btn',
    'standby_wake_btn',
    'pamount_opt1_btn',
    'pamount_opt2_btn',
    'pamount_opt3_btn',
    'pconfirm_decr_btn',
    'pconfirm_incr_btn',
    'pconfirm_confirm_btn',
    'pconfirm_goback_btn',
    'pinfo_pay_btn',
    'pinfo_cancel_btn',
    'pwait_cancel_btn',
    'psuccess_no_btn',
    'psuccess_yes_btn',
    'preceipt_goback_btn',
    'wselect_fiat_btn',
    'wselect_bitcoin_btn',
    'wscan_goback_btn',
    'wconfirm_confirm_btn',
    'wconfirm_cancel_btn',
    'wsuccess_no_btn',
    'wsuccess_yes_btn',
    'wreceipt_goback_btn',
    'timeout_no_btn',
    'timeout_yes_btn',
]

try:
    from xbterminal.nuitka_fix import BASE_DIR
except ImportError:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

PROJECT_LOCAL_PATH = os.path.join(BASE_DIR, 'xbterminal')

RUNTIME_PATH = os.path.join(PROJECT_LOCAL_PATH, 'runtime')
GUI_CONFIG_FILE_PATH = os.path.join(RUNTIME_PATH, 'gui_config')
QR_IMAGE_PATH = os.path.join(RUNTIME_PATH, 'qr.png')

UI_TRANSLATIONS_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'ts')
UI_DEFAULT_LANGUAGE = 'en'
UI_THEMES_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'themes')
UI_DEFAULT_THEME = 'default'

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(name)s [%(levelname)s] :: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'requests.packages.urllib3.connectionpool': {
            'level': 'WARNING',
        },
        'urllib3.connectionpool': {
            'level': 'WARNING',
        },
        'tornado.access': {
            'level': 'WARNING',
        },
    },
}

MAIN_LOOP_PERIOD = 0.05  # seconds
STAGE_LOOP_PERIOD = 0.1  # seconds
STAGE_CHANGE_DELAY = 0.3  # seconds

REMOTE_CONFIG_UPDATE_CYCLE = 60  # seconds between remote config updates

STANDBY_SCREEN_TIMEOUT = 300
STANDBY_SCREEN_REFRESH_CYCLE = 5  # seconds

SCREEN_TIMEOUT = 60
SCREEN_TIMEOUT_CONFIRMATION_TIME = 15

OUTPUT_DEC_PLACES = 2  # fractional decimal places to show on screen

BITCOIN_SCALE_DIVIZER = 1000  # 1 for BTC, 1000 for mBTC, 1000000 for uBTC
BITCOIN_OUTPUT_DEC_PLACES = 5
