# Access google drive for generating reports and accessing report history

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
    return render_template('report/history.html')

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
        scopes=['https://www.googleapis.com/auth/tasks']
    )

    service = build('calendar', 'v3', credentials=creds)

    return service

def check_defaults(service):
    folder_name = 'BetterYear Reports'
    first_file_name = 'BetterYear_1.pdf'

    # check if folder exists
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

def view_history(service):

    # get files
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

def create_report(service):

    # create file metadata
    file_metadata = {
        'name': 'report.pdf',
        'mimeType': 'application/pdf'
    }

    # create media object
    media = MediaFileUpload('report.pdf', mimetype='application/pdf')

    # upload file
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # print file id
    print('File ID: %s' % file.get('id'))

def edit_report(service):

    # create file metadata
    file_metadata = {
        'name': 'report.pdf',
        'mimeType': 'application/pdf'
    }

    # create media object
    media = MediaFileUpload('report.pdf', mimetype='application/pdf')

    # upload file
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # print file id
    print('File ID: %s' % file.get('id'))

def delete_report(service):

    # delete file
    service.files().delete(fileId='FILE_ID').execute()

def handler(token, inp):
    service = make_service(token)
    check_defaults(service)
    if inp == 'hist':
        return view_history(service)
    elif inp == 'crea':
        return create_report(service)
    elif inp == 'edit':
        return edit_report(service)
    elif inp == 'dele':
        return delete_report(service)
    elif inp == 'chec':
        pass
    else:
        return 'error'