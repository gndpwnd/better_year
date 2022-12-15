# Access google drive for creating, modifying, deleting, and accessing report history

import io
import os
import flask
from flask import Blueprint, render_template
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials

from google_api_stuff.cal import add_report_submission, delete_report_submission

report_app = Blueprint('report', __name__, template_folder='templates')

@report_app.route('/report')
def report():
    return render_template('report/report.html')

@report_app.route('/report/history')
def history():
    reports = view_history(flask.session['google_token'], flask.session['client_tz'])
    return render_template('report/history.html', reports=reports)

@report_app.route('/report/create', methods = ['POST', 'GET'])
def create():
    # build a form for user input
    return render_template('report/create.html')

@report_app.route('/report/edit', methods = ['POST', 'GET'])
def edit():
    edit_report_id = flask.request.args.get('id')
    data = edit_report(flask.session['google_token'], edit_report_id)
    # auto populate create form with data
    # redirect to create page
    return render_template('report/create.html', data=data)

@report_app.route('/report/delete', methods = ['POST', 'GET'])
def delete():
    if flask.request.method == 'POST':
        # get report id from url param
        report_id = flask.request.args.get('id')

        # delete report submission
        delete_report(flask.session['google_token'], report_id)

    # redirect to history page
    return flask.redirect(flask.url_for('report.history'))

def make_service(token):
    # use token to get calender data
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/drive']
    )

    service = build('drive', 'v3', credentials=creds)

    return service

def get_main_folder_id(service):

    expected_folder_name = 'BetterYear Reports'

    folder = service.files().list(
        q="name='" + expected_folder_name + "'",
        spaces='drive',
        fields='nextPageToken, files(id, name)',
        pageToken=None
    ).execute()

    folder_id = ""

    try:
        folder_name = folder['files'][0]['name']
        if folder_name == expected_folder_name:
            folder_id = folder['files'][0]['id']
    except:
        pass

    if folder_id == "":
        # make folder
        file_metadata = {
            'name': expected_folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = service.files().create(body=file_metadata, fields='id').execute()

        folder_id = file.get("id")

    return folder_id

def conv_ctime_to_tz(ctime, tz):
    # convert createdTime to given timezone
    # timezone is number of hours from UTC
    ctime_d = ctime.split('T')[0].replace('-', '/')
    ctime_hr = ctime.split('T')[1].split('.')[0]

    ctime_hr = ctime_hr.split(':')
    ctime_hr[0] = int(ctime_hr[0]) + int(tz)
    
    # if hour is less than 0, subtract a day
    if ctime_hr[0] < 0:
        ctime_hr[0] = 24 + ctime_hr[0]
        ctime_d = ctime_d.split('/')
        ctime_d[2] = str(int(ctime_d[2]) - 1)
        ctime_d = '/'.join(ctime_d)
    elif ctime_hr[0] > 23:
        ctime_hr[0] = ctime_hr[0] - 24
        ctime_d = ctime_d.split('/')
        ctime_d[2] = str(int(ctime_d[2]) + 1)
        ctime_d = '/'.join(ctime_d)

    # if am or pm
    if ctime_hr[0] >= 12:
        ctime_hr = ':'.join([str(x) for x in ctime_hr]) + " PM"
    elif ctime_hr[0] < 12:
        ctime_hr = ':'.join([str(x) for x in ctime_hr]) + " AM"

    return ctime_d + " " + ctime_hr

def get_files_in_folder(service, folder_id, tz):
    # get files in folder that is in main folder
    files = service.files().list(
        q="'" + str(folder_id) + "' in parents",
        spaces='drive',
        fields='nextPageToken, files(id, name, createdTime)',
        pageToken=None
    ).execute()

    file_ids = []
    file_names = []
    file_dates = []
    file_links = []
    
    for file in files['files']:
        file_ids.append(file['id'])

        file_names.append(file['name'])

        ctime = file['createdTime']
        ctime = conv_ctime_to_tz(ctime, tz)
        file_dates.append(ctime)

        f_lnk = "https://drive.google.com/file/d/" + file['id'] + "/view?usp=sharing"
        file_links.append(f_lnk)

    return file_ids, file_names, file_dates, file_links

def view_history(token, tz):
    
    service = make_service(token)
    main_folder_id = get_main_folder_id(service)
    
    # get files in main folder
    file_ids, file_names, file_dates, file_links = get_files_in_folder(service, main_folder_id, tz)

    reports = []
    for i in range(len(file_names)):
        reports.append([file_ids[i], file_names[i], file_dates[i], file_links[i]])
        # organize reports by date
        reports.sort(key=lambda x: x[1], reverse=False)

    return reports

# create a report

def upload_report(token, report_name, meals, workouts, memories,):
    service = make_service(token)
    main_folder_id = get_main_folder_id(service)

    # create google doc in main folder
    file_metadata = {
        'name': report_name,
        'parents': [main_folder_id],
        'mimeType': 'application/vnd.google-apps.document'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()

    doc_id = file.get("id")

    # upload text to doc
    text = "Report: " + report_name
    text = text.encode('utf-8')
    media = MediaIoBaseUpload(io.BytesIO(text), mimetype='text/plain')
    service.files().update(fileId=doc_id, media_body=media).execute()

# edit a report

def edit_report(token, report_id):
    # auto populate create report form with report data
    service = make_service(token)
    report = service.files().get(fileId=report_id).execute()

    report_name = report['name']

    # get text from doc
    request = service.files().export_media(fileId=report_id, mimeType='text/plain')
    text = request.execute().decode('utf-8')

    # get meals, workouts, memories
    meals = []
    workouts = []
    memories = []

    return report_name, meals, workouts, memories

def delete_report(token, report_id):
    service = make_service(token)
    service.files().delete(fileId=report_id).execute()