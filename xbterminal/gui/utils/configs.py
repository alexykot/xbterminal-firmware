import json
import os
import logging
import pprint

from xbterminal import defaults

logger = logging.getLogger(__name__)


def load_gui_config():
    """
    GUI config params:
        default_withdrawal_address: string (default: None)
        language: string (default: 'en')
        theme: string (default: 'default')
        show_cursor: boolean (default: False)
    Returns:
        gui_config: dict
    """
    if not os.path.exists(defaults.GUI_CONFIG_FILE_PATH):
        gui_config = {}
        save_gui_config(gui_config)
        logger.info('created new GUI config')
    else:
        with open(defaults.GUI_CONFIG_FILE_PATH) as gui_config_file:
            gui_config = json.loads(gui_config_file.read())
            logger.info('GUI config loaded:\n{0}'.format(
                pprint.pformat(gui_config)))
    return gui_config


def save_gui_config(gui_config):
    with open(defaults.GUI_CONFIG_FILE_PATH, 'w') as gui_config_file:
        gui_config_file.write(json.dumps(
            gui_config, indent=2, sort_keys=True, separators=(',', ': ')))
