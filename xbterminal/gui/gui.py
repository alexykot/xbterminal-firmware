# -*- coding: utf-8 -*-
import logging
import os
import re
import subprocess
import sys
import time
from collections import deque

from PyQt4 import QtGui, QtCore

logger = logging.getLogger(__name__)

import xbterminal
import xbterminal.helpers
from xbterminal.gui import ui as appui
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

    def loadTranslations(self):
        """
        Load translations from files
        """
        ts_dir = os.path.join(defaults.PROJECT_ABS_PATH,
                              defaults.UI_TRANSLATIONS_PATH)
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


class GUI(QtGui.QWidget):

    def __init__(self, application):
        super(GUI, self).__init__()
        self._application = application
        self.keys = deque(maxlen=5)
        # Initialize UI
        self.ui = appui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.logo.setPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(
            defaults.PROJECT_ABS_PATH,
            defaults.UI_IMAGES_PATH,
            'logo.png'))))
        self.ui.show_qr_btn.clicked.connect(self.qrBtnPressEvent)
        self.ui.skip_wifi_btn.clicked.connect(self.skipWiFiBtnPressEvent)
        self.ui.testnet_notice.hide()
        self.ui.wrong_passwd_lbl.hide()
        self.ui.connecting_lbl.hide()
        self.show()

    def processEvents(self):
        try:
            self._application.sendPostedEvents()
            self._application.processEvents()
        except NameError as error:
            logger.exception(error)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() == QtCore.Qt.Key_Return:
            xbterminal.runtime['CURRENT_STAGE'] = 'enter_amount'
            self.ui.main_stackedWidget.setCurrentIndex(6)
        self.keys.append(event.key())

    def closeEvent(self, event):
        xbterminal.runtime['CURRENT_STAGE'] = 'application_halt'

    def qrBtnPressEvent(self):
        xbterminal.runtime['screen_buttons']['qr_button'] = True

    def skipWiFiBtnPressEvent(self):
        xbterminal.runtime['screen_buttons']['skip_wifi'] = True

    def toggleTestnetNotice(self, show):
        if show:
            self.ui.testnet_notice.show()
        else:
            self.ui.testnet_notice.hide()

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

    def advanceLoadingProgressBar(self, level):
        self.ui.progressBar_percent.setValue(level)
        time.sleep(0.3)

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

    def retranslateUi(self, language_code):
        """
        Change UI language
        """
        if self._application.setLanguage(language_code):
            self.ui.retranslateUi(self)
            xbterminal.local_state['language'] = language_code
            xbterminal.helpers.configs.save_local_state()


def initGUI():
    """
    Initialize GUI
    """
    application = Application(sys.argv)
    application.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
    language_code = xbterminal.local_state.get(
        'language',
        defaults.UI_DEFAULT_LANGUAGE)
    application.setLanguage(language_code)
    main_window = GUI(application)
    adjust_screen_brightness(defaults.SCREEN_BRIGHTNESS)
    return main_window


def adjust_screen_brightness(value):
    command = "echo {0} > /sys/class/backlight/backlight.11/brightness".\
        format(value)
    subprocess.check_call(command, shell=True)


def formatCharSelectHelperHMTL(char_tupl, char_selected = None):
    char_list = []

    for index, char in enumerate(char_tupl):
        if char_selected == char:
            char_list.append("<strong><font color=\"#333333\" size=\"5\">{char_selected}</font></strong>".format(char_selected=char))
        else:
            char_list.append(str(char))

    char_string = ' '.join(char_list)

    return "<html><head/><body><p align=\"center\"><font color=\"#666666\">{char_string}</font></p></body></html>".format(char_string=char_string)


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
