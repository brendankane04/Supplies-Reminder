# Supplies Reminder

Supplies Reminder is a program designed to function as a list of items routinely & conveniently sent to a list of users via email. 
The primary use of this is for people who share a living space to know what shared items need to be bought. 

This list of supplies can be added to by simply sending an email to the designated email address & 
any element in the list can be removed by simply emailing the name of the object as it appears in the list.


![Adding an Object to the List](/Example_Use.PNG)

this list is emailed to every user daily, so no one will forget what is needed on the list.

This program is written to be run on a server you own. This includes a raspberry pi.

# Example Use

If you run this line in the console with the .txt files formatted as described, 
the program should work correctly, in the background. 

**For Linux:**
`python supplies_reminder.py sender_info.txt users.txt &`

**For Windows:**
`start /b python.exe supplies_reminder.py sender_info.txt users.txt`

## The Files

All the files are line separated. Examples of the files are included in the original version of this project.

**supplies_manager.py:** the main source file. Run it to activate the program.

**sender_info.txt:** This file has the email address of the gmail account the emails are sent from & its password
ensure that the gmail account has "less secure app access" on or else you'll get authentication errors

**users.txt:** This file is the list of every email address the list will be emailed to. 
By using phone numbers according to the [following format](https://www.techwalla.com/articles/how-to-send-a-text-message-from-email) 
the program can send & receive text messages instead of emails. 
It changes based on the carrier, so it doesn't always work.