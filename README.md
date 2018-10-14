# tbtray
A rough hash up for a thunderbird tray addon for linux (best on KDE).

Its not really meant for anyone else to use but iv got nothing against people using it. Keep in mind im probably the worlds
worst coder. I'm doing this to try and learn a little about using git and github.

**you will need xdotool & wmctrl installed and Its a PyQt5 project**

**pacman -S wmctrl xdotool**

Then run it from inside the tbtray folder

**./tbtray.py**

All you need to do is run ./tbtray.py then select your Inbox.msf files. You might need to first remove any paths listed in the
main profile box (select it and click remove) then find (or manualy enter) the path to your Inbox.msf files in the top bar.
Add them to the main profile list by clicking the "add" button.

i.e :-
"/home/user/.thunderbird/tdvx3gPn.default/Mail/smart mailboxes/Inbox.msf"

