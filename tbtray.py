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
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QFileDialog, QColorDialog

import popup
import tbtrayui


def close():
    os.system('pkill thunderbird')
    sys.exit(0)


def readmessage(count=1):
    from_text = []
    file = open('/home/greg/.thunderbird/tzvg3gbn.default/ImapMail/jackdinn.co.uk.mail.aa.net-1.uk/INBOX', encoding="utf8", errors='ignore')
    text = file.read()
    file.close()
    fromx = re.findall('From: (.*@.*)', text)[(0 - count):]
    subject = re.findall('Subject: (.*)', text)[-20:]
    date = re.findall('Date: (.*)', text)[0-count:]
    messageid = re.findall('Message-ID: (.*)', text)[0-count:]
    
    if not messageid:
        messageid_text = ['Empty']
    else:
        messageid_text = messageid
    if not date:
        date_text = ['Empty']
    else:
        date_text = date
    if not fromx:
        from_text = ['Empty']
    else:
        for x in fromx:
            xx = str(x).replace('<', '"')
            xx = str(xx).replace('>', '"')
            from_text.append(xx)
    if not subject:
        subject_text = ['Empty']
    else:
        subject_text = list(filter(None, subject))
        subject_text = subject_text[(0 - count):]
    return {'from': from_text, 'subject': subject_text, 'date': date_text, 'messageid': messageid_text}


class Popup(QtWidgets.QDialog, popup.Ui_formpopup):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.sound = QSound("res/popup.wav")
        self.popup_timer = QTimer(self)
        self.popup_timer.setSingleShot(True)
        self.popup_timer.timeout.connect(self.timer)
        self.pushButton.clicked.connect(self.clicked)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.X11BypassWindowManagerHint)
        self.setWindowOpacity(0.80)
        self.setGeometry(1615, 60, 300, 320)
        self.shownmessages = []
        # self.fire()

    def fire(self, count=1):
        mailinfo = readmessage(count)
        self.textBrowser.clear()
        up = 0
        for mc in range(len(mailinfo['messageid'])):
            if self.shownmessages.__contains__(mailinfo['messageid'][up]):
                mailinfo['from'].pop(up)
                mailinfo['subject'].pop(up)
                mailinfo['date'].pop(up)
                mailinfo['messageid'].pop(up)
                count -= 1
            else: up += 1
        for x in range(count):
            self.textBrowser.append('<h3 style="color: green"><center>' + mailinfo['from'][x-1] + '</center></h3><p>'
                                    + mailinfo['subject'][x-1])
        print('count ' + str(count))
        for fr in mailinfo['messageid']:
            self.shownmessages.append(fr)
        print('mailinfo ' + str(len(mailinfo['messageid'])))
        if len(mailinfo['messageid']) > 0:
            self.setGeometry(1615, 60, 300, 100*count)
            self.popup_timer.start(6000)
            # self.textBrowser.mouseDoubleClickEvent(self.click())
            self.show()
            self.sound.play()

    def timer(self):
        self.hide()
        # sys.exit(0)

    def clicked(self):
        self.hide()


