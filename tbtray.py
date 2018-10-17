#!/usr/bin/env python
import base64
import configparser
import getpass
import os
import quopri
import re
import subprocess
import sys

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QFont
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QFileDialog, QColorDialog

import tbtrayui


def close():
    os.system('pkill thunderbird')
    sys.exit(0)


def readmessage(path, count=1):
    from_text = []
    subject_text = []
    date_text = []
    messageid_text = []
    for gg in path:
        if not os.path.isfile(gg): continue
        tex = subprocess.run(["tail", "-n", "8000", gg], stdout=subprocess.PIPE)
        text = tex.stdout.decode('UTF-8')
        fromx = re.findall('\\r\\nFrom: (.*@.*)\\r\\n', text)[(0 - count):]
        subject = re.findall('\\r\\nSubject: (.*)\\r\\n', text)[0 - count:]
        date = re.findall('\\r\\nDate: (.*)\\r\\n', text)[0-count:]
        messageid = re.findall('\\r\\nMessage-I[Dd]: (.*)\\r\\n', text)[0-count:]
        for q in messageid:
            messageid_text.append(q)
        for w in date:
            date_text.append(w)
        for x in fromx:
            xx = str(x).replace('<', '"')
            xx = str(xx).replace('>', '"')
            from_text.append(xx)
        for tt in subject:
            subject_text.append(tt)
    return {'from': from_text, 'subject': subject_text, 'date': date_text, 'messageid': messageid_text}


class TextBrowser(QtWidgets.QTextBrowser):
    def __init__(self, parent=None):
        super(TextBrowser, self).__init__(parent)
        self.windowid = 0
        self.INTRAY = False

    def mouseReleaseEvent(self, event):
        subprocess.run(["xdotool", "windowmap", self.windowid])
        subprocess.run(['wmctrl', '-r', 'Mozilla Thunderbird', '-b', 'remove,skip_taskbar'])
        subprocess.run(["xdotool", "windowactivate", self.windowid])
        self.INTRAY = True


class Popup(QtWidgets.QDialog):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setObjectName("formpopup")
        self.resize(407, 303)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setStatusTip("")
        self.setWindowTitle("formpopup")
        QtCore.QMetaObject.connectSlotsByName(self)
        self.textBrowser = TextBrowser(self)
        self.textBrowser.setGeometry(5, 5, 322, 100)
        self.popupon = True
        self.sound = QSound("res/popup.wav")
        self.soundon = True
        self.popup_timer = QTimer(self)
        self.popup_timer.setSingleShot(True)
        self.popup_timer.timeout.connect(self.timer)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.X11BypassWindowManagerHint)
        self.setWindowOpacity(0.90)
        self.xpos = 1585
        self.shownmessages = []

    def fire(self, profiles, count=1, firstrun=False, testrun=False):
        if testrun:
            if self.popupon or self.sound:
                self.textBrowser.clear()
                xx = ''
                for tt in range(3):
                    xx += '<h3 style="color: DodgerBlue"><center>Mail Info:- From address</center></h3><p>Subject line of text</p>'
                self.textBrowser.setText(xx)
                self.setGeometry(self.xpos, 40, 330, 90 * 3)
                self.textBrowser.setGeometry(5, 5, 322, (90*3)-10)
                self.popup_timer.start(20000)
                if self.popupon: self.show()
                if self.soundon: self.sound.play()

        if self.popupon or self.sound:
            popprofiles = []
            fileexists = False
            for ss in range(len(profiles)):
                popprofiles.append(profiles[ss].replace('INBOX.msf', 'INBOX'))
                if os.path.isfile(popprofiles[ss]): fileexists = True
            if fileexists:
                mailinfo = readmessage(popprofiles, count)
                up = 0
                for mc in range(len(mailinfo['messageid'])):
                    if self.shownmessages.__contains__(mailinfo['messageid'][up]):
                        mailinfo['from'].pop(up)
                        mailinfo['subject'].pop(up)
                        mailinfo['date'].pop(up)
                        mailinfo['messageid'].pop(up)
                    else: up += 1
                for fr in mailinfo['messageid']: self.shownmessages.append(fr)
                if not firstrun and len(mailinfo['messageid']) > 0:
                    self.textBrowser.clear()
                    vv = ''
                    for x in range(len(mailinfo['messageid'])):
                        decode = self.encoded_words_to_text(mailinfo['subject'][x - 1])
                        vv += '<h3 style="color: DodgerBlue"><center>' + mailinfo['from'][x - 1] + '</center></h3><p>' + decode
                    self.textBrowser.setText(vv)
                    self.setGeometry(self.xpos, 40, 330, 90*len(mailinfo['messageid']))
                    self.textBrowser.setGeometry(5, 5, 322, ((90 * len(mailinfo['messageid'])) - 10))
                    self.popup_timer.start(10000)
                    if self.popupon: self.show()
                    if self.soundon: self.sound.play()

    @staticmethod
    def encoded_words_to_text(encoded_words):
        byte_string = ''
        encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
        if not re.match(encoded_word_regex, encoded_words): return encoded_words
        charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
        if encoding is 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding is 'Q':
            byte_string = quopri.decodestring(encoded_text)
        return byte_string.decode(charset)

    def timer(self):
        self.hide()

    def clicked(self):
        self.hide()


