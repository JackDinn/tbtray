#!/usr/bin/env python

import os
import re
import subprocess
import sys
import time
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QFont
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon

import tbtrayui


def close():
    os.system('pkill thunderbird')
    sys.exit(0)


class ExampleApp(QtWidgets.QDialog, tbtrayui.Ui_Form):

    def __init__(self):
        super(self.__class__, self).__init__()
        os.system('thunderbird & disown')
        time.sleep(5)
        os.chdir(os.path.dirname(sys.argv[0]))
        self.sound = QSound("media/new_mail_notification.wav")
        self.file = "/home/greg/.thunderbird/tzvg3gbn.default/Mail/smart mailboxes/Inbox.msf"
        self.lastmtime = 0
        self.timetriggercheck = QTimer(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.INTRAY = False
        self.winclass = 'thunderbird'
        result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass],
                                stdout=subprocess.PIPE)
        self.windowid = result.stdout.decode('UTF-8')
        self.setupUi(self)
        self.traysetup()
        self.timersetup()
        self.fire()

    def timersetup(self):
        self.timetriggercheck.timeout.connect(self.fire)
        self.timetriggercheck.start(1000)

    def traysetup(self):
        self.tray_icon.setIcon(QtGui.QIcon("res/thunderbird.png"))
        action_settings = QAction("Settings", self)
        action = QAction("Exit", self)
        action.triggered.connect(close)
        action_settings.triggered.connect(self.settings)
        self.tray_icon.activated.connect(self.iconclick)
        tray_menu = QMenu()
        tray_menu.addAction(action)
        tray_menu.addAction(action_settings)
        self.tray_icon.setContextMenu(tray_menu)
        self.pushButton_cancel.clicked.connect(self.close)
        self.pushButton_ok.clicked.connect(self.ok)
        self.tray_icon.show()

    def close(self):
        self.hide()

    def ok(self):
        self.hide()

    def settings(self):
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
            self.INTRAY = False
        self.timetriggercheck.start(1000)

    def fire(self):
        self.timetriggercheck.stop()
        if not self.INTRAY:
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass],
                                    stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if not stdout:
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
                print('minimize')

        if os.path.getmtime(self.file) > self.lastmtime:
            self.lastmtime = os.path.getmtime(self.file)
            file = open(self.file, 'r')
            filetext = file.read()
            file.close()
            matches = re.findall('A2=(\d+)', filetext)
            if int(matches[-1]) > 0:
                font = QFont("Arial Black", 16)
                iconpixmap = QtGui.QPixmap("res/mail.png")
                count = matches[-1]
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
