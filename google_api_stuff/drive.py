# Access google drive for creating, modifying, deleting, and accessing report history

import os
import flask
from flask import Blueprint, render_template
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

from google_api_stuff.cal import add_report_submission, delete_report_submission

report_app = Blueprint('report', __name__, template_folder='templates')

@report_app.route('/report')
def report():
    return render_template('report/report.html')

@report_app.route('/report/history')
def history():
    folder_names, reports = view_history(flask.session['google_token'])
    return render_template('report/history.html', folder_names=folder_names, reports=reports)

@report_app.route('/report/create', methods = ['POST', 'GET'])
def create():
    # build a form for user input
    return render_template('report/create.html')

@report_app.route('/report/edit')
def edit():
    return render_template('report/edit.html')

@report_app.route('/report/delete')
def delete():
    return render_template('report/delete.html')

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

def get_files_in_folder(service, folder_id, main_folder_id):
    # get files in folder that is in main folder
    files = service.files().list(
        q="'" + str(folder_id) + "' in parents and '" + str(main_folder_id) + "' in parents",
        spaces='drive',
        fields='nextPageToken, files(id, name)',
        pageToken=None
    ).execute()

    file_ids = []
    file_names = []
    file_dates = []
    file_links = []
    
    for file in files['files']:
        file_ids.append(file['id'])
        file_names.append(file['name'])
        file_dates.append(file['createdTime'])
        file_links.append("https://drive.google.com/file/d/" + file['id'] + "/view?usp=sharing")

    return file_names, file_dates, file_links

def view_history(token):
    
    service = make_service(token)
    main_folder_id = get_main_folder_id(service)
    
    # get folders in main folder

    folders = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and '" + main_folder_id + "' in parents",
        spaces='drive',
        fields='nextPageToken, files(id, name)',
        pageToken=None
    ).execute()

    # get folder ids
    folder_ids = []
    for folder in folders['files']:
        folder_ids.append(folder['id'])

    # get folder names
    folder_names = []
    for folder in folders['files']:
        folder_names.append(folder['name'])

    # get files for every folder
    reports = []
    for folder in range(len(folder_ids)):

        folder_name = folder_names[folder]
        file_names, file_dates, file_links = get_files_in_folder(service, folder, main_folder_id)
        
        for i in range(len(file_names)):
            reports.append([folder_name, [file_dates[i], file_names[i], file_links[i]]])

    return folder_names, reports

# create a report
# edit a report
# delete a report