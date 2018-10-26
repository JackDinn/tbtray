#!/usr/bin/env python3
import base64
import configparser
import getpass
import os
import quopri
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from shutil import copyfile
from urllib.parse import urlparse

import requests
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QFont
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QFileDialog, QColorDialog
from bs4 import BeautifulSoup
from time import strftime

import tbtrayui


def close():
    os.system('pkill thunderbird')
    sys.exit(0)


def log(tex=''):
    return
    tim = strftime("%y-%m-%d %H:%M:%S")
    with open('log.txt', 'a+') as qq:
        qq.write(tim + ' ' + tex + '\n')
    return


def parse_markup_for_favicon(markup, url):
    parsed_site_uri = urlparse(url)
    soup = BeautifulSoup(markup, features="html5lib")
    icon_link = soup.find('link', rel='icon')
    if icon_link and icon_link.has_attr('href'):
        favicon_url = icon_link['href']
        if favicon_url.startswith('//'):
            parsed_uri = urlparse(url)
            favicon_url = parsed_uri.scheme + ':' + favicon_url
        elif favicon_url.startswith('/'):
            favicon_url = parsed_site_uri.scheme + '://' + parsed_site_uri.netloc + favicon_url
        elif not favicon_url.startswith('http'):
            path, filename = os.path.split(parsed_site_uri.path)
            favicon_url = parsed_site_uri.scheme + '://' + parsed_site_uri.netloc + '/' + os.path.join(path, favicon_url)
        return favicon_url
    return None


def get_favicon_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'}
    parsed_site_uri = urlparse(url)
    try:
        response = requests.get(url, headers=headers)
    except:
        raise Exception("Unable to find URL. Is it valid? %s" % url)
    if response.status_code == requests.codes.ok:
        favicon_url = parse_markup_for_favicon(response.content, url)
        if favicon_url:
            return favicon_url
    favicon_url = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(uri=parsed_site_uri)
    response = requests.get(favicon_url, headers=headers)
    if response.status_code == requests.codes.ok:
        return favicon_url
    return None


def getfavicon(url):
    path = str(Path.home()) + '/.config/tbtray/icons/'
    iconpath = path + url + '.ico'
    if Path.is_file(Path(iconpath)):
        return iconpath
    try:
        favicon_url = get_favicon_url('http://' + url)
        log('favicon URL ' + favicon_url)
        icon = urllib.request.urlopen(favicon_url)
        with open(iconpath, "wb") as f:
            f.write(icon.read())
        return iconpath
    except:
        log('Cant get icon from that URL!')
        return 'res/thunderbird.png'

    # try:
    #     path = str(Path.home()) + '/.config/tbtray/icons/'
    #     iconpath = path + url + '.ico'
    #     if Path.is_file(Path(iconpath)):
    #         return iconpath
    #     icon = urllib.request.urlopen('https://api.faviconkit.com/' + url + '/16')
    #     with open(iconpath, "wb") as f:
    #         f.write(icon.read())
    #     return iconpath
    # except:
    #     return 'res/thunderbird.png'


def checksettings():
    my_dir = Path(str(Path.home()) + '/.config/tbtray')
    if not my_dir.is_dir(): my_dir.mkdir()
    if not Path(str(Path.home()) + '/.config/tbtray/icons').is_dir(): Path.mkdir(Path(str(Path.home()) + '/.config/tbtray/icons'))
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


def readmessage(path, count=1):
    from_text = []
    subject_text = []
    date_text = []
    messageid_text = []
    for gg in path:
        if not os.path.isfile(gg): continue
        text = subprocess.run(["tail", "-n", "6000", gg], stdout=subprocess.PIPE).stdout.decode('UTF-8')
        fromx = re.findall('\\r\\nFrom: (.*@.*)\\r\\n', text)[(0 - count):]
        subject = re.findall('\\r\\nSubject: (.*)\\r\\n', text)[0 - count:]
        date = re.findall('\\r\\nDate: (.*)\\r\\n', text)[0-count:]
        messageid = re.findall('\\r\\nMessage-I[Dd]: (.*)\\r\\n', text)[0-count:]
        for q in messageid:
            messageid_text.append(q)
        for w in date:
            date_text.append(w)
        for x in fromx:
            xx = str(x).replace('<', '&lt;')
            xx = str(xx).replace('>', '&gt;')
            from_text.append(xx)
        for tt in subject:
            xy = str(tt).replace('<', '&lt;')
            xy = str(xy).replace('>', '&gt;')
            subject_text.append(xy)
    return {'from': from_text, 'subject': subject_text, 'date': date_text, 'messageid': messageid_text}


class TextBrowser(QtWidgets.QTextBrowser):
    def __init__(self, parent=None):
        super(TextBrowser, self).__init__(parent)
        self.windowid = 0
        self.INTRAY = False
        self.hideme = False
        self.height = 100
        self.document().contentsChanged.connect(self.sizechange)

    def sizechange(self):
        docheight = self.document().size().height()
        self.height = int(docheight)
        self.setGeometry(5, 5, 322, self.height + 10)

    def mouseReleaseEvent(self, event):
        subprocess.run(["xdotool", "windowmap", self.windowid])
        subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])
        subprocess.run(["xdotool", "windowactivate", self.windowid])
        self.hideme = True
        self.INTRAY = True


