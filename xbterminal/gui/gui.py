# -*- coding: utf-8 -*-
import logging
import os
import re
import subprocess
import sys
import time
import functools

from PyQt4 import QtGui, QtCore

logger = logging.getLogger(__name__)

import xbterminal
import xbterminal.helpers
from xbterminal.gui import ui as appui
from xbterminal.gui import resources  # flake8: noqa
from xbterminal import defaults

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Application(QtGui.QApplication):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self._translators = {}
        self.language = defaults.UI_DEFAULT_LANGUAGE
        self.loadTranslations()

    def loadFonts(self):
        """
        Load additional fonts
        """
        fonts_dir = QtCore.QDir(':/fonts')
        for font_file_name in fonts_dir.entryList(QtCore.QDir.Files):
            QtGui.QFontDatabase.addApplicationFont(
                fonts_dir.filePath(font_file_name))

    def loadStyles(self):
        """
        Load additional styles
        """
        css_dir = QtCore.QDir(':/styles')
        for css_file_name in css_dir.entryList(QtCore.QDir.Files):
            css_file = QtCore.QFile(css_dir.filePath(css_file_name))
            css_file.open(QtCore.QIODevice.ReadOnly)
            css = QtCore.QVariant(css_file.readAll()).toString()
            self.setStyleSheet(css)
            css_file.close()

    def loadTranslations(self):
        """
        Load translations from files
        """
        ts_dir = defaults.UI_TRANSLATIONS_PATH
        for file_name in os.listdir(ts_dir):
            match = re.match("xbterminal_(?P<code>\w+).qm", file_name)
            if match:
                language = match.group('code')
                translator = QtCore.QTranslator()
                translator.load(file_name, directory=ts_dir)
                self._translators[language] = translator

    def setLanguage(self, language_code):
        """
        Set language for application
        Returns:
            True - language changed, False otherwise
        """
        if self.language == language_code:
            return False
        if self.language != defaults.UI_DEFAULT_LANGUAGE:
            self.removeTranslator(self._translators[self.language])
        if language_code != defaults.UI_DEFAULT_LANGUAGE:
            self.installTranslator(self._translators[language_code])
        self.language = language_code
        return True


