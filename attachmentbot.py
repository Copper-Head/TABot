# This script was created by Ilia Kurenkov who decided he was fed up with
# manually downloading batches of email attachments from students.
# This program is free and subject to the conditions of the MIT license.
# If you care to read that, here's a link:
# http://opensource.org/licenses/MIT

#================================== IMPORTS ===================================
from __future__ import print_function
import sys
from imaplib import IMAP4_SSL #for IMAP server connections 
import email #for accessing email message attributes 
import getpass #secure way to get passwords 

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
for messages with attachments.\n *** Case sensitive ***\n'''
   
FOLDER_REQUEST_REPEAT = '''Seems like the folder ``{}" was not found.\nPlease type \
in a new folder name. Don't forget that it's Case Sensitive\n'''

EXIT_CLAUSE = '''If you wish to exit, type ``exit" sans quotes now.\n If you \
want to give it another go, simply hit ENTER.\n'''

# some connection defaults
SERVERNAME = "imap.gmail.com"   # should be changeable to any imap server name 
PORT = 993                      # change only if server uses custom SSL port 

#=========================== Boolean Functions ================================

def has_selected(serverinst):
    '''expects IMAP4_SSL instance, checks if its state is "selected"'''
    return serverinst.state == 'SELECTED'

def is_python_script(filename):
    '''Given a filename (potentially NoneType), check if it's valid (not
    NoneType) and that it ends in ``.py".  For this to work, it is paramount
    for students to make sure their submissions contain an explicit extension.
    Please make sure to stress this in class, since the file extension is
    also important when running the script files.
    '''
    return filename and filename.endswith('.py')

#============================ Helper Functions ================================

def generate_folder_name(string):
    '''very primitive conversion of user input into acceptable mail imap
    formats. very much a work in progress, dunno if will keep it and develop
    further or scrap entirely. '''
    if string == 'inbox':
        return string.capitalize()
    return string

#================================= __MAIN__ ===================================

def main():
    file_counter = 0
    downloaded_files = []
    loggedIn = False
    print(WELCOME_MESSAGE)
    print('Starting up a connection...')
    server = IMAP4_SSL(SERVERNAME ,PORT)
    while not loggedIn:
        # ask for credentials
        user = raw_input('Please enter your username, then hit Enter:\n')
        pw = getpass.getpass('Now please enter your password and hit Enter:\n')
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
    folder = generate_folder_name(raw_input(FOLDER_REQUEST_MAIN))
    server.select(folder) # attempt to select a folder 
    while not has_selected(server):
        #if for some reason the specified folder was not selected...
        folder = generate_folder_name(
                raw_input(FOLDER_REQUEST_REPEAT.format(folder)))
        server.select(folder) #... try again after prompting 
    print('\nSelected folder ``{}", looking at the messages therein.'.format(folder))
    #search for messages
    typ, messgs = server.search(None, 'ALL', 'UNDELETED')
    #turn retrieved object into list of message numbers and loop over it
    messgIDs = messgs[0].split()
    for messageId in messgIDs:
        raw = server.fetch(messageId, '(RFC822)')[1][0][1]
        mail = email.message_from_string(raw)
        return_email = mail['From']
        if return_email:
            print('Sender: {}'.format(return_email))
        if mail.is_multipart():
            for submessg in mail.get_payload():
                file_name = submessg.get_filename() #NoneType if no filename
                if is_python_script(file_name):
                    if file_name not in downloaded_files:
                        file_counter += 1
                        downloaded_files.append(file_name)
                    with open(file_name, 'wb') as f:
                        f.write(submessg.get_payload(decode=True))
                    print('Created file: {}'.format(file_name))
    print('\nMission accomplished! I downloaded {0} unique files. Ciao :)'.format(file_counter))

#==============================================================================
if __name__ == '__main__':
    main()
