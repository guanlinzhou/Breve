from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
import os
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'C:/Users/Eric/Documents/CalHacks18/client_id.json'
APPLICATION_NAME = 'Google Calendar API Quickstart'
credential_path = 'C:/Users/Eric/Documents/CalHacks18/'


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    store = file.Storage('C:/Users/Eric/Documents/CalHacks18/client_secret.json')
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def pushToCal(e):
    credentials = get_credentials()
    http = credentials.authorize(Http())
    service = build('calendar', 'v3', http=http)
    name = e['name']
    time = e['time']
    location = e['location']
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    minute = time.minute
    second = time.second
    event = {
  'summary': 'Meet with {}'.format(name),
  'location': location,
  'description': 'Sample Event',
  'start': {
    'dateTime': '{}-{}-{}T{}:{}:{}-08:00'.format(year, month, day, hour, minute, second),
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': '{}-{}-{}T{}:{}:{}-08:00'.format(year, month, day, hour + 1, minute, second),
    'timeZone': 'America/Los_Angeles',
  },

  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(event)



SAMPLE_EVENT = {'name' : 'Jonathan Pan', 'time' : datetime.datetime(2018, 11, 7, 22, 0), 'location': "Moffitt Library"}

if __name__ == '__main__':
    main(SAMPLE_EVENT)


#source:
