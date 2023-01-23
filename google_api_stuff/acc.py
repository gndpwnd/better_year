# access google api for the following:
# 1. Display name
# 2. Get birthday to display (birthday + delta_days) on the home page

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

  
def get_birthday(token):

    # use token to get birthday
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/user.birthday.read']
    )

    service = build('people', 'v1', credentials=creds)

    # Call the People API
    results = service.people().get(
        resourceName='people/me',
        personFields='birthdays'
    ).execute()
    birthdays = results.get('birthdays', [])

    if not birthdays:
        return 'No birthdays found.'
    else:
        bdate = birthdays[1]['date']
        month = bdate['month']
        day = bdate['day']

        today = date.today()

        # check if birthday is today
        dob = 0
        if not (today.month == month and today.day == day):
            # calculate days from last birthday
            d0 = date(today.year, today.month, today.day)
            d1 = date(today.year, month, day)
            delta = d0 - d1
            dob = delta.days
        
        if dob == 0:
            return "BDAY!!!"
        else:
            return "BDAY + " + str(dob)
