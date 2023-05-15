#!/usr/bin/env python3
import configparser
import getpass
import mailbox
import os
import re
import subprocess
import sys
import urllib.request
from email.header import decode_header, make_header
from pathlib import Path
from shutil import copyfile
from time import strftime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QAction, QColorDialog, QFileDialog, QMenu, QSystemTrayIcon

import tbtrayui


def close():
    os.system('pkill thunderbird')
    sys.exit(0)


def checkvisable():
    winname = ' - Mozilla Thunderbird'
    try:
        # check 3 times because sometimes when there are lots of child windows open it misses the fact that the TB window is actually visible.
        for two in range(3):
            out = subprocess.run(
                ["xdotool", "search", "--all", "--onlyvisible", "--maxdepth", "3", "--limit", "1", "--name", winname],
                stdout=subprocess.PIPE).stdout.decode('UTF-8')
            log('check is TB window visable ' + out)
            if out: return True
    except:
        pass
    return False


def log(tex=''):
    try:
        tail = subprocess.run(["tail", "-n", "500", "log.txt"], stdout=subprocess.PIPE).stdout.decode('UTF-8')
        with open('log.txt', 'w+') as xx:
            xx.write(tail)
        tim = strftime("%y-%m-%d %H:%M:%S")
        with open('log.txt', 'a+') as qq:
            qq.write(tim + ' ' + tex + '\n')
    except:
        pass


