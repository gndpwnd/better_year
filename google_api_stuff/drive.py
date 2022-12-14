# Access google drive for generating reports and accessing report history

import flask
from flask import Blueprint, render_template

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

report_app = Blueprint('report', __name__, template_folder='templates')

@report_app.route('/report')
def report():
    return render_template('report/report.html')

@report_app.route('/report/history')
def history():
    return render_template('report/history.html')

@report_app.route('/report/create')
def create():
    return render_template('report/create.html')

@report_app.route('/report/edit')
def edit():
    return render_template('report/edit.html')

@report_app.route('/report/delete')
def delete():
    return render_template('report/delete.html')

def get_token():
    token = flask.session['google_token']
    return token

def view_history():
    # get token from flask session
    token = get_token()

    # get credentials from token
    credentials = google.oauth2.credentials.Credentials(
        token['access_token'],
        refresh_token=token['refresh_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id='FN_CLIENT_ID',
        client_secret='FN_CLIENT_SECRET',
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # create drive service
    drive_service = build('drive', 'v3', credentials=credentials)

    # get files
    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

def create_report():
    # get token from flask session
    token = get_token()

    # get credentials from token
    credentials = google.oauth2.credentials.Credentials(
        token['access_token'],
        refresh_token=token['refresh_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id='FN_CLIENT_ID',
        client_secret='FN_CLIENT_SECRET',
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # create drive service
    drive_service = build('drive', 'v3', credentials=credentials)

    # create file metadata
    file_metadata = {
        'name': 'report.pdf',
        'mimeType': 'application/pdf'
    }

    # create media object
    media = MediaFileUpload('report.pdf', mimetype='application/pdf')

    # upload file
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # print file id
    print('File ID: %s' % file.get('id'))

def edit_report():
    # get token from flask session
    token = get_token()

    # get credentials from token
    credentials = google.oauth2.credentials.Credentials(
        token['access_token'],
        refresh_token=token['refresh_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id='FN_CLIENT_ID',
        client_secret='FN_CLIENT_SECRET',
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # create drive service
    drive_service = build('drive', 'v3', credentials=credentials)

    # create file metadata
    file_metadata = {
        'name': 'report.pdf',
        'mimeType': 'application/pdf'
    }

    # create media object
    media = MediaFileUpload('report.pdf', mimetype='application/pdf')

    # upload file
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # print file id
    print('File ID: %s' % file.get('id'))

def delete_report():
    # get token from flask session
    token = get_token()

    # get credentials from token
    credentials = google.oauth2.credentials.Credentials(
        token['access_token'],
        refresh_token=token['refresh_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id='FN_CLIENT_ID',
        client_secret='FN_CLIENT_SECRET',
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # create drive service
    drive_service = build('drive', 'v3', credentials=credentials)

    # delete file
    drive_service.files().delete(fileId='FILE_ID').execute()