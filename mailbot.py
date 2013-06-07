# This program was created by Ilia Kurenkov, who decided he was fed up with
# manually downloading batches of email attachments from students, then
# responding to their submissions with comments and grades. The goal of this
# program is to make it so that its user (an instructor or TA) should only need
# to worry about making the right comments and grades and leave all the menial
# processing to MailBot.
# This program is free and subject to the conditions of the MIT license.
# If you care to read that, here's a link:
# http://opensource.org/licenses/MIT

#USAGE:

# python mailbot.py [-h] [-send_from COMMENTS_FILE_NAME | -comments]

# optional arguments:
#  -h, --help            show this help message and exit
#  -send_from COMMENTS_FILE_NAME
#                        send emails using specified comments file name instead
#                        of downloading attachments
#  -comments             generate comments file

#================================== IMPORTS ===================================
from __future__ import print_function
import sys, re
import email #for accessing email message attributes 
from email.mime.text import MIMEText #used for creating emails from scratch 
import getpass #secure way to get passwords 
from imaplib import IMAP4_SSL #IMAP server functionality for downloading
from smtplib import SMTP_SSL #SMTP server functionality for sending 
#import xml.etree.ElementTree as et
import json
from collections import OrderedDict
from random import choice
import argparse #smart command line argument parsing 

#================================= SET UP =====================================
# Some messages for printing
WELCOME_MESSAGE = '''Welcome to Mailbot, the email attachment collector that \
will make downloading batches of attachments from Gmail extremely easy!\n
If you are ever unsure how to run this program, you can view the help message \
for it by running it with the ``-h" option like so:\n
    python mailbot.py -h
Before proceeding, make sure you are running this from the right directory \
and that you know which folder in your mailbox you want to download the \
attachments from. \n
To begin, please enter the username for the mailbox you would like to login \
to followed by the password for it.'''

FOLDER_REQUEST_FIRST = '''Now enter the folder you wish to select to search \
for messages with attachments.\n *** Case sensitive ***\n'''
   
FOLDER_REQUEST_REPEAT = '''Seems like the folder "{}" was not found.\nPlease type \
in a new folder name. Don't forget that it's case sensitive\n'''

EXIT_CLAUSE = '''If you wish to exit, type "exit" sans quotes now.\n If you \
want to give it another go, simply hit ENTER.\n'''

GREETINGS = ['Hi', 'Hello', 'Greetings',]
SETTINGS = {'incoming': (IMAP4_SSL,("imap.gmail.com", 993)), 'outgoing':
        (SMTP_SSL, ("smtp.gmail.com", 465))}

# some connection defaults
SERVERNAME = "imap.gmail.com" # should be changeable to any imap server name 
PORT = 993 # change only if server uses custom SSL port 

# regex for extracting email addresses:
address = re.compile('[^<]*@[^>]*')
name = re.compile('([^<]*)<')

#=========================== Server Setup Functions ================================

def ask_for_uname():
    return raw_input('Please enter your username, then hit Enter:\n')

def ask_for_password():
    return getpass.getpass('Now please enter your password and hit Enter:\n')

def setup_server(direction):
    loggedIn = False
    print(WELCOME_MESSAGE)
    #print('Starting up a connection...')
    (protocol, ServerAndPort) = SETTINGS[direction]
    server = protocol(*ServerAndPort)
    while not loggedIn:
        # ask for credentials
        user = ask_for_uname()
        pw = ask_for_password()
        print('Attempting to authenticate...')
        try:
            print('logging into server')
            server.login(user, pw)
            loggedIn = True 
            print("Authentication successful. We're in!!")
        except Exception as e:
            print(e)
            print('Authentication failed :( \nPlease try again.')
            leave = raw_input(EXIT_CLAUSE)
            if leave == 'exit': # if user wishes to exit, do so
                sys.exit()
            continue
    if direction is 'outgoing':
        #when sending emails return also sender address in addition to server
        return (server, user + '@gmail.com')
    return server

def has_selected(serverinst):
    '''expects IMAP4_SSL instance, checks if its state is "selected"'''
    return serverinst.state == 'SELECTED'

#============================ Sending Functions ================================

def is_found(name_match):
    return len(name_match) > 0

def generate_folder_name(string):
    '''very primitive conversion of user input into acceptable mail imap
    formats. very much a developing idea, dunno if will keep it and develop
    further or scrap entirely. '''
    if string == 'inbox':
        return string.capitalize()
    return string

def comments_fname(folder_name):
    return folder_name.replace(' ', '_').lower() + '.json'

