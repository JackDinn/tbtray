# TBtray #

#### A Thunderbird tray addon for linux (best on KDE) ####

I only built it because we did'nt have any TB tray integration after Thunderbird 60+. 
Keep in mind im just a hobbyist. I'm doing this to try and learn a little about using git and github.


## Installation ##

    you will need to install these packages on your system first

    xdotool
    wmctrl                                          [these 2 control the window manager]
    python3-bs4 (or python-beautifulsoup4)          [One of these are for the favicon scraping] 
    python3-pyqt5.qtmultimedia (or qt5-multimedia)  [One of these are for the sound]
    
    Then clone the repo 
    git clone https://github.com/JackDinn/tbtray.git
    
    Run with
    tbtray/tbtray.py



After installing and running TBtray select your INBOX.msf files for your accounts. 
Find (or manually enter) the path to your INBOX.msf files in the top bar of the settings and click "add" to put them
into your profile list box.

example of INBOX.msf :-
/home/greg/.thunderbird/tzvg3gbn.default/ImapMail/imap.gmail.com/INBOX.msf


#### **_You can not use the unified (Smart-mail) inbox._** ####


#### Features :- ####

* Minimize to tray
* Click tray icon to show/hide TB
* Show unread count on tray icon
* set icons (one for default (no unread), another for the notification
* Allow TBtray to take over the popup notification & sound from TB
* You can also click on the popup notification to show the TB window
* Set opacity of popup
* popup duration control
* Popup option to Show favicons alongside individual emails (these are scraped once & then cached locally)
* Very low idle CPU & Memory.



![Tray icon](https://i.imgur.com/Kocpyo8.png)

![Popup window](https://i.imgur.com/0AnneUK.png)

![Basic Settings](https://i.imgur.com/4PiAi30.png)


### General usage ###
TBtray executes TB so i advise creating a launcher that runs TBtray to replace your TB launcher.

You can close both TBtray and TB together via the tray icon.

You can run TBtray after TB is already running and it will work but you may need to "synchronize" it by clicking the tray icon.

I can not figure a way to intercept the TB close signal so i can not have TBtray minimize TB when you click close on TB. The best i can do is to close both TB and TBtray if you close TB.

TBtray (PyQt5) does not seem to work well on Wayland.


### Removal of TBtray ###
just delete the tbtray folder and the settings folder found at ~/.config/tbtray