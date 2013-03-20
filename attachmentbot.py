# This script was created by Ilia Kurenkov who decided he was fed up with
# manually downloading batches of email attachments from students.
# This program is free and subject to the conditions of the MIT license.
# If you care to read that, here's a link:
# http://opensource.org/licenses/MIT

#================================== IMPORTS ===================================
import sys
from imaplib import IMAP4_SSL
import email
import getpass

#================================= SET UP =====================================
# Some messages for printing
WELCOME_MESSAGE = '''Welcome to Mailbot, the email attachment collector that 
will make downloading batches of attachments from Gmail extremely easy!\n
Before proceeding, make sure you are running this from the right directory and
that you know which folder in your mailbox you want to download the attachments
from. \n
To begin, please enter the username for the mailbox you would like to login to
followed by the password for it.'''

FOLDER_REQUEST_MAIN = '''Now enter the folder you wish to select to search \
for messages with attachments. Case sensitive.\n'''
   
FOLDER_REQUEST_REPEAT = '''Seems like the folder "{}" was not found.\nPlease type \
in a new folder name. Don't forget that it's case sensitive\n'''

EXIT_CLAUSE = '''If you wish to exit, type "exit" sans quotes now.\n If you \
want to give it another go, simply hit ENTER.\n'''

# some connection defaults
SERVERNAME = "imap.gmail.com" # should be changeable to any imap server name 
PORT = 993 # change only if server uses custom SSL port 

#=========================== Boolean Functions ================================

def has_selected(serverinst):
    '''expects IMAP4_SSL instance, checks if its state is "selected"'''
    return serverinst.state == 'SELECTED'

def is_application(message):
    '''checks if message instance is an application'''
    return 'application' in message.get_content_type()

#============================ Helper Functions ================================

def generate_folder_name(string):
    '''very primitive conversion of user input into acceptable mail imap
    formats. very much a developing idea, dunno if will keep it and develop
    further or scrap entirely. '''
    if string == 'inbox':
        return string.capitalize()
    return string

#================================= __MAIN__ ===================================

def main():
    loggedIn = False
    print(WELCOME_MESSAGE)
    print('Starting up a connection...')
    server = IMAP4_SSL(SERVERNAME ,PORT)
    while not loggedIn:
        # ask for credentials
        #user = raw_input('Please enter your username, then hit Enter:\n')
        #pw = getpass.getpass('Now please enter your password and hit Enter:\n')
        user, pw = 'ilia.kurenkov', 'bow2Googletheallknowing'
        print('Attempting to authenticate...')
        try:
            server.login(user, pw)
            loggedIn = True 
            print("We're in!!")
        except Exception as e:
            print(e)
            print(':( \nPlease try again.')
            leave = raw_input(EXIT_CLAUSE)
            if leave == 'exit': # if user wishes to exit, do so
                sys.exit()
            continue
    #folder = generate_folder_name(raw_input(FOLDER_REQUEST_MAIN))
    folder = 'HAS FILES'
    server.select(folder) # attempt to select a folder 
    while not has_selected(server):
        #if for some reason the specified folder was not selected...
        folder = generate_folder_name(
                raw_input(FOLDER_REQUEST_REPEAT.format(folder)))
        server.select(folder) #... try again after prompting 
    print('\nSelected folder {}, looking at messages'.format(folder))
    #search for messages
    typ, messgs = server.search(None, 'ALL', 'UNDELETED')
    #turn retrieved object into list of message numbers and loop over it
    messgIDs = messgs[0].split()
    for messageId in messgIDs:
        raw = server.fetch(messageId, '(RFC822)')[1][0][1]
        mail = email.message_from_string(raw)
        return_email = mail['Return-Path']
        print return_email
        if mail.is_multipart():
            for submessg in mail.get_payload():
                if is_application(submessg):
                    with open(submessg.get_filename(), 'wb') as f:
                        f.write(submessg.get_payload(decode=True))
                    print('Created file: {}'.format(submessg.get_filename()))
    print('\nMission accomplished!! Ciao :)')

#==============================================================================
if __name__ == '__main__':
    main()