class Popup(QtWidgets.QDialog):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setObjectName("formpopup")
        self.setGeometry(1585, 40, 330, 293)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setStatusTip("")
        self.setWindowTitle("formpopup")
        self.textBrowser = TextBrowser(self)
        self.textBrowser.setGeometry(5, 5, 322, 100)
        self.closebutton = QtWidgets.QPushButton(self)
        self.closebutton.setText('X')
        self.closebutton.setGeometry(304, 8, 20, 20)
        self.closebutton.setStyleSheet('color: red')
        self.closebutton.clicked.connect(self.clicked)
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
        self.xpos = 1585
        self.shownmessages = []

    def fire(self, profiles, count=1, firstrun=False, testrun=False):
        if testrun:
            if self.popupon or self.sound:
                if not self.isVisible():
                    self.textBrowser.clear()
                    self.browsertext = ''
                reg = re.findall('@(.*?\.[a-zA-Z]*\.*[a-zA-Z]*)', 'fred@twitter.com')[0]
                for tt in range(3):
                    icon = getfavicon(reg)
                    if self.favicons:
                        self.browsertext += '<h3 style="color: DodgerBlue"><img height="30" width="30" src="' + icon + '"/>&nbsp;&nbsp;Twitter &lt;binfo@twitter.com&gt;</h3><p>This is a test message'
                    else:
                        self.browsertext += '<h3 style="color: DodgerBlue">Mail Info:- From address</h3><p>Subject line of text'
                if self.popupon: self.show()
                self.textBrowser.setText(self.browsertext)
                self.setGeometry(self.xpos, 40, 330, self.textBrowser.height + 20)
                if self.soundon: self.sound.play()
                self.popup_timer.start(self.duration * 1000)
                self.popup_timer2.start()
                return
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
                    if not self.isVisible():
                        self.textBrowser.clear()
                        self.browsertext = ''
                    for x in range(len(mailinfo['messageid'])):
                        fromx = self.encoded_words_to_text(mailinfo['from'][x - 1])
                        log('from ' + fromx)
                        subject = self.encoded_words_to_text(mailinfo['subject'][x - 1])
                        if self.favicons:
                            fav = re.findall('@(.*?\.[a-zA-Z]*\.*[a-zA-Z]*)', fromx)[0]
                            log('get favicon ' + fav)
                            icon = getfavicon(fav)
                            self.browsertext += '<h3 style="color: DodgerBlue"><img height="30" width="30" src="' + icon + '"/>&nbsp;&nbsp;' + fromx + '</h3><p>' + subject
                        else:
                            self.browsertext += '<h3 style="color: DodgerBlue"><center>' + fromx + '</center></h3><p>' + subject
                    if self.popupon: self.show()
                    if self.soundon: self.sound.play()
                    self.textBrowser.setText(self.browsertext)
                    self.setGeometry(self.xpos, 40, 330, self.textBrowser.height + 20)
                    self.popup_timer.start(self.duration * 1000)
                    self.popup_timer2.start()

    @staticmethod
    def encoded_words_to_text(encoded_words):
        byte_string = ''
        encoded_word_regex = r'(.*)=\?{1}(.+)\?{1}([B|Q|b|q])\?{1}(.+)\?{1}=(.*)'
        if not re.match(encoded_word_regex, encoded_words): return encoded_words
        front, charset, encoding, encoded_text, back = re.match(encoded_word_regex, encoded_words).groups()
        try:
            if encoding is 'B'or encoding is 'b':
                byte_string = base64.b64decode(encoded_text)
            elif encoding is 'Q' or encoding is 'q':
                byte_string = quopri.decodestring(encoded_text)
            if byte_string: return front + byte_string.decode(charset) + back
        except:
            print('def encoded_words_to_text:  LookupError: unknown encoding')
            return 'Could Not decode Subject string'

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


