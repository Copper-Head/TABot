# This program was created by Ilia Kurenkov who decided he was fed up with
# manually downloading batches of email attachments from students, then
# responding to their submissions with comments and grades. The goal of this
# program is to make it so tha its user (an instructor or TA) should only need
# to worry about making the right comments and grades and leave all the menial
# processing to MailBot.
# This program is free and subject to the conditions of the MIT license.
# If you care to read that, here's a link:
# http://opensource.org/licenses/MIT

#================================== IMPORTS ===================================
import sys, re
import email
from email.mime.text import MIMEText
import getpass
from imaplib import IMAP4_SSL
from smtplib import SMTP_SSL
#import xml.etree.ElementTree as et
import json
from collections import OrderedDict
from random import choice

#================================= SET UP =====================================
# Some messages for printing
WELCOME_MESSAGE = '''Welcome to Mailbot, the email attachment collector that 
will make downloading batches of attachments from Gmail extremely easy!\n
Before proceeding, make sure you are running this from the right directory and
that you know which folder in your mailbox you want to download the attachments
from. \n
To begin, please enter the username for the mailbox you would like to login to
followed by the password for it.'''

FOLDER_REQUEST_FIRST = '''Now enter the folder you wish to select to search \
for messages with attachments. Case sensitive.\n'''
   
FOLDER_REQUEST_REPEAT = '''Seems like the folder "{}" was not found.\nPlease type \
in a new folder name. Don't forget that it's case sensitive\n'''

EXIT_CLAUSE = '''If you wish to exit, type "exit" sans quotes now.\n If you \
want to give it another go, simply hit ENTER.\n'''

USAGE_MESSAGE = ''' It seems you forgot to specify an option. 
In case you've forgotten what these are, an explanation of how to run this
program is given below.

This program is generally run the following way:
    ~$ python mailbot.py OPTION [COMMENTS FILE NAME]

OPTION can either be 'download' or 'email'. If it is 'email', COMMENTS FILE
NAME must be specified. It currently will *not* work with the 'download'
option.

Please try to run the program again with your desired option.
'''

GREETINGS = ['Hi', 'Hello', 'Greetings',]
SETTINGS = {'incoming': (IMAP4_SSL,("imap.gmail.com", 993)), 'outgoing':
        (SMTP_SSL, ("smtp.gmail.com", 465))}

# some connection defaults
SERVERNAME = "imap.gmail.com" # should be changeable to any imap server name 
PORT = 993 # change only if server uses custom SSL port 

# regex for extracting email addresses:
address = re.compile('[^<]*@[^>]*')
name = re.compile('([^<]*)<')

#=========================== Boolean Functions ================================

def has_selected(serverinst):
    '''expects IMAP4_SSL instance, checks if its state is "selected"'''
    return serverinst.state == 'SELECTED'

def is_application(message):
    '''checks if message instance is an application'''
    return 'application' in message.get_content_type()

def is_found(name_match):
    return len(name_match) > 0

#============================ Helper Functions ================================

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

def setup_server(direction):
    loggedIn = False
    print(WELCOME_MESSAGE)
    print('Starting up a connection...')
    (protocol, ServerAndPort) = SETTINGS[direction]
    server = protocol(*ServerAndPort)
    while not loggedIn:
        # ask for credentials
        user = raw_input('Please enter your username, then hit Enter:\n')
        pw = getpass.getpass('Now please enter your password and hit Enter:\n')
        print('Attempting to authenticate...')
        try:
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

#============================ Core Functions ==================================

def download_attachments():
    # set up the server (includes login)
    auth_server = setup_server('incoming') 
    #ask for folder to select
    folder = raw_input(FOLDER_REQUEST_FIRST)
    auth_server.select(folder) # attempt to select a folder 
    while not has_selected(server):
        #if for some reason the specified folder was not selected...
        folder = generate_folder_name(
                raw_input(FOLDER_REQUEST_REPEAT.format(folder)))
        auth_server.select(folder) #... try again after prompting 
    print('\nSelected folder {}, looking at messages'.format(folder))
    
    #search for messages
    typ, messgs = server.search(None, 'ALL', 'UNDELETED')
    #turn retrieved object into list of message numbers and loop over it
    messgIDs = messgs[0].split()
    comments = []
    for messageId in messgIDs:
        raw = auth_server.fetch(messageId, '(RFC822)')[1][0][1]
        mail = email.message_from_string(raw)
        return_email = mail['From']
        if mail.is_multipart():
            for submessg in mail.get_payload():
                if is_application(submessg):
                    with open(submessg.get_filename(), 'wb') as f:
                        f.write(submessg.get_payload(decode=True))
                    print('Created file: {}'.format(submessg.get_filename()))
                    # create a comments entry
                    comments.append(create_submission(return_email))
    
    # once done downloading attachments, dump comments into comments file
    print('Creating comments file.', comments_file)
    comments_file = comments_fname(folder)
    with open(comments_file, 'w') as cfile:
        json.dumps(comments)
        json.dump(comments, cfile, indent=1) # include nicer-looking indentation 
    
    print('\nMission accomplished!! Ciao :)')

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

#================================= __MAIN__ ===================================

def main(options):
    '''This is set up to ignore any cmd-line args beyond the second one
    '''
    if not options: # in case no options were passed...
        # enlighten the user about how to use this program
        print(USAGE_MESSAGE)
        sys.exit()
    if options[0] == 'download': # if we are dl-ing submissions 
        download_attachments()
    elif options[0] == 'email': # if we are sending out grades 
        send_emails_from(options[1])

#==============================================================================
if __name__ == '__main__':
    main(sys.argv[1:])
