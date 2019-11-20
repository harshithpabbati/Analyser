import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import re
import time
import dateutil.parser as parser
from datetime import date, datetime, timedelta
import csv

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
store = file.Storage('credentials.json') 
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))
user_id =  'me'
print("Enter date (dd-mm-yyyy)")
date = input()
Subject = "[foss-2019] Status Update [" + date + "]"

msgs = GMAIL.users().messages().list(userId='me',q=Subject).execute()

mssg_list = msgs['messages']
csvData = []
csvData.append(['email_id', 'no_of_words'])
for msg in mssg_list:
    msg = GMAIL.users().messages().get(userId=user_id, id=msg['id']).execute()
    header_data = msg["payload"]["headers"]
    for data in header_data:
        if "From" == data["name"]:
            email_id = data["value"]
            if '<' in email_id:
                start = email_id.find('<')
                end = email_id.find('>')
                email_id = email_id[start + 1: end]

    MsgB64 = msg["payload"]['parts'][0]['body']['data'].replace("-", "+").replace("_", "/")
    Msg = base64.b64decode(bytes(MsgB64, 'UTF-8')).decode('UTF-8')

    Msg = "<br />".join(Msg.split("\r\n"))
    Msg = Msg.split("wrote:<br /><br />>")[0]
    Msg = Msg.rsplit("On ", 1)[0]
    Msg = Msg.split("-- <br />You received this message")[0]
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(Msg)
    tokens = [w for w in tokens if not w in stop_words]
    words = set(tokens)
    length = len(words)

    csvData.append([
        email_id, length
    ])

with open(date + 'statusupdate.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(csvData)
csvFile.close()