def getfavicon(url):
    path = str(Path.home()) + '/.config/tbtray/icons/'
    iconpath = path + url + '.ico'
    if Path.is_file(Path(iconpath)):
        log('Local icon ' + iconpath)
        return iconpath
    try:
        log('favicon URL https://www.google.com/s2/favicons?domain=' + url)
        data = urllib.request.urlopen('https://www.google.com/s2/favicons?domain=' + url)
        icon = data.read()
        if icon == b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f' \
                   b'\xf3\xffa\x00\x00\x01\xb3IDATx\x01b\xf8\xff\xff?E\x18\xce\xf0\x8b\x9c\xc7\xe9\xe8;C\xb6\xaai[PI\xed\xe6\xbd\xc9\xb9' \
                   b'\xab>\x86\xc4\x03\xe8\xa6\x86\xed\xda\x82(\xf81\xefc\xde\xf4b\x18\xdb\xb6\xedd\x1a\xdb\xb6m\xdb\xb6m\';]\x83\xee\xd5W{' \
                   b'\xad\xe3\xaa\xda\xaaS\xf8\x83\xc3\xd2\xb9\xf2\xc1+\xb8\xa9\'\x80}\x03\x06X\xce\x13\xe4\xff\xaa\xac\x7f.~\xf5\xf1\x16N\x15' \
                   b'\xab1\xc9\xdd\xd7E\xb5\xb3\x94S1E\xb8\x0eO\x1fPX\\\xc7\xb5\x99C\xf9\xaa\x8bo]<\xb0\xe0\x08\x01\xa8\xba\xf8\xd6\xc7[\xb9T\x1d' \
                   b'\xa6d\x0cRm\xfb\nu\x0cn\xd1\xd5\xdd\x1b\xed\x9f<\x10\xe2\xf4\xf2\x85\xf0\x8e\x89\x1c:\xfb\xd4\xc5\x83#\x04P\x9a\x99c\xf9*2\x81' \
                   b'\x8c\xa3\xa9g\x1d\x87\x10\xf8\xfe!\xea\x1d\xdb\xa5>v\x98:\x94\xad\x82#\x04\xd0\x1fJ\x04\x08d\xf9xx\xfe"\x04\xaex\x9e_=\xa3\xe0' \
                   b'\xe8\xf6k\xcf\xa0\xc6\x1e!\x80!!;@\xfa\xc8\xbc\x82\x95\xad+\xc2{`\xcd\x1d+\x1e\x84\x80\xda\xb4\xe0gk\xff\x8e\x10\xe8\x13@N\x96' \
                   b'\x03-@\x00X\x95q\xfe\x8f\x86\x00\x86\xc4K\xe5\x03\xd4\'\x80\xb9@@)\x0b\xb0\xd5\xa1\x05\x92\x03\xcf\xfc\xe0\xe2\x08&\x8cw\xd8\xc6' \
                   b'\x83\xc6\x10\xc3\xd9\x10%\xbe\xce<&\x16N\x88\x87_x\xcb\xb5G`c\x8f\xbcF%L\x02eC\x0280H`L\xec\xd9\x1a#Z\x95\x1aF\x82\xc3\x98\x17\x0ee' \
                   b'\x11\xf4\xca\xc9\xb8\x1f\x06\xd9\xaeL\xd7H\xdc\xca\xceL\x04&a\xff\xc35\xc00\r\xec\x9cV4N\x81\x91m\xd7\xc8\x0c\xb2\x8e\x95\xe5' \
                   b'\x9f\t\xa5\xc1$\xd8\xb3\xca\xa4\xe0\x07\xd3\xfe\x1b(\xc0\x80b{\xaa\x9b\xb7\x078a\xc9L\x14a\x00BM\xf5\xdf\xed\xe70\xb1\x00\x00' \
                   b'\x00\x00IEND\xaeB`\x82':
            os.symlink(os.getcwd() + '/res/thunderbird.png', iconpath)
            return 'res/thunderbird.png'
        with open(iconpath, "wb") as f:
            f.write(icon)
        return iconpath
    except:
        log('Failed google scrape ' + url)
        return 'res/thunderbird.png'


def checksettings():
    my_dir = Path(str(Path.home()) + '/.config/tbtray')
    if not my_dir.is_dir(): my_dir.mkdir()
    if not Path(str(Path.home()) + '/.config/tbtray/icons').is_dir(): Path.mkdir(
        Path(str(Path.home()) + '/.config/tbtray/icons'))
    my_file = Path(str(Path.home()) + '/.config/tbtray/settings.ini')
    if not my_file.is_file(): copyfile('settings.ini', str(my_file))
    config_new = configparser.ConfigParser()
    config_old = configparser.ConfigParser()
    config_new.read('settings.ini')
    config_old.read(str(my_file))
    for xx in config_new.sections():
        if xx == 'profiles': continue
        if not config_old.__contains__(xx):
            config_old.add_section(xx)
        for hh in config_new[xx]:
            if not config_old[xx].__contains__(hh):
                config_old[xx][hh] = config_new[xx][hh]
    with open(my_file, 'w') as configfile:
        config_old.write(configfile)
        configfile.close()


def readmessage(path):
    from_text = []
    subject_text = []
    date_text = []
    messageid_text = []
    for gg in path:
        try:
            if not os.path.isfile(gg): continue
            text = subprocess.run(["tail", "-n", "10000", gg], stdout=subprocess.PIPE).stdout.decode('UTF-8', "ignore")
            with open('/tmp/tbtraydata', 'w+') as xyz:
                xyz.write(text)
            fr = mailbox.mbox('/tmp/tbtraydata')
            if os.path.isfile('/tmp/tbtraydata'): os.remove('/tmp/tbtraydata')
            for q in fr:
                try:
                    messageid_text.append(str(make_header(decode_header(q['message-ID']))))
                    date_text.append(str(make_header(decode_header(q['date']))))
                    from_text.append(
                        str(make_header(decode_header(q['from']))).replace('<', '&lt;').replace('>', '&gt;'))
                    subject_text.append(str(make_header(decode_header(q['subject']))).replace('\r\n', '<br>'))
                except:
                    continue
        except:
            continue
    return {'from': from_text, 'subject': subject_text, 'date': date_text, 'messageid': messageid_text}


class TextBrowser(QtWidgets.QTextBrowser):
    windowid: int

    def __init__(self, parent=None):
        super(TextBrowser, self).__init__(parent)
        self.windowid = 0
        self.INTRAY = False
        self.hideme = False
        self.height = 100
        self.width = 100
        self.fixedwidth = True
        self.document().contentsChanged.connect(self.sizechange)

    def sizechange(self):
        docwidth = 300
        docheight = self.document().size().height()
        if self.fixedwidth: docwidth = 300
        if not self.fixedwidth: docwidth = self.document().size().width()
        self.height = int(docheight)
        self.width = int(docwidth)
        self.setGeometry(5, 5, self.width + 10, self.height + 5)

    def mouseReleaseEvent(self, event):
        subprocess.run(["xdotool", "windowmap", self.windowid])
        subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])
        subprocess.run(["xdotool", "windowactivate", self.windowid])
        self.hideme = True
        self.INTRAY = True


