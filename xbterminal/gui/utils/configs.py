import json
import os
import logging
import pprint

from xbterminal.gui import settings

logger = logging.getLogger(__name__)


def load_gui_config():
    """
    GUI config params:
        debug: boolean (default: False)
        default_withdrawal_address: string (default: None)
        default_withdrawal_amount: string (default: '0.1')
        language: string (default: 'en')
        theme: string (default: 'default')
        show_cursor: boolean (default: False)
    Returns:
        gui_config: dict
    """
    if not os.path.exists(settings.GUI_CONFIG_FILE_PATH):
        gui_config = {}
        save_gui_config(gui_config)
        logger.info('created new GUI config')
    else:
        with open(settings.GUI_CONFIG_FILE_PATH) as gui_config_file:
            gui_config = json.loads(gui_config_file.read())
            logger.info('GUI config loaded:\n{0}'.format(
                pprint.pformat(gui_config)))
    return gui_config


def save_gui_config(gui_config):
    with open(settings.GUI_CONFIG_FILE_PATH, 'w') as gui_config_file:
        gui_config_file.write(json.dumps(
            gui_config, indent=2, sort_keys=True, separators=(',', ': ')))
