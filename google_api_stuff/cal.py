# Access google calendar to make a record of report submission
# Link to report in google drive

import datetime
import os.path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

expected_calendar_name = 'BetterYear Reports'

timzezones_dict = {
    "-12": "Etc/GMT+12",
    "-11": "Pacific/Midway",
    "-10": "Pacific/Honolulu",
    "-9": "America/Anchorage",
    "-8": "America/Los_Angeles",
    "-7": "America/Denver",
    "-6": "America/Mexico_City",
    "-5": "America/New_York",
    "-4": "America/Caracas",
    "-3": "Argentina/Buenos_Aires",
    "-2": "Atlantic/Azores",
    "-1": "Atlantic/Azores",
    "0": "Europe/London",
    "1": "Europe/Paris",
    "2": "Europe/Helsinki",
    "3": "Europe/Moscow",
    "4": "Asia/Baku",
    "5": "Asia/Karachi",
    "6": "Asia/Dhaka",
    "7": "Asia/Bangkok",
    "8": "Asia/Singapore",
    "9": "Asia/Tokyo",
    "10": "Australia/Sydney",
    "11": "Pacific/Guadalcanal",
    "12": "Pacific/Auckland",
}

def make_service(token):
    # use token to get calendar data
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/tasks']
    )

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_cal_id(service, tz):

    calendar_id = ""

    page_token = None

    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == expected_calendar_name:
                calendar_id = calendar_list_entry['id']
                break
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    if calendar_id == "":
        calendar = {
            'summary': expected_calendar_name,
            'timeZone': timzezones_dict[tz],
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = created_calendar['id']

    return calendar_id

def add_report_submission(token, tz, google_drive_report_link):
    
    service = make_service(token)
    calendar_id = get_cal_id(service, tz)
    today_datetime = datetime.datetime.utcnow().isoformat() + 'Z'

    #print("Link: ", google_drive_report_link)
    event = {
            'summary': 'Report Submission',
            'description': 'You can view your report <a href="' + google_drive_report_link + '">here</a>.',
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

def delete_report_submission(token, tz, doc_id):

    service = make_service(token)
    calendar_id = get_cal_id(service, tz)

    # get all events
    #print("Collecting events")
    events_result = service.events().list(calendarId=calendar_id, 
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    event_id = ""
    # find event with matching document id in link in description
    #print("Link: ", doc_id)
    for event in events:
        event_id = ""
        #print("Description:", event['description'])
        if doc_id in event['description']:
            #print("MATCH FOUND!!!")
            event_id = event['id']
            if event_id == "":
                #print("Event not found #2")
                return
            else:
                # delete event
                service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
                #print("Event deleted")
                break
        else:
            continue
            #print("Event not found #1")