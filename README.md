AttachmentBot
==============================
A very small but occasionally useful script for downloading batches of email attachments
from IMAP mailboxes. Currently, only downloading executable scripts from Gmail is supported and *no* Yahoo! support is projected in the near future!

[MIT License](http://opensource.org/licenses/MIT) (click if you'd like to read
it).


Motivation
------------------------------
For one of my jobs in college I have to download over 20 email attachments sent
in as homework submissions by students. This task has always stricken me as
unnecessarily tedious and ripe for automation. One evening I finally got a
chance to sit down with IMAP documentation 

Usage
------------------------------
It's simple. All you really need is an up-to-date installation of Python 2.7.x
(the code should work with 3.x, but hasn't been tested on it) and some
knowledge of how to use the terminal/bash. Once these two conditions have been
met, here's the plan:

* Just place the attachmentbot.py file into the folder where you want to download
your files to.
* Run the file by typing in  ```python attachmentbot.py```
* When prompted, enter your email login credentials (yea, you still *do* need
  to do this) along with the name of the folder you want to download
  attachments from.
* Relax while watching loads of attachments get copied to your computer one by one!

N.B.
------------------------------
The folder name is case and space sensitive. This means *Folder Name* is
different from *folder name* is different from *folderName*. I would also
advise against specifying your whole Inbox as the target folder, since the
script at this point downloads all attachments indiscriminately and so
running it on one's entire Inbox may quickly get out of hand.
