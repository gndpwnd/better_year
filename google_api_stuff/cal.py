# Access google calendar to make a record of report submission

# there are three calendars:
# 1. macro goals
# 2. micro goals
# 3. report submissions

import datetime
import os.path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

calender_name = 'BetterYear Reports'

def make_service(token):
    # use token to get calender data
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/tasks']
    )

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_cal_id(service):

    # Call calendar API

    # get calender id
    results = service.calendarList().list().execute()
    calendars = results.get('items', [])

    for calender in calendars:
        if calender['summary'] == calender_name:
            calender_id = calender['id']
            break
    
    # if calender is not found, create it
    if calender_id == 0:
        calender = {
            'summary': calender_name
        }
        calender = service.calendarList().insert(body=calender).execute()
        calender_id = calender['id']

    return calender_id

def add_report_submission(token, tz, google_drive_report_link):
    
    service = make_service(token)
    calendar_id = get_cal_id(service)
    today_datetime = datetime.datetime.utcnow().isoformat() + 'Z'

    event = {
            'summary': 'Report Submission',
            'description': 'You can view your report here: ' + google_drive_report_link,
            'start': {
                'dateTime': today_datetime,
                'timeZone': tz,
            },
            'end': {
                'dateTime': today_datetime,
                'timeZone': tz,
            },
        }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()

def delete_report_submission(token, google_drive_report_link):

    service = make_service(token)
    calendar_id = get_cal_id(service)

    # get all events
    events_result = service.events().list(calendarId=calendar_id, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    # find event with matching description
    for event in events:
        if event['description'] == 'You can view your report here: ' + google_drive_report_link:
            event_id = event['id']
            break

    # delete event
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()