class MainApp(QtWidgets.QDialog, tbtrayui.Ui_Form):

    def __init__(self):
        super(self.__class__, self).__init__()
        os.system('thunderbird > /dev/null 2>&1 &')
        os.chdir(os.path.dirname(sys.argv[0]))
        self.my_settings_file = Path(str(Path.home()) + '/.config/tbtray/settings.ini')
        log('')
        log('TBtray started ################################################ ')
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
        checksettings()
        config = configparser.ConfigParser()
        config.read(self.my_settings_file)
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
        self.actionsetup()
        self.timersetup()

    def actionsetup(self):
        self.label_accountwarrning.setText('')
        self.popup.duration = self.spinBox_displaytime.value()
        self.popup.favicons = self.checkBox_favicons.isChecked()
        self.popup.setWindowOpacity(float(self.horizontalSlider_opacity.value()/100))
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
        if self.badprofile: self.tray_icon.showMessage('TBtray Profile Warning', 'Please setup account profiles', QSystemTrayIcon.Critical)
        self.popup.fire(self.profiles, 10, True)

    def func_toolbutton_firepopup(self):
        self.popup.fire(self.profiles, 2, False, True)

    def func_toolbutton_notifysound(self):
        x = QFileDialog.getOpenFileName(self, 'Select Notify Sound File', '/home/' + getpass.getuser())[0]
        if x: self.lineEdit_notifysound.setText(x)

    def func_colourpicker(self):
        x = QColorDialog.getColor(QColor(self.colour))
        if x.isValid():
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
        x = QFileDialog.getOpenFileName(self, 'Select Profile .msf File', '/home/' + getpass.getuser() + '/.thunderbird/', "INBOX.msf(INBOX.msf)")[0]
        if x: self.editline_profilepath.setText(x)

    def cancel(self):
        self.testforprofile()
        self.hide()
        self.checkBox_favicons.setChecked(self.popup.favicons)
        self.label_colour.setStyleSheet('color: ' + self.colour)
        self.spinBox_xpos.setValue(self.popup.xpos)
        self.checkBox_popup.setChecked(self.popup.popupon)
        self.lineEdit_notifysound.setText(self.popup.sound.fileName())
        self.checkBox_notifysound.setChecked(self.popup.soundon)
        self.horizontalSlider_opacity.setValue(int(self.popup.windowOpacity()*100))
        self.spinBox_displaytime.setValue(self.popup.duration)
        self.timetriggercheck.start(1000)

    def ok(self):
        config = configparser.ConfigParser()
        config['popup'] = {}
        config['popup']['duration'] = str(self.spinBox_displaytime.value())
        self.popup.duration = self.spinBox_displaytime.value()
        config['popup']['favicons'] = str(int(self.checkBox_favicons.isChecked()))
        self.popup.favicons = self.checkBox_favicons.isChecked()
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
        with open(self.my_settings_file, 'w') as configfile:
            config.write(configfile)
            configfile.close()
        self.hide()
        self.timetriggercheck.start(1000)
        self.popup.fire(self.profiles, 10, True)

    def settings(self):
        self.timetriggercheck.stop()
        self.show()

    def iconclick(self):
        if self.checkbox_minimizetotray.isChecked() and not self.badprofile:
            self.timetriggercheck.stop()
            stdout = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE).stdout.decode('UTF-8')
            if stdout:
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            else:
                subprocess.run(["xdotool", "windowmap", self.windowid])
                subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                self.INTRAY = False
            self.timetriggercheck.start(1000)

    def iconmenushowhide(self):
        if not self.badprofile:
            self.timetriggercheck.stop()
            stdout = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE).stdout.decode('UTF-8')
            if stdout:
                subprocess.run(["xdotool", "windowunmap", self.windowid])
                self.INTRAY = True
            else:
                subprocess.run(["xdotool", "windowmap", self.windowid])
                subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'remove,skip_taskbar'])
                subprocess.run(["xdotool", "windowactivate", self.windowid])
                self.INTRAY = False
            self.timetriggercheck.start(1000)

    def fire(self):
        stdout = subprocess.run(["pgrep", "-i", "thunderbird"], stdout=subprocess.PIPE).stdout.decode('UTF-8')
        if not stdout: sys.exit()
        if self.badprofile:
            self.label_accountwarrning.setText('ERROR! Please Fix Account List')
            self.label_accountwarrning.setStyleSheet('color: red')
            self.label_accountwarrning.show()
            self.tabWidget.setCurrentIndex(1)
            return
        self.timetriggercheck.stop()
        if self.popup.textBrowser.INTRAY:
            self.INTRAY = False
            self.popup.textBrowser.INTRAY = False
        if not self.windowid:
            stdout = subprocess.run(["wmctrl", '-lx'], stdout=subprocess.PIPE).stdout.decode('UTF-8')
            idx = re.findall('(\dx\w+)..0 Mail\.Thunderbird', str(stdout))
            if idx:
                self.windowid = idx[0]
                self.popup.textBrowser.windowid = self.windowid
                print('grabbed window ' + idx[0])
        if self.checkbox_minimizetotray.isChecked() and not self.INTRAY:
            stdout = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", self.winclass], stdout=subprocess.PIPE).stdout.decode('UTF-8')
            if not stdout and self.windowid:
                subprocess.run(['wmctrl', '-i', '-r', str(self.windowid), '-b', 'add,skip_taskbar'])
                self.INTRAY = True
        for profile in self.profiles:
            if os.path.getmtime(profile) > self.lastmtime:
                self.lastmtime = os.path.getmtime(profile)
                self.matches = 0
                for profile2 in self.profiles:
                    if not os.path.isfile(profile2): continue
                    filetext = subprocess.run(["tail", "-n", "2000", profile2], stdout=subprocess.PIPE).stdout.decode('UTF-8')
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
