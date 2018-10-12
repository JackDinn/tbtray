#!/usr/bin/env python
import configparser
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
        self.lastmtime = 0
        self.timetriggercheck = QTimer(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.INTRAY = False
        self.winclass = 'thunderbird'
        self.windowid = 0
        self.setupUi(self)
        self.actionsetup()
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.profilepath = (config['DEFAULT']['profilepath'])
        self.testforprofile()
        self.timersetup()

    def actionsetup(self):
        self.tray_icon.setIcon(QtGui.QIcon("res/thunderbird.png"))
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
        self.tray_icon.show()

    def testforprofile(self):
        try:
            vv = open(self.profilepath, 'r')
            vv.close()
        except (IsADirectoryError, FileNotFoundError):
            self.profilepath = "Please input path to unified Inbox.msf"
            self.editline_profilepath.setText("Please input path to unified Inbox.msf")
            self.show()
            self.activateWindow()

    def timersetup(self):
        self.timetriggercheck.timeout.connect(self.fire)
        self.timetriggercheck.start(1000)

    def selectfile(self):
        self.editline_profilepath.setText(QFileDialog.getOpenFileName()[0])

    def cancel(self):
        self.testforprofile()
        self.hide()

    def ok(self):
        self.profilepath = self.editline_profilepath.text()
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'profilepath': self.profilepath}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
            configfile.close()
        self.testforprofile()
        self.hide()

    def settings(self):
        self.editline_profilepath.setText(self.profilepath)
        self.show()

    def iconclick(self):
        self.timetriggercheck.stop()
        result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass],
                                stdout=subprocess.PIPE)
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
        if self.profilepath == "Please input path to unified Inbox.msf":
            self.show()
            self.activateWindow()
            return
        self.timetriggercheck.stop()
        if not self.INTRAY:
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass],
                                    stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if not stdout and self.windowid:
                subprocess.run(['wmctrl', '-r', 'thunderbird', '-b', 'add,skip_taskbar'])
                self.INTRAY = True
            else:
                self.windowid = result.stdout.decode('UTF-8')
            if os.path.getmtime(self.profilepath) > self.lastmtime:
                self.lastmtime = os.path.getmtime(self.profilepath)
                file = open(self.profilepath, 'r')
                filetext = file.read()
                file.close()
                matchesx = re.findall('\^A2=(\w+)', filetext)
                matches = int(matchesx[-1], 16)
                if matches > 0:
                    font = QFont("Boulder", 14)
                    iconpixmap = QtGui.QPixmap("res/mail.png")
                    count = str(matches)
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
                    painter.drawText(int((pixmap.width() - fm.width(count)) / 2),
                                     int((pixmap.height() - fm.height()) / 2 + fm.ascent() + 1), count)
                    painter.end()
                    self.tray_icon.setIcon(QtGui.QIcon(pixmap))
                else:
                    self.tray_icon.setIcon(QtGui.QIcon("res/thunderbird.png"))
            self.timetriggercheck.start(1000)
            return


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = ExampleApp()
    ui.hide()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
