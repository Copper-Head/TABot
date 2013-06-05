TABot
==============================
A small and occasionally useful script for downloading batches of email attachments
from IMAP mailboxes. Currently, only downloading executable scripts from Gmail is supported and *no* Yahoo! support is projected in the near future!

[MIT License](http://opensource.org/licenses/MIT) (click if you'd like to read
it).


Motivation
------------------------------
For one of my jobs at UMass Amherst every week I had to download over 20 email attachments sent
in as homework submissions by students in the class I was TAing. 
This task has always stricken me as unnecessarily tedious and ripe for automation. 
One evening I finally got a chance to sit down with IMAP documentation and produce a small script
that would extract all the attachments from emails in a specified folder.
The script grew a bit since then and now has some additional functionality as well as an improved
mechanism for determining what to download.

Usage
------------------------------
It's simple. All you really need is an up-to-date installation of Python 2.7.x
(the code should work with 3.x, but hasn't been tested on it) and some
knowledge of how to use the terminal/bash. 

The main script is in the file "mailbot.py" and the below instructions reference it only. 
The "attachmentbot.py" file provides just
downloading functionality which is equivalently covered by the ``mailbot" script,
so I'm considering getting rid of it completely.
As things are, running "mailbot.py" without any command-line options does the same as running
"attachmentbot.py".
In addition, "mailbot" supports some optional arguments whereas "attachmentbot" does not.

* Place the mailbot.py file into the folder where you want to download
your files to.
* Run the file by typing in  ```python mailbot.py [-h] [-comments | -send_from COMMENTS_FILE_NAME]```
* If you run the file without providing any options it will simply start the download process.
All the other options are explained later.
* When prompted, enter your email login credentials along with the name of the folder you want 
	to download  attachments from.
* Relax while watching loads of attachments get copied to your computer one by one!

Command-Line Options
------------------------------

* -h 	
	displays the help for the program
* -comments 	
	if this flag is included, the program will generate a comments file corresponding
  	to the downloaded files; incompatible with the "-send_from" option
* -send_from COMMENTS_FILE_NAME 
this option is incompatible with the "-comments" option; when used, it tells the
program to send out emails using the COMMENTS_FILE_NAME as the source of comments instead
of its normal behavior (downloading attachments to the current directory)

Disclaimer
------------------------------

The ability to store email addresses in a file and use them later to send email is controversial
from some views of privacy and you must check with your supervisor before you enjoy that functionality. 
All responsibility for the results lies with the user.

N.B.
------------------------------
The folder name is case and space sensitive. This means *Folder Name* is
different from *folder name* is different from *folderName*. I would also
advise against specifying your whole Inbox as the target folder, since the
script at this point downloads all attachments indiscriminately and so
running it on one's entire Inbox may quickly get out of hand.
