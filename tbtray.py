#!/usr/bin/env python
import configparser
import getpass
import os
import re
import subprocess
import sys

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QFont
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QFileDialog

import tbtrayui


def close():
    os.system('pkill thunderbird')
    sys.exit(0)


class ExampleApp(QtWidgets.QDialog, tbtrayui.Ui_Form):

    def __init__(self):
        super(self.__class__, self).__init__()
        os.system('thunderbird & disown')
        os.chdir(os.path.dirname(sys.argv[0]))
        self.matches = 0
        self.lastmtime = 0
        self.timetriggercheck = QTimer(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.INTRAY = False
        self.winclass = 'thunderbird'
        self.windowid = 0
        self.setupUi(self)
        self.profiles = []
        self.defaulticon = self.lineedit_defulticon.text()
        self.notifyicon = self.lineedit_notifyicon.text()
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.checkbox_showcount.setChecked(bool(int(config['ticks']['showcount'])))
        self.checkbox_minimizetotray.setChecked(bool(int(config['ticks']['minimizetotray'])))
        self.defaulticon = config['icons']['default']
        self.lineedit_defulticon.setText(config['icons']['default'])
        self.notifyicon = config['icons']['notify']
        self.lineedit_notifyicon.setText(config['icons']['notify'])
        for value in config['profiles']:
            self.profiles.append(config['profiles'][str(value)])
            self.listWidget.addItem(config['profiles'][str(value)])
        self.actionsetup()
        self.testforprofile()
        self.timersetup()

    def actionsetup(self):
        self.tray_icon.setIcon(QtGui.QIcon(self.defaulticon))
        action_hideshow = QAction("Hide/Show", self)
        action_settings = QAction("Settings", self)
        action = QAction("Exit", self)
        action.triggered.connect(close)
        action_hideshow.triggered.connect(self.iconclick)
        action_settings.triggered.connect(self.settings)
        self.tray_icon.activated.connect(self.iconclick)
        tray_menu = QMenu()
        tray_menu.addAction(action_hideshow)
        tray_menu.addAction(action_settings)
        tray_menu.addAction(action)
        self.tray_icon.setContextMenu(tray_menu)
        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_ok.clicked.connect(self.ok)
        self.toolButton_profilepath.clicked.connect(self.selectfile)
        self.pushButton_add.clicked.connect(self.func_pushbutton_add)
        self.pushButton_remove.clicked.connect(self.func_pushbutton_remove)
        self.checkbox_minimizetotray.clicked.connect(self.func_minimizetotrayclicked)
        self.toolButton_defaulticon.clicked.connect(self.func_defaulticon)
        self.toolButton_notifyicon.clicked.connect(self.func_notifyicon)
        self.tray_icon.show()

    def func_defaulticon(self):
        x = QFileDialog.getOpenFileName(self, 'Select Default Icon', '/home/' + getpass.getuser())[0]
        if x:
            self.lineedit_defulticon.setText(x)

    def func_notifyicon(self):
        x = QFileDialog.getOpenFileName(self, 'Select Notify Icon', '/home/' + getpass.getuser())[0]
        if x:
            self.lineedit_notifyicon.setText(x)

    def func_minimizetotrayclicked(self):
        if not self.checkbox_minimizetotray.isChecked():
            subprocess.run(['wmctrl', '-r', 'thunderbird', '-b', 'remove,skip_taskbar'])

    def func_pushbutton_add(self):
        self.listWidget.addItem(self.editline_profilepath.text())

    def func_pushbutton_remove(self):
        self.listWidget.takeItem(self.listWidget.currentRow())

    def testforprofile(self):
        if not self.profiles:
            self.editline_profilepath.setText("Please check your profile paths")
            return
        try:
            for value in self.profiles:
                vv = open(value, 'r')
                vv.close()
            self.lastmtime = 0
            self.editline_profilepath.setText('Profiles look OK')
        except (IsADirectoryError, FileNotFoundError):
            self.editline_profilepath.setText("Please check your profile paths")

    def timersetup(self):
        self.timetriggercheck.timeout.connect(self.fire)
        self.timetriggercheck.start(1000)

    def selectfile(self):
        x = QFileDialog.getOpenFileName(self, 'Select Profile .msf File', '/home/' + getpass.getuser() + '/.thunderbird/')[0]
        if x:
            self.editline_profilepath.setText(x)

    def cancel(self):
        self.testforprofile()
        self.hide()
        self.timetriggercheck.start(1000)

    def ok(self):
        config = configparser.ConfigParser()
        config['ticks'] = {}
        config['ticks']['minimizetotray'] = str(int(self.checkbox_minimizetotray.isChecked()))
        config['ticks']['showcount'] = str(int(self.checkbox_showcount.isChecked()))
        config['icons'] = {}
        config['icons']['default'] = self.lineedit_defulticon.text()
        self.defaulticon = self.lineedit_defulticon.text()
        config['icons']['notify'] = self.lineedit_notifyicon.text()
        self.notifyicon = self.lineedit_notifyicon.text()
        config['profiles'] = {}
        self.profiles.clear()
        for x in range(self.listWidget.count()):
            self.profiles.append(self.listWidget.item(x).text())
            config['profiles'][str(x)] = self.listWidget.item(x).text()
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
            configfile.close()
        self.testforprofile()
        self.fire()
        self.hide()
        self.timetriggercheck.start(1000)

    def settings(self):
        self.timetriggercheck.stop()
        self.show()

    def iconclick(self):
        if self.checkbox_minimizetotray.isChecked():
            self.timetriggercheck.stop()
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if stdout:
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            else:
                subprocess.run(["xdotool", "windowmap", self.windowid])
                subprocess.run(['wmctrl', '-r', 'thunderbird', '-b', 'remove,skip_taskbar'])
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                self.INTRAY = False
            self.timetriggercheck.start(1000)

    def fire(self):
        if self.editline_profilepath.text() == "Please check your profile paths":
            self.show()
            self.activateWindow()
            self.timetriggercheck.stop()
            return
        self.timetriggercheck.stop()
        if self.checkbox_minimizetotray.isChecked() and not self.INTRAY:
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if not stdout and self.windowid:
                subprocess.run(['wmctrl', '-r', 'thunderbird', '-b', 'add,skip_taskbar'])
                self.INTRAY = True
            else:
                self.windowid = result.stdout.decode('UTF-8')
        for profile in self.profiles:
            if os.path.getmtime(profile) > self.lastmtime:
                print('profile changed ! ' + profile)
                self.lastmtime = os.path.getmtime(profile)
                self.matches = 0
                for profile2 in self.profiles:
                    file = open(profile2, 'r')
                    filetext = file.read()
                    file.close()
                    matchesx = re.findall('\^A2=(\w+)', filetext)
                    if matchesx:
                        self.matches += int(matchesx[-1], 16)
                if self.matches > 0:
                    if self.checkbox_showcount.isChecked():
                        iconpixmap = QtGui.QPixmap(self.notifyicon)
                        font = QFont("Boulder", 14)
                        count = str(self.matches)
                        pixmap = QPixmap(iconpixmap.width(), iconpixmap.height())
                        painter = QPainter()
                        pixmap.fill(Qt.transparent)
                        painter.begin(pixmap)
                        painter.setFont(font)
                        painter.setOpacity(0.3)
                        painter.drawPixmap(iconpixmap.rect(), iconpixmap)
                        painter.setOpacity(1.0)
                        painter.setPen(QColor(255, 255, 255))
                        fm = QFontMetrics(font)
                        painter.drawText(int((pixmap.width() - fm.width(count)) / 2), int((pixmap.height() - fm.height()) / 2 + fm.ascent() + 1), count)
                        painter.end()
                        self.tray_icon.setIcon(QtGui.QIcon(pixmap))
                    else:
                        self.tray_icon.setIcon(QtGui.QIcon(self.notifyicon))
                else:
                    self.tray_icon.setIcon(QtGui.QIcon(self.defaulticon))
                break
        self.timetriggercheck.start(1000)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = ExampleApp()
    ui.hide()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