class MainApp(QtWidgets.QDialog, tbtrayui.Ui_Form):

    def __init__(self):
        super(self.__class__, self).__init__()
        os.system('thunderbird > /dev/null 2>&1 & disown')
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
        self.badprofile = True
        self.defaulticon = self.lineedit_defulticon.text()
        self.notifyicon = self.lineedit_notifyicon.text()
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.horizontalSlider_opacity.setValue(int(config['popup']['opacity']))
        self.checkBox_popup.setChecked(bool(int(config['popup']['on'])))
        self.lineEdit_notifysound.setText(config['popup']['soundpath'])
        self.checkBox_notifysound.setChecked(bool(int(config['popup']['soundon'])))
        self.spinBox_xpos.setValue(int(config['popup']['x']))
        self.colour = config['icons']['colour']
        self.colour_pre = config['icons']['colour']
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
        self.testforprofile()
        self.popup = Popup()
        self.actionsetup()
        self.timersetup()

    def actionsetup(self):
        self.popup.setWindowOpacity(float(self.horizontalSlider_opacity.value()/100))
        self.popup.xpos = self.spinBox_xpos.value()
        self.popup.popupon = self.checkBox_popup.isChecked()
        self.popup.soundon = self.checkBox_notifysound.isChecked()
        self.popup.sound = QSound(self.lineEdit_notifysound.text())
        self.tray_icon.setIcon(QtGui.QIcon(self.defaulticon))
        self.tray_icon.setToolTip('TB-Tray')
        action_hideshow = QAction("Hide/Show", self)
        action_settings = QAction("Settings", self)
        action = QAction("Exit", self)
        tray_menu = QMenu()
        tray_menu.addAction(action_hideshow)
        tray_menu.addAction(action_settings)
        tray_menu.addAction(action)
        self.tray_icon.setContextMenu(tray_menu)
        action.triggered.connect(close)
        action_hideshow.triggered.connect(self.iconmenushowhide)
        action_settings.triggered.connect(self.settings)
        self.toolButton_firepopup.clicked.connect(self.func_toolbutton_firepopup)
        self.toolButton_notifysound.clicked.connect(self.func_toolbutton_notifysound)
        self.tray_icon.activated.connect(self.iconclick)
        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_ok.clicked.connect(self.ok)
        self.toolButton_profilepath.clicked.connect(self.selectfile)
        self.pushButton_add.clicked.connect(self.func_pushbutton_add)
        self.pushButton_remove.clicked.connect(self.func_pushbutton_remove)
        self.checkbox_minimizetotray.clicked.connect(self.func_minimizetotrayclicked)
        self.toolButton_defaulticon.clicked.connect(self.func_defaulticon)
        self.toolButton_notifyicon.clicked.connect(self.func_notifyicon)
        self.pushButton_colourpicker.clicked.connect(self.func_colourpicker)
        self.tray_icon.show()
        self.popup.fire(self.profiles, 10, True)

    def func_toolbutton_firepopup(self):
        self.popup.fire(self.profiles, 2, False, True)

    def func_toolbutton_notifysound(self):
        x = QFileDialog.getOpenFileName(self, 'Select Notify Sound File', '/home/' + getpass.getuser())[0]
        if x: self.lineEdit_notifysound.setText(x)

    def func_colourpicker(self):
        x = QColorDialog.getColor()
        if x:
            self.label_colour.setStyleSheet('color: ' + x.name())
            self.colour_pre = x.name()

    def func_defaulticon(self):
        x = QFileDialog.getOpenFileName(self, 'Select Default Icon', '/home/' + getpass.getuser())[0]
        if x: self.lineedit_defulticon.setText(x)

    def func_notifyicon(self):
        x = QFileDialog.getOpenFileName(self, 'Select Notify Icon', '/home/' + getpass.getuser())[0]
        if x: self.lineedit_notifyicon.setText(x)

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
        x = QFileDialog.getOpenFileName(self, 'Select Profile .msf File', '/home/' + getpass.getuser() + '/.thunderbird/', "INBOX.msf(INBOX.msf)")[0]
        if x: self.editline_profilepath.setText(x)

    def cancel(self):
        self.testforprofile()
        self.hide()
        self.label_colour.setStyleSheet('color: ' + self.colour)
        self.spinBox_xpos.setValue(self.popup.xpos)
        self.checkBox_popup.setChecked(self.popup.popupon)
        self.lineEdit_notifysound.setText(self.popup.sound.fileName())
        self.checkBox_notifysound.setChecked(self.popup.soundon)
        self.horizontalSlider_opacity.setValue(int(self.popup.windowOpacity()*100))
        self.timetriggercheck.start(1000)

    def ok(self):
        config = configparser.ConfigParser()
        config['popup'] = {}
        config['popup']['opacity'] = str(int(self.horizontalSlider_opacity.value()))
        self.popup.setWindowOpacity(float(self.horizontalSlider_opacity.value()/100))
        config['popup']['on'] = str(int(self.checkBox_popup.isChecked()))
        self.popup.popupon = self.checkBox_popup.isChecked()
        config['popup']['soundpath'] = self.lineEdit_notifysound.text()
        self.popup.sound = QSound(self.lineEdit_notifysound.text())
        config['popup']['soundon'] = str(int(self.checkBox_notifysound.isChecked()))
        self.popup.soundon = self.checkBox_notifysound.isChecked()
        config['popup']['x'] = str(self.spinBox_xpos.value())
        self.popup.xpos = self.spinBox_xpos.value()
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
        if self.popup.textBrowser.INTRAY:
            self.INTRAY = False
            self.popup.textBrowser.INTRAY = False
        if self.checkbox_minimizetotray.isChecked() and not self.INTRAY:
            result = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE)
            stdout = result.stdout.decode('UTF-8')
            if not stdout and self.windowid:
                subprocess.run(['wmctrl', '-r', 'Mozilla thunderbird', '-b', 'add,skip_taskbar'])
                self.INTRAY = True
            else:
                self.windowid = result.stdout.decode('UTF-8')
                self.popup.textBrowser.windowid = self.windowid
        for profile in self.profiles:
            if os.path.getmtime(profile) > self.lastmtime:
                self.lastmtime = os.path.getmtime(profile)
                self.matches = 0
                for profile2 in self.profiles:
                    if not os.path.isfile(profile2): continue
                    tex = subprocess.run(["tail", "-n", "2000", profile2], stdout=subprocess.PIPE)
                    filetext = tex.stdout.decode('UTF-8')
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
                    else: self.tray_icon.setIcon(QtGui.QIcon(self.notifyicon))
                    if not self.badprofile: self.popup.fire(self.profiles, self.matches)
                else: self.tray_icon.setIcon(QtGui.QIcon(self.defaulticon))
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