def create_submission(email_address):
    return OrderedDict([
        ('email',email_address), 
        ('grade', ' '), ('comment', ' ')])

def get_name(email_field):
    name_match = name.findall(email_field)
    if is_found(name_match):
        return ' ' + name_match[0].strip()
    return ''

def create_email(submission, subject, sign, sender):
    greeting = choice(GREETINGS) + get_name(submission['email']) +','
    grade = 'Here is your grade: '+ submission['grade']
    body = submission['comment']
    signature = sign
    put_together = '\n\n'.join([greeting, grade, body, signature])
    messg = MIMEText(put_together)
    messg['To'] = submission['email']
    messg['Subject'] = subject
    messg['From'] = sender
    return messg

def send_emails_from(comments_fname):
    #set up the server and get sender name
    (auth_server, sender) = setup_server('outgoing') 

    #open file with comments 
    try:
        comments = open(comments_fname)
    except IOError:
        print('No file with the name {} was found, please try again'.format(comments_fname))
        sys.exit()
    
    #establish subject and signature
    subj = raw_input('What would you like the subject of your emails to be?\n')
    sign = raw_input('How would you like to sign your emails? \n')
    
    submissions = json.load(comments) # load comments file 
    for submission in submissions:
        # loop over all submissions
        message = create_email(submission, subj, sign, sender)
        # creating messages
        auth_server.sendmail(sender, message['To'], message.as_string())
        # and sending them


#============================ Downloading Functions ==================================

def is_python_script(filename):
    '''Given a filename (potentially NoneType), check if it's valid (not
    NoneType) and that it ends in ``.py".  For this to work, it is paramount
    for students to make sure their submissions contain an explicit extension.
    Please make sure to stress this in class, since the file extension is
    also important when running the script files.
    '''
    return filename and filename.endswith('.py')

def is_attachment(message):
    '''Given a message subpart, checks whether it is an attachment'''
    return message['Content-Disposition'] and ('attachment' in message['Content-Disposition'])

def download_attachments(create_comments):
    file_counter = 0
    downloaded_files = []
    # set up the server (includes login)
    auth_server = setup_server('incoming') 
    #ask for folder to select
    folder = raw_input(FOLDER_REQUEST_FIRST)
    auth_server.select(folder) # attempt to select specified folder 
    while not has_selected(auth_server):
        #if for some reason the specified folder was not selected...
        folder = generate_folder_name(
                raw_input(FOLDER_REQUEST_REPEAT.format(folder)))
        auth_server.select(folder) #... try again after prompting 
    print('\nSelected folder ``{}", looking at the messages therein.'.format(folder))
    #search for messages
    typ, messgs = auth_server.search(None, 'ALL', 'UNDELETED')
    #turn retrieved object into list of message numbers and loop over it
    messgIDs = messgs[0].split()
    comments = []
    for messageId in messgIDs:
        raw = auth_server.fetch(messageId, '(RFC822)')[1][0][1]
        mail = email.message_from_string(raw)
        return_email = mail['From']
        if mail.is_multipart():
            for submessg in mail.get_payload():
                if is_attachment(submessg):
                    file_name = submessg.get_filename() 
                    if file_name not in downloaded_files:
                        file_counter += 1
                        downloaded_files.append(file_name)
                    with open(file_name, 'wb') as f:
                        f.write(submessg.get_payload(decode=True))
                    print('Created file: {}'.format(file_name))
                    # create a comments entry
                    comments.append(create_submission(return_email))
    if create_comments:
        # once done downloading attachments, dump comments into comments file
        comments_file = comments_fname(folder)
        print('Creating comments file.', comments_file)
        with open(comments_file, 'w') as cfile:
            json.dumps(comments)
            json.dump(comments, cfile, indent=1) # include nicer-looking indentation 
    else:
        print("Just so you know, I did not create a comments file because you didn't request one:")
    print('\nMission accomplished! I downloaded {0} unique files. Ciao :)'.format(file_counter))

#================================= __MAIN__ ===================================

def main():
    # set up some argparse goodness
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-send_from', default=None, metavar='COMMENTS_FILE_NAME',
    help='send emails using specified comments file name instead of downloading attachments')
    group.add_argument('-comments', action='store_true', 
            help='generate comments file')
    args = parser.parse_args()
    if args.send_from: # if we are sending out grades 
        send_emails_from(args.send_from)
    else: # if we are dl-ing submissions 
        download_attachments(args.comments)

#==============================================================================
if __name__ == '__main__':
    main()