class GUI(QtGui.QMainWindow):

    def __init__(self, application):
        super(GUI, self).__init__()
        self._application = application
        # Initialize UI
        self.ui = appui.Ui_MainWindow()
        self.ui.setupUi(self)
        # Set up images
        self.ui.main_stackedWidget.setStyleSheet(
            'background-image: url(:/images/bg.png);')
        self.ui.bc_logo_image.setPixmap(QtGui.QPixmap(':/images/bc_logo.png'))
        # Loader
        self.loader = QtGui.QMovie(':/images/loading.gif')
        self.ui.loader_lbl.setMovie(self.loader)
        self.loader.start()
        # Disable keyboard on amount input widget
        self.ui.amount_input.keyPressEvent = lambda event: event.ignore()
        # Set up buttons
        self.ui.pay_btn.clicked.connect(
            functools.partial(self.buttonPressEvent, 'pay'))
        self.ui.withdraw_btn.clicked.connect(
            functools.partial(self.buttonPressEvent, 'withdraw'))
        self.ui.skip_wifi_btn.clicked.connect(
            functools.partial(self.buttonPressEvent, 'skip_wifi'))
        self.ui.wconfirm_confirm_btn.clicked.connect(
            functools.partial(self.buttonPressEvent, 'confirm_withdrawal'))
        # Hide notices
        self.ui.wrong_passwd_lbl.hide()
        self.ui.error_text_lbl.hide()
        self.ui.connecting_lbl.hide()
        self._saved_screen = self.currentScreen()
        self.show()

    def processEvents(self):
        try:
            self._application.sendPostedEvents()
            self._application.processEvents()
        except NameError as error:
            logger.exception(error)

    def keyPressEvent(self, event):
        xbterminal.runtime['keyboard_events'].append(event.key())

    def buttonPressEvent(self, button_name):
        logger.debug('button "{0}" pressed'.format(button_name))
        xbterminal.runtime['last_activity_timestamp'] = time.time()
        xbterminal.runtime['screen_buttons'][button_name] = True

    def toggleWifiConnectingState(self, show):
        if show:
            self.ui.connecting_lbl.show()
            self.ui.password_input.setEnabled(False)
            self.ui.password_input.setStyleSheet('background: #BBBBBB')
        else:
            self.ui.connecting_lbl.hide()
            self.ui.password_input.setEnabled(True)
            self.ui.password_input.setStyleSheet('background: #FFFFFF')

    def toggleWifiWrongPasswordState(self, show):
        if show:
            self.ui.wrong_passwd_lbl.show()
            self.ui.password_input.setStyleSheet('background: #B33A3A')
        else:
            self.ui.wrong_passwd_lbl.hide()
            self.ui.password_input.setStyleSheet('background: #FFFFFF')

    def wifiListAddItem(self, ssid):
        self.ui.wifi_listWidget.addItem(ssid)

    def wifiListSelectItem(self, index):
        self.ui.wifi_listWidget.setCurrentRow(index)

    def wifiListSaveSelectedItem(self):
        ssid = self.ui.wifi_listWidget.currentItem().text()
        xbterminal.runtime['wifi']['selected_ssid'] = str(ssid)

    def wifiListClear(self):
        self.ui.wifi_listWidget.clear()

    def toggleAmountErrorState(self, show):
        if show:
            self.ui.error_text_lbl.show()
        else:
            self.ui.error_text_lbl.hide()

    def currentScreen(self):
        screen_index = self.ui.main_stackedWidget.currentIndex()
        for screen_name, i in defaults.SCREENS.items():
            if i == screen_index:
                return screen_name

    def showScreen(self, screen_name):
        screen_index = defaults.SCREENS[screen_name]
        self.ui.main_stackedWidget.setCurrentIndex(screen_index)

    def setText(self, widget_name, text):
        widget = getattr(self.ui, widget_name)
        widget.setText(text)

    def setImage(self, widget_name, image_path):
        widget = getattr(self.ui, widget_name)
        widget.setPixmap(QtGui.QPixmap(image_path))

    def setStyle(self, widget_name, css):
        widget = getattr(self.ui, widget_name)
        widget.setStyleSheet(css)

    @QtCore.pyqtSlot(str, tuple)
    def stageWorkerSlot(self, method_name, args):
        getattr(self, str(method_name))(*args)

    def retranslateUi(self, language_code, currency_prefix):
        """
        Change UI localization
        """
        if self._application.setLanguage(language_code):
            self.ui.retranslateUi(self)
            xbterminal.runtime['local_config']['language'] = language_code
            xbterminal.helpers.configs.save_local_config(xbterminal.runtime['local_config'])
        self.ui.currency_lbl.setText(currency_prefix)
        self.ui.pwait_currency_lbl.setText(currency_prefix)

    def showErrors(self, errors):
        translations = {
            'no internet': _translate(
                'MainWindow', 'no internet', None),
            'internet disconnected': _translate(
                'MainWindow', 'internet disconnected', None),
        }
        if self.currentScreen() != 'errors':
            # Show error screen
            self._saved_screen = self.currentScreen()
            self.showScreen('errors')
        self.ui.errors_lbl.setText(
            '\n'.join(unicode(translations[error]) for error in errors))

    def hideErrors(self):
        if self.currentScreen() == 'errors':
            # Restore previous screen
            self.showScreen(self._saved_screen)


def initGUI():
    """
    Initialize GUI
    """
    application = Application(sys.argv)

    application.loadFonts()

    if xbterminal.runtime['local_config'].get('show_cursor'):
        application.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
    else:
        application.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    language_code = xbterminal.runtime['local_config'].get(
        'language',
        defaults.UI_DEFAULT_LANGUAGE)
    application.setLanguage(language_code)

    application.loadStyles()

    main_window = GUI(application)
    return main_window


def formatCharSelectHelperHMTL(char_tupl, char_selected=None):
    char_list = []
    selected_char_html = '<span style="color: #333333; font-size: x-large; font-weight: bold;">{char}</span>'
    for index, char in enumerate(char_tupl):
        if char_selected == char:
            char_list.append(selected_char_html.format(char=char))
        else:
            char_list.append(str(char))
    result_html = "<html><head/><body><p>{chars}</p></body></html>"
    return result_html.format(chars=' '.join(char_list))


def wake_up_screen():
    """
    Deactivate screen saver if it is active
    """
    display = subprocess.check_output("echo $DISPLAY", shell=True)
    display = display.strip('\n')
    if display:
        logger.debug("waking up screen")
        subprocess.call(["xset", "-display", display, "-dpms"])
        subprocess.call(["xset", "-display", display, "+dpms"])
    else:
        logger.error("unable to get X server display name")
