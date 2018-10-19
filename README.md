# TBtray

####A Thunderbird tray addon for linux (best on KDE).

I only built it because we did'nt have any TB tray integration after Thunderbird 60+. 
Keep in mind im just a hobbyist. I'm doing this to try and learn a little about using git and github.

**you will need xdotool, wmctrl & qt5-multimedia installed**

### ***sudo pacman -S wmctrl xdotool qt5-multimedia***

Then run it from inside the tbtray folder.

**./tbtray.py**

All you need to do is run ./tbtray.py then select your INBOX.msf files for your accounts. 
Find (or manually enter) the path to your INBOX.msf files in the top bar and click "add" to put them
into your profile list box.

example of INBOX.msf :-
/home/greg/.thunderbird/tzvg3gbn.default/ImapMail/imap.gmail.com/INBOX.msf


#### **_You can not use the unified (Smart-mail) inbox._**


#### Features :-

* Minimize to tray
* Click tray icon to show/hide TB
* Show unread count on tray icon
* set icons (one for default (no unread), another for the notification
* Allow TBtray to take over the popup notification & sound from TB
* You can also click on the popup notification to show the TB window
* Set opacity of popup
* Popup option to Show favicons alongside individual emails (these are scraped once & then cached locally)
* Very low idle CPU



![Tray icon](https://i.imgur.com/Kocpyo8.png)

![Popup window](https://i.imgur.com/0AnneUK.png)

![Basic Settings](https://i.imgur.com/lIJKRgZ.png)