class Popup(QtWidgets.QDialog):

    # noinspection PyArgumentList
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setObjectName("formpopup")
        self.setGeometry(1185, 40, 430, 993)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setStatusTip("")
        self.setWindowTitle("formpopup")
        self.setObjectName('formpopup')
        self.textBrowser = TextBrowser(self)
        self.textBrowser.setGeometry(5, 5, 150, 100)
        self.textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.closebutton = QtWidgets.QPushButton(self)
        self.closebutton.setText('X')
        self.closebutton.setGeometry(404, 8, 20, 20)
        self.closebutton.setStyleSheet('color:red;')
        self.closebutton.clicked.connect(self.clicked)
        self.screenheight = getscreenheight()
        self.top = True
        self.duration = 10
        self.browsertext = ''
        self.favicons = True
        self.popupon = True
        self.sound = QSound("res/popup.wav")
        self.soundon = True
        self.popup_timer = QTimer(self)
        self.popup_timer.setSingleShot(True)
        self.popup_timer.timeout.connect(self.timer)
        self.popup_timer2 = QTimer(self)
        self.popup_timer2.setInterval(1000)
        self.popup_timer2.timeout.connect(self.timer2)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.X11BypassWindowManagerHint)
        self.setWindowOpacity(0.90)
        self.xpos = 1485
        self.shownmessages = []

    def fire(self, profiles, firstrun=False):
        if self.popupon or self.soundon:
            popprofiles = []
            fileexists = False
            for ss in range(len(profiles)):
                popprofiles.append(profiles[ss].replace('INBOX.msf', 'INBOX'))
                if os.path.isfile(popprofiles[ss]): fileexists = True
            if fileexists:
                mailinfo = readmessage(popprofiles)
                up = 0
                for mc in range(len(mailinfo['messageid'])):
                    if self.shownmessages.__contains__(mailinfo['messageid'][up]):
                        mailinfo['from'].pop(up)
                        mailinfo['subject'].pop(up)
                        mailinfo['date'].pop(up)
                        mailinfo['messageid'].pop(up)
                    else:
                        up += 1
                for fr in mailinfo['messageid']: self.shownmessages.append(fr)
                if not firstrun and len(mailinfo['messageid']) > 0:
                    if not self.isVisible():
                        self.browsertext = ''
                    for x in range(len(mailinfo['messageid'])):
                        log('parsed from ' + mailinfo['from'][x - 1])
                        log('parsed subj ' + mailinfo['subject'][x - 1])
                        fromx = mailinfo['from'][x - 1]
                        subject = mailinfo['subject'][x - 1]
                        if self.favicons:
                            fromxy = fromx + '&'
                            log('fromxy ' + fromxy)
                            fav = re.findall('@\S*?\.?([\w|-]*(\.\w{2,3})?\.\w{2,3})&', fromxy)
                            if len(fav) > 0:
                                log('get favicon ' + fav[0][0])
                                icon = getfavicon(fav[0][0])
                            else:
                                icon = 'res/thunderbird.png'
                            self.browsertext += '<h3 style="color: DodgerBlue"><img height="20" width="20" src="' + icon + '"/>&nbsp;&nbsp;' + fromx + '</h3><p>' + subject
                        else:
                            self.browsertext += '<h3 style="color: DodgerBlue"><center>' + fromx + '</center></h3><p>' + subject
                    if self.popupon: self.show()
                    if self.soundon: self.sound.play()
                    self.textBrowser.clear()
                    self.textBrowser.setText(self.browsertext)
                    if self.top:
                        self.setGeometry(self.xpos - self.textBrowser.width, 40, self.textBrowser.width + 20,
                                         self.textBrowser.height + 15)
                    else:
                        self.setGeometry(self.xpos - self.textBrowser.width,
                                         self.screenheight - 55 - self.textBrowser.height, self.textBrowser.width + 20,
                                         self.textBrowser.height + 15)
                    self.closebutton.setGeometry(self.textBrowser.width - 4, 8, 20, 20)
                    self.popup_timer.start(self.duration * 1000)
                    self.popup_timer2.start()

    def timer2(self):
        if self.textBrowser.hideme:
            self.popup_timer2.stop()
            self.textBrowser.hideme = False
            self.hide()

    def timer(self):
        self.popup_timer2.stop()
        self.hide()

    def clicked(self):
        self.popup_timer2.stop()
        self.hide()


