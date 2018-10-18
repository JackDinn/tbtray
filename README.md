# tbtray
A Thunderbird tray addon for linux (best on KDE).

I only built it because we did'nt have any TB tray integration and i was also 
bored, but others can feel free to use it. Keep in mind im just a hobbyist. I'm doing this to try and
 learn a little about using git and github.

**you will need xdotool, wmctrl & qt5-multimedia installed**

### ***sudo pacman -S wmctrl xdotool qt5-multimedia*** ###

Then run it from inside the tbtray folder

**./tbtray.py**

All you need to do is run ./tbtray.py then select your INBOX.msf files for your accounts. 
You might need to first remove any paths listed in the main profile box (select them and click remove)
then find (or manually enter) the path to your Inbox.msf files in the top bar and click "add" to put them
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
* Very low idle CPU


![Basic Settings](https://i.imgur.com/W3XY70L.png)