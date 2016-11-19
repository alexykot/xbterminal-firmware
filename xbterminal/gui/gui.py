# -*- coding: utf-8 -*-
import logging
import os
import re
import sys
import time
import functools
import imp
import random

from PyQt4 import QtGui, QtCore

from xbterminal.gui.utils import configs
from xbterminal.gui import ui as appui
from xbterminal.gui import settings
from xbterminal.gui.state import state
from xbterminal.gui.keypad import Keypad

logger = logging.getLogger(__name__)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(
            context, text, disambig,
            QtGui.QApplication.UnicodeUTF8)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Application(QtGui.QApplication):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.loadConfig()
        self.initResources()
        self._translators = {}
        self.language = settings.UI_DEFAULT_LANGUAGE
        self.loadTranslations()

    def loadConfig(self):
        state['gui_config'] = configs.load_gui_config()

    def initResources(self):
        theme = state['gui_config'].get(
            'theme',
            settings.UI_DEFAULT_THEME)
        file, pathname, description = imp.find_module(
            theme, [settings.UI_THEMES_PATH])
        imp.load_module(theme, file, pathname, description)

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
        ts_dir = settings.UI_TRANSLATIONS_PATH
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
        if self.language != settings.UI_DEFAULT_LANGUAGE:
            self.removeTranslator(self._translators[self.language])
        if language_code != settings.UI_DEFAULT_LANGUAGE:
            self.installTranslator(self._translators[language_code])
        self.language = language_code
        return True


class GUI(QtGui.QMainWindow):

    def __init__(self):
        # Initialize Qt application
        application = Application(sys.argv)
        application.loadFonts()
        if state['gui_config'].get('show_cursor'):
            application.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        else:
            application.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        language_code = state['gui_config'].get(
            'language',
            settings.UI_DEFAULT_LANGUAGE)
        application.setLanguage(language_code)
        application.loadStyles()
        # Initialize Qt main window
        super(GUI, self).__init__()
        self._application = application
        # Keypad
        state['keypad'] = Keypad()
        # Initialize UI
        self.ui = appui.Ui_MainWindow()
        self.ui.setupUi(self)
        # Loader
        self.loader = QtGui.QMovie(':/images/loading.gif')
        self.ui.loader_lbl.setMovie(self.loader)
        self.loader.start()
        # Set up buttons
        for button_name in settings.BUTTONS:
            button = getattr(self.ui, button_name)
            button.clicked.connect(
                functools.partial(self.buttonPressEvent, button_name))
        # Show window
        self._saved_screen = self.currentScreen()
        self.show()

    def processEvents(self):
        try:
            self._application.sendPostedEvents()
            self._application.processEvents()
        except NameError as error:
            logger.exception(error)

    def keyPressEvent(self, event):
        state['keyboard_events'].append(event.key())

    def buttonPressEvent(self, button_name):
        logger.debug('button "{0}" pressed'.format(button_name))
        state['last_activity_timestamp'] = time.time()
        state['screen_buttons'][button_name] = True

    def currentScreen(self):
        screen_index = self.ui.main_stackedWidget.currentIndex()
        for screen_name, i in settings.SCREENS.items():
            if i == screen_index:
                return screen_name

    def showScreen(self, screen_name):
        screen_index = settings.SCREENS[screen_name]
        self.ui.main_stackedWidget.setCurrentIndex(screen_index)

    def showStandByScreen(self):
        screen_index = settings.SCREENS['standby']
        if self.ui.main_stackedWidget.currentIndex() != screen_index:
            self.ui.main_stackedWidget.setCurrentIndex(screen_index)
        btn_width = self.ui.standby_wake_btn.width()
        btn_height = self.ui.standby_wake_btn.height()
        widget_width = self.ui.standby_wake_widget.width()
        widget_height = self.ui.standby_wake_widget.height()
        widget_x = random.randint(0, btn_width - widget_width)
        widget_y = random.randint(0, btn_height - widget_height)
        self.ui.standby_wake_widget.setGeometry(
            widget_x, widget_y, widget_width, widget_height)

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
            state['gui_config']['language'] = language_code
            configs.save_gui_config(state['gui_config'])

    def showConnectionError(self):
        error_message = _translate('MainWindow', 'connection error', None)
        if self.currentScreen() != 'errors':
            # Show error screen
            self._saved_screen = self.currentScreen()
            self.showScreen('errors')
        self.ui.errors_lbl.setText(unicode(error_message))

    def hideConnectionError(self):
        if self.currentScreen() == 'errors':
            # Restore previous screen
            self.showScreen(self._saved_screen)