def getscreenheight():
    out = subprocess.run(["xrandr"], stdout=subprocess.PIPE).stdout.decode('UTF-8')
    matches = re.findall('\d*x(\d*).*?\*', out)
    if matches:
        log('get screen height ' + matches[0])
        return int(matches[0])
    else:
        log('get screen height ERROR')
        return 1080


class MainApp(QtWidgets.QDialog, tbtrayui.Ui_Form):

    def __init__(self):
        super(self.__class__, self).__init__()
        os.system('thunderbird > /dev/null 2>&1 &')
        stdout = subprocess.run(["pgrep", "-fc", "tbtray.py"], stdout=subprocess.PIPE).stdout.decode('UTF-8')
        if int(stdout) > 1:
            bob = open('/tmp/tbpassover', 'x')
            bob.close()
            log('make tmp passover file & close')
            sys.exit(0)
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.my_settings_file = Path(str(Path.home()) + '/.config/tbtray/settings.ini')
        log('')
        log('TBtray started ################################################ ')
        self.matches = 0
        self.lastmtime = 0
        self.timetriggercheck = QTimer(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.INTRAY = False
        self.windowid = 0
        self.setupUi(self)
        self.profiles = []
        self.badprofile = True
        self.defaulticon = self.lineedit_defulticon.text()
        self.notifyicon = self.lineedit_notifyicon.text()
        checksettings()
        config = configparser.ConfigParser()
        config.read(self.my_settings_file)
        self.radioButton_top.setChecked(bool(int(config['popup']['top'])))
        self.radioButton_bottom.setChecked(not bool(int(config['popup']['top'])))
        self.checkBox_fixedwidth.setChecked(bool(int(config['popup']['fixedwidth'])))
        self.spinBox_displaytime.setValue(int(config['popup']['duration']))
        self.checkBox_favicons.setChecked(bool(int(config['popup']['favicons'])))
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
        self.popup_test = Popup()
        self.actionsetup()
        self.timersetup()

    def actionsetup(self):
        self.label_accountwarrning.setText('')
        self.popup.top = self.radioButton_top.isChecked()
        self.popup.textBrowser.fixedwidth = self.checkBox_fixedwidth.isChecked()
        if self.popup.textBrowser.fixedwidth: self.popup.textBrowser.setLineWrapMode(QtWidgets.QTextBrowser.WidgetWidth)
        if not self.popup.textBrowser.fixedwidth: self.popup.textBrowser.setLineWrapMode(QtWidgets.QTextBrowser.NoWrap)
        self.popup.duration = self.spinBox_displaytime.value()
        self.popup.favicons = self.checkBox_favicons.isChecked()
        self.popup.setWindowOpacity(float(self.horizontalSlider_opacity.value() / 100))
        self.popup.xpos = self.spinBox_xpos.value()
        self.popup.popupon = self.checkBox_popup.isChecked()
        self.popup.soundon = self.checkBox_notifysound.isChecked()
        self.popup.sound = QSound(self.lineEdit_notifysound.text())
        self.tray_icon.setIcon(QtGui.QIcon(self.defaulticon))
        self.tray_icon.setToolTip('TBtray')
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
        if self.badprofile: self.tray_icon.showMessage('TBtray Profile Warning', 'Please setup account profiles',
                                                       QSystemTrayIcon.Critical)
        self.popup.fire(self.profiles, True)

    def func_toolbutton_firepopup(self):
        self.popup_test.textBrowser.windowid = self.windowid
        if not self.popup_test.isVisible():
            self.popup_test.browsertext = ''
        icon = 'res/thunderbird.png'
        self.popup_test.sound = QSound(self.lineEdit_notifysound.text())
        if self.checkBox_favicons.isChecked():
            self.popup_test.browsertext += '<h3 style="color: DodgerBlue"><img height="20" width="20" src="' + icon + '"/>&nbsp;&nbsp;Mail Info:- From address</h3><p>This is a test message. Lorem ipsum dolor sit amet, vivamus platea faucibus sed per penatibus.'
        else:
            self.popup_test.browsertext += '<h3 style="color: DodgerBlue">Mail Info:- From address</h3><p>This is a test message. Lorem ipsum dolor sit amet, vivamus platea faucibus sed per penatibus.'
        if self.checkBox_popup.isChecked(): self.popup_test.show()
        self.popup_test.setWindowOpacity(float(self.horizontalSlider_opacity.value() / 100))
        self.popup_test.textBrowser.fixedwidth = self.checkBox_fixedwidth.isChecked()
        if self.popup_test.textBrowser.fixedwidth: self.popup_test.textBrowser.setLineWrapMode(
            QtWidgets.QTextBrowser.WidgetWidth)
        if not self.popup_test.textBrowser.fixedwidth: self.popup_test.textBrowser.setLineWrapMode(
            QtWidgets.QTextBrowser.NoWrap)
        self.popup_test.textBrowser.clear()
        self.popup_test.textBrowser.setText(self.popup_test.browsertext)
        if self.radioButton_top.isChecked():
            self.popup_test.setGeometry(self.spinBox_xpos.value() - self.popup_test.textBrowser.width, 40,
                                        self.popup_test.textBrowser.width + 20, self.popup_test.textBrowser.height + 15)
        else:
            self.popup_test.setGeometry(self.spinBox_xpos.value() - self.popup_test.textBrowser.width,
                                        self.popup_test.screenheight - 55 - self.popup_test.textBrowser.height,
                                        self.popup_test.textBrowser.width + 20, self.popup_test.textBrowser.height + 15)
        self.popup_test.closebutton.setGeometry(self.popup_test.textBrowser.width - 4, 8, 20, 20)
        self.popup_test.popup_timer.start(self.spinBox_displaytime.value() * 1000)
        self.popup_test.popup_timer2.start()
        if self.checkBox_notifysound.isChecked(): self.popup_test.sound.play()

    def func_toolbutton_notifysound(self):
        x = QFileDialog.getOpenFileName(self, 'Select Notify Sound File', '/home/' + getpass.getuser())[0]
        if x: self.lineEdit_notifysound.setText(x)

    def func_colourpicker(self):
        x = QColorDialog.getColor(QColor(self.colour))
        if x.isValid():
            self.label_colour.setStyleSheet('color: ' + x.name())
            self.colour_pre = x.name()

    def func_defaulticon(self):
        x = \
            QFileDialog.getOpenFileName(self, 'Select Default Icon', 'res/',
                                        "Icons .png .ico .svg (*.png *.ico *.svg)")[0]
        if x: self.lineedit_defulticon.setText(x)

    def func_notifyicon(self):
        x = QFileDialog.getOpenFileName(self, 'Select Notify Icon', 'res/', "Icons .png .ico .svg (*.png *.ico *.svg)")[
            0]
        if x: self.lineedit_notifyicon.setText(x)

    def func_minimizetotrayclicked(self):
        if not self.checkbox_minimizetotray.isChecked():
            subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])

    def func_pushbutton_add(self):
        self.listWidget.addItem(self.editline_profilepath.text())
        self.testforprofile()

    def func_pushbutton_remove(self):
        self.listWidget.takeItem(self.listWidget.currentRow())
        self.testforprofile()

    def testforprofile(self):
        try:
            if self.listWidget.count() == 0: raise Exception()
            for value in range(self.listWidget.count()):
                vv = open(self.listWidget.item(value).text(), 'r')
                vv.close()
            self.lastmtime = 0
            self.label_accountwarrning.hide()
            self.badprofile = False
        except:
            self.label_accountwarrning.setText('ERROR! Please Fix Account List')
            self.label_accountwarrning.setStyleSheet('color: red')
            self.tabWidget.setCurrentIndex(1)
            self.label_accountwarrning.show()
            self.badprofile = True

    def timersetup(self):
        self.timetriggercheck.timeout.connect(self.fire)
        self.timetriggercheck.start(1000)

    def selectfile(self):
        x = \
            QFileDialog.getOpenFileName(self, 'Select Profile .msf File',
                                        '/home/' + getpass.getuser() + '/.thunderbird/',
                                        "INBOX.msf(INBOX.msf)")[0]
        if x: self.editline_profilepath.setText(x)

    def cancel(self):
        self.testforprofile()
        self.hide()
        self.checkBox_fixedwidth.setChecked(self.popup.textBrowser.fixedwidth)
        if self.popup.textBrowser.fixedwidth:
            self.popup.textBrowser.setLineWrapMode(QtWidgets.QTextBrowser.WidgetWidth)
        if not self.popup.textBrowser.fixedwidth:
            self.popup.textBrowser.setLineWrapMode(QtWidgets.QTextBrowser.NoWrap)
        self.checkBox_favicons.setChecked(self.popup.favicons)
        self.label_colour.setStyleSheet('color: ' + self.colour)
        self.radioButton_top.setChecked(self.popup.top)
        self.radioButton_bottom.setChecked(not self.popup.top)
        self.spinBox_xpos.setValue(self.popup.xpos)
        self.checkBox_popup.setChecked(self.popup.popupon)
        self.lineEdit_notifysound.setText(self.popup.sound.fileName())
        self.checkBox_notifysound.setChecked(self.popup.soundon)
        self.horizontalSlider_opacity.setValue(int(self.popup.windowOpacity() * 100))
        self.spinBox_displaytime.setValue(self.popup.duration)
        self.timetriggercheck.start(1000)

    def ok(self):
        config = configparser.ConfigParser()
        config['popup'] = {}
        config['popup']['top'] = str(int(self.radioButton_top.isChecked()))
        self.popup.top = self.radioButton_top.isChecked()
        config['popup']['fixedwidth'] = str(int(self.checkBox_fixedwidth.isChecked()))
        self.popup.textBrowser.fixedwidth = self.checkBox_fixedwidth.isChecked()
        if self.popup.textBrowser.fixedwidth: self.popup.textBrowser.setLineWrapMode(QtWidgets.QTextBrowser.WidgetWidth)
        if not self.popup.textBrowser.fixedwidth: self.popup.textBrowser.setLineWrapMode(QtWidgets.QTextBrowser.NoWrap)
        config['popup']['duration'] = str(self.spinBox_displaytime.value())
        self.popup.duration = self.spinBox_displaytime.value()
        config['popup']['favicons'] = str(int(self.checkBox_favicons.isChecked()))
        self.popup.favicons = self.checkBox_favicons.isChecked()
        config['popup']['opacity'] = str(int(self.horizontalSlider_opacity.value()))
        self.popup.setWindowOpacity(float(self.horizontalSlider_opacity.value() / 100))
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
        with open(self.my_settings_file, 'w') as configfile:
            config.write(configfile)
            configfile.close()
        self.hide()
        self.tray_icon.setIcon(QtGui.QIcon(self.defaulticon))
        self.timetriggercheck.start(1000)
        self.lastmtime = 0
        self.popup.fire(self.profiles, False)

    def settings(self):
        self.show()

    def iconclick(self):
        if self.checkbox_minimizetotray.isChecked() and not self.badprofile:
            log('self.windowid = ' + str(self.windowid))
            log('self.INTRAY = ' + str(self.INTRAY))
            self.timetriggercheck.stop()
            if checkvisable():
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            elif self.winId():
                subprocess.run(["xdotool", "windowmap", self.windowid])
                subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                self.INTRAY = False
            self.timetriggercheck.start(1000)

    def iconmenushowhide(self):
        if not self.badprofile:
            self.timetriggercheck.stop()
            if checkvisable():
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            elif self.winId():
                subprocess.run(["xdotool", "windowmap", self.windowid])
                subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                self.INTRAY = False
            self.timetriggercheck.start(1000)

    def fire(self):
        if self.checkbox_minimizetotray.isChecked() and os.path.isfile('/tmp/tbpassover'):
            if self.INTRAY:
                self.INTRAY = False
                self.popup.textBrowser.INTRAY = False
                self.popup_test.textBrowser.INTRAY = False
                subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])
            elif not self.INTRAY:
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            os.remove('/tmp/tbpassover')
            log('passover')
        stdout = subprocess.run(["pgrep", "-i", "thunderbird"], stdout=subprocess.PIPE).stdout.decode('UTF-8')
        if not stdout: sys.exit()
        if self.badprofile:
            self.label_accountwarrning.setText('ERROR! Please Fix Account List')
            self.label_accountwarrning.setStyleSheet('color: red')
            self.label_accountwarrning.show()
            self.tabWidget.setCurrentIndex(1)
            self.tray_icon.showMessage('TBtray Profile Warning', 'Please setup account profiles',
                                       QSystemTrayIcon.Critical)
            self.timetriggercheck.start(15000)
            return
        self.timetriggercheck.stop()
        if self.popup.textBrowser.INTRAY or self.popup_test.textBrowser.INTRAY:
            self.INTRAY = False
            self.popup.textBrowser.INTRAY = False
            self.popup_test.textBrowser.INTRAY = False
        if not self.windowid:
            stdout = subprocess.run(["wmctrl", '-lx'], stdout=subprocess.PIPE).stdout.decode('UTF-8')
            idx = re.findall('(\dx\w+)..0 Mail\.thunderbird', str(stdout))
            if idx:
                self.windowid = idx[0]
                self.popup.textBrowser.windowid = self.windowid
                log('grabbed window ' + idx[0])
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
        if self.checkbox_minimizetotray.isChecked() and not self.INTRAY:
            if not checkvisable() and self.windowid:
                subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'add,skip_taskbar'])
                self.INTRAY = True
        for profile in self.profiles:
            if os.path.getmtime(profile) > self.lastmtime:
                self.lastmtime = os.path.getmtime(profile)
                self.matches = 0
                for profile2 in self.profiles:
                    if not os.path.isfile(profile2): continue
                    filetext = subprocess.run(["tail", "-n", "2000", profile2], stdout=subprocess.PIPE).stdout.decode(
                        'UTF-8')
                    matchesx = re.findall('\^A2=(\w+)', filetext)
                    if matchesx: self.matches += int(matchesx[-1], 16)
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
                        painter.drawText(int((pixmap.width() - fm.width(count)) / 2),
                                         int((pixmap.height() - fm.height()) / 2 + fm.ascent() + 1), count)
                        painter.end()
                        self.tray_icon.setIcon(QtGui.QIcon(pixmap))
                    else:
                        self.tray_icon.setIcon(QtGui.QIcon(self.notifyicon))
                    if not self.badprofile: self.popup.fire(self.profiles)
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