class MainApp(QtWidgets.QDialog, tbtrayui.Ui_Form):

    def __init__(self):
        super(self.__class__, self).__init__()
        # os.system('thunderbird > /dev/null 2>&1 & disown')
        os.chdir(os.path.dirname(sys.argv[0]))
        self.popup = Popup()
        self.matches = 0
        self.lastmtime = 0
        self.timetriggercheck = QTimer(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.INTRAY = False
        self.winclass = 'thunderbird'
        self.windowid = 0
        self.setupUi(self)
        self.profiles = []
        self.badprofile = True
        self.colour_pre = ''
        self.defaulticon = self.lineedit_defulticon.text()
        self.notifyicon = self.lineedit_notifyicon.text()
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.colour = config['icons']['colour']
        self.label_colour.setStyleSheet('color: ' + self.colour)
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
        self.tray_icon.setToolTip('TB-Tray')
        action_hideshow = QAction("Hide/Show", self)
        action_settings = QAction("Settings", self)
        action = QAction("Exit", self)
        action.triggered.connect(close)
        action_hideshow.triggered.connect(self.iconmenushowhide)
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
        self.pushButton_colourpicker.clicked.connect(self.func_colourpicker)
        self.popup.pushButton.clicked.connect(self.iconclick)
        self.tray_icon.show()
        # self.tray_icon.showMessage('Title', 'message here')
        print(self.tray_icon.geometry().width())
        print(self.tray_icon.geometry().height())
        # self.popup.show()

    def func_colourpicker(self):
        x = QColorDialog.getColor()
        if x:
            self.label_colour.setStyleSheet('color: ' + x.name())
            self.colour_pre = x.name()

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
            subprocess.run(['wmctrl', '-r', 'Mozilla thunderbird', '-b', 'remove,skip_taskbar'])

    def func_pushbutton_add(self):
        self.listWidget.addItem(self.editline_profilepath.text())

    def func_pushbutton_remove(self):
        self.listWidget.takeItem(self.listWidget.currentRow())

    def testforprofile(self):
        if not self.profiles:
            self.editline_profilepath.setText("Please check your profile paths")
            self.badprofile = True
            return
        try:
            for value in self.profiles:
                vv = open(value, 'r')
                vv.close()
            self.lastmtime = 0
            self.editline_profilepath.setText('Profiles look OK')
            self.badprofile = False
        except (IsADirectoryError, FileNotFoundError):
            self.badprofile = True
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
        self.label_colour.setStyleSheet('color: ' + self.colour)
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
        self.colour = self.colour_pre
        config['icons']['colour'] = self.colour
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
        if self.checkbox_minimizetotray.isChecked() and not self.badprofile:
            self.timetriggercheck.stop()
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if stdout:
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            else:
                subprocess.run(["xdotool", "windowmap", self.windowid])
                subprocess.run(['wmctrl', '-r', 'Mozilla Thunderbird', '-b', 'remove,skip_taskbar'])
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                self.INTRAY = False
            self.timetriggercheck.start(1000)

    def iconmenushowhide(self):
        if not self.badprofile:
            self.timetriggercheck.stop()
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if stdout:
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            else:
                subprocess.run(["xdotool", "windowmap", self.windowid])
                subprocess.run(['wmctrl', '-r', 'Mozilla thunderbird', '-b', 'remove,skip_taskbar'])
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                self.INTRAY = False
            self.timetriggercheck.start(1000)

    def fire(self):
        if self.badprofile:
            self.show()
            self.activateWindow()
            self.tabWidget.setCurrentIndex(1)
            return
        self.timetriggercheck.stop()
        if self.checkbox_minimizetotray.isChecked() and not self.INTRAY:
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if not stdout and self.windowid:
                subprocess.run(['wmctrl', '-r', 'Mozilla thunderbird', '-b', 'add,skip_taskbar'])
                self.INTRAY = True
            else:
                self.windowid = result.stdout.decode('UTF-8')
        for profile in self.profiles:
            if os.path.getmtime(profile) > self.lastmtime:
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
                        count = str(self.matches)
                        pixmap = QPixmap(iconpixmap.width(), iconpixmap.height())
                        fontsize = self.findfontsize(count, pixmap)
                        font = QFont("Arial", fontsize)
                        painter = QPainter()
                        pixmap.fill(Qt.transparent)
                        painter.begin(pixmap)
                        painter.setFont(font)
                        painter.setOpacity(0.3)
                        painter.drawPixmap(iconpixmap.rect(), iconpixmap)
                        painter.setOpacity(1.0)
                        painter.setPen(QColor(self.colour))
                        fm = QFontMetrics(font)
                        painter.drawText(int((pixmap.width() - fm.width(count)) / 2), int((pixmap.height() - fm.height()) / 2 + fm.ascent() + 1), count)
                        painter.end()
                        self.tray_icon.setIcon(QtGui.QIcon(pixmap))
                    else:
                        self.tray_icon.setIcon(QtGui.QIcon(self.notifyicon))
                    self.popup.fire(3)

                else:
                    self.tray_icon.setIcon(QtGui.QIcon(self.defaulticon))
                break
        self.timetriggercheck.start(1000)

    @staticmethod
    def findfontsize(text, pixmap):
        x = 4
        for x in range(4, 200):
            font = QFont("Arial", x)
            fm = QFontMetrics(font)
            if fm.width(text) > pixmap.width() or fm.height() > pixmap.height():
                break
        return x


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainApp()
    ui.hide()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
