#!/usr/bin/python

import email
import imaplib
import smtplib
import ssl
import sqlite3
from datetime import datetime
import time
import sys

roommates_list = []
sender_email = ""
password = ""


# send an email with the string 'message' to every email address in 'receiver_list'
def send_email(receiver_list, message):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    context = ssl.create_default_context()
    for receiver_email in receiver_list:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


# receive a list of every email & its sender
# returns [], [] when inbox is empty
def receive_mail():
    SERVER = 'imap.gmail.com'

    # output lists
    output_senders = []
    output_messages = []

    # connect to the server and go to the inbox
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(sender_email, password)
    mail.select('inbox')

    # get a list of of every email in the inbox
    status, data = mail.search(None, 'ALL')

    # the information returned in search is a character string,
    # so convert it to a list
    mail_ids = []
    for block in data:
        mail_ids += block.split()

    for i in mail_ids:

        # get the email data from the id
        status, data = mail.fetch(i, '(RFC822)')

        # find the tuple in the email data (there's a lot of useless stuff)
        for response_part in data:
            # so if its a tuple...
            if isinstance(response_part, tuple):

                # receive the message info from the second element
                message = email.message_from_bytes(response_part[1])

                # collect the sender & subject of the message
                mail_from = message['from']
                # mail_subject = message['subject']

                # see if the email has unique content (images, html, etc.)
                if message.is_multipart():
                    mail_content = ''

                    for part in message.get_payload():
                        # only return the plaintext from the email body to the user
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    # if the message isn't multipart, just extract it
                    mail_content = message.get_payload()

                # clean up the input...
                # only read the first line
                mail_content = mail_content.split("\n")[0]
                # normalize to lower case
                mail_content = mail_content.lower()

                output_senders.append(mail_from)
                output_messages.append(mail_content)

        # mark the email for deletion because we're done with it
        mail.store(i, "+FLAGS", "\\Deleted")

    # remove the emails marked for deletion & close the mailbox
    mail.expunge()
    mail.close()
    mail.logout()

    # return the list of senders & messages
    return output_senders, output_messages


# returns a list of every string in the supplies database, returns [] if empty
def get_data():
    tmp_conn = sqlite3.connect('supplies_data.db')
    supplies = []
    for curr_tup in tmp_conn.execute("SELECT item FROM supplies ORDER BY item ASC").fetchall():
        supplies.append(curr_tup[0])
    tmp_conn.close()
    return supplies


# adds a string to the database
def data_add(element):
    tmp_conn = sqlite3.connect('supplies_data.db')
    tmp_conn.execute("INSERT INTO supplies (item) VALUES (?)", [element])
    tmp_conn.commit()
    tmp_conn.close()


# returns true if the database contains the string
def data_contains(element):
    tmp_conn = sqlite3.connect('supplies_data.db')
    lst = tmp_conn.execute("SELECT * FROM supplies WHERE item=?", [element]).fetchall()
    tmp_conn.close()
    if lst:
        return True
    else:
        return False


# removes an element from the database
def data_delete(element):
    tmp_conn = sqlite3.connect('supplies_data.db')
    tmp_conn.execute("DELETE FROM supplies WHERE item=?", [element])
    tmp_conn.commit()
    tmp_conn.close()


# see if the database is empty
def data_empty():
    tmp_conn = sqlite3.connect('supplies_data.db')
    lst = tmp_conn.execute("SELECT item FROM supplies").fetchall()
    tmp_conn.close()
    if lst:
        return False
    else:
        return True


# sends the list of supplies to all the users
def status_update(subject):
    supplies = get_data()
    output = []
    # add "-" before every element in the list
    for curr in supplies:
        output.append("-" + curr)
    send_email(roommates_list, "Subject: " + subject + "\n" + "".join(output))


if __name__ == "__main__":
    try:
        # Load in the email & password of the email sending bot
        with open(sys.argv[1], "r") as file:
            sender_email, password = file.read().splitlines()

        # Load in the array of users from the 'users.txt' file
        with open(sys.argv[2], "r") as file:
            roommates_list = file.read().splitlines()

        # Establish connection to database
        conn = sqlite3.connect('supplies_data.db')

        # Create a table if none already exists
        if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='supplies';").fetchall():
            conn.execute("CREATE TABLE supplies ( \
                        ID INTEGER PRIMARY KEY AUTOINCREMENT, \
                        item TEXT \
            )")

        # finish with database
        conn.commit()
        conn.close()

        while True:
            # get the list of senders and messages
            senders, messages = receive_mail()

            # if the lists aren't empty & input is received...
            if senders != [] and messages != []:

                # iterate through the inbox...
                for i in range(len(messages)):

                    # normalize the strings if there's a carriage return
                    curr_message = messages[i]

                    # if curr_message not in supplies:
                    if not data_contains(curr_message):
                        # add element to list if not already in & update the users of the change
                        data_add(curr_message)
                        status_update("Item Added")
                    else:
                        # remove element from list if it's already there
                        data_delete(curr_message)
                        status_update("Item Removed")

            # send an email to all users around 10am every day if there's anything to get
            now = datetime.now().time()  # time object
            if now.hour == 9 and now.minute == 0 and 0 <= now.second < 5:
                if not data_empty():
                    status_update("Daily List of Things We Need")

            time.sleep(5)
    except Exception as e:
        # Send the error message as an email to the head user
        send_email(roommates_list[0:1], e)
