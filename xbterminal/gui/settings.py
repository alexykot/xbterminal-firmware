import os

VERSION = '0.16.1'

STAGES = {
    'bootup': 'bootup',
    'activate': 'activate',
    'idle': 'idle',
    'help': 'help',
    'payment': {
        'pay_amount': 'pay_amount',
        'pay_confirm': 'pay_confirm',
        'pay_loading': 'pay_loading',
        'pay_info': 'pay_info',
        'pay_wait': 'pay_wait',
        'pay_progress': 'pay_progress',
        'pay_receipt': 'pay_receipt',
        'pay_cancel': 'pay_cancel',
    },
    'withdrawal': {
        'withdraw_select': 'withdraw_select',
        'withdraw_loading1': 'withdraw_loading1',
        'withdraw_wait': 'withdraw_wait',
        'withdraw_scan': 'withdraw_scan',
        'withdraw_confirm': 'withdraw_confirm',
        'withdraw_loading2': 'withdraw_loading2',
        'withdraw_receipt': 'withdraw_receipt',
    },
    'application_halt': 'application_halt',
}

SCREENS = {
    'load_indefinite': 0,
    'activation': 1,
    'idle': 2,
    'help': 3,
    'standby': 4,
    'pay_amount': 5,
    'pay_confirm': 6,
    'pay_loading': 7,
    'pay_info': 8,
    'pay_wait': 9,
    'pay_progress': 10,
    'pay_receipt': 11,
    'pay_cancel': 12,
    'withdraw_select': 13,
    'withdraw_loading': 14,
    'withdraw_wait': 15,
    'withdraw_scan': 16,
    'withdraw_confirm': 17,
    'withdraw_receipt': 18,
    'error': 19,
    'timeout': 20,
}

BUTTONS = [
    'idle_begin_btn',
    'idle_help_btn',
    'standby_wake_btn',
    'help_goback_btn',
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
    'pwait_cancel_refund_btn',
    'preceipt_goback_btn',
    'pcancel_goback_btn',
    'wselect_fiat_btn',
    'wselect_bitcoin_btn',
    'wwait_goback_btn',
    'wwait_scan_btn',
    'wconfirm_confirm_btn',
    'wconfirm_cancel_btn',
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

HELP_PAGE_URL = 'http://www.apmodule.co.uk/'
