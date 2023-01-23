import io
import os
import flask
import shutil
from PIL import Image
import google_api_stuff.acc as acc
from datetime import date
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_api_stuff.cal import add_report_submission, delete_report_submission
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

def drive_service(token):
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)
    return service

def docs_service(token):
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/documents']
    )
    service = build('docs', 'v1', credentials=creds)
    return service

def get_main_folder_id(service):

    folder_name = 'BetterYear Reports'
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false and name='" + folder_name + "'"

    # Search for the folder
    results = service.files().list(q=query,fields="nextPageToken, files(id, name)").execute()
    files = results.get('files', [])

    # Get the folder ID
    if files:
        folder_id = files[0]['id']
        #print(f'Folder ID: {folder_id}')
    #else:
        #print(f'No files found.')

    return folder_id

def get_images_folder_id(service):
    # get images folder id in google drive
    expected_folder_name = 'BetterYear Images'

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
    flask.session['client_tz']
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

def get_files_in_folder(service, folder_id):
    tz =  flask.session['client_tz']
    #print("Timezone: ", tz, "Type: ", type(tz))
    # get files in folder that is in main folder
    files = service.files().list(
        q="'" + str(folder_id) + "' in parents",
        spaces='drive',
        fields='nextPageToken, files(id, name, createdTime)',
        pageToken=None
    ).execute()
    
    file_ids = []
    file_dates = []
    file_names = []
    file_view_links = []
    file_edit_links = []

    # append details to lists
    for file in files['files']:
        file_ids.append(file['id'])
        file_names.append(file['name'])
        file_dates.append(conv_ctime_to_tz(file['createdTime'], tz))
        file_view_links.append("https://drive.google.com/file/d/" + file['id'] + "/view")
        file_edit_links.append("https://docs.google.com/document/d/" + file['id'] + "/edit")
    return file_ids, file_names, file_dates, file_view_links, file_edit_links

def view_history(token):
    
    service = drive_service(token)
    main_folder_id = get_main_folder_id(service)
    
    # get files in main folder
    file_ids, file_names, file_dates, file_view_links, file_edit_links = get_files_in_folder(service, main_folder_id)   
    reports = []
    for i in range(len(file_names)):
        reports.append([file_ids[i], file_names[i], file_dates[i], file_view_links[i], file_edit_links[i]])
        # organize reports by date (latest report is shown first)
        reports.sort(key=lambda x: x[1], reverse=True)

    return reports

def delete_report(token, report_id):
    service = drive_service(token)
    # delete report from calendar
    try:
        delete_report_submission(token, flask.session['client_tz'], report_id)
    except:
        pass
    # delete report from google drive
    service.files().delete(fileId=report_id).execute()

# build a report

def build_report(token, day_summary, workout_descriptions, meal_descriptions, memory_topics, memory_descriptions):
    service = drive_service(token)

    desc_delimeter = ","

    # get number of previous reports from history
    folder_id = get_main_folder_id(service)
    results = service.files().list(q=f"'{folder_id}' in parents", fields='nextPageToken, files(id, name)').execute()
    num_files = len(results.get('files', []))
    report_name = "Better Year #" + str(num_files + 1)


    # get current date
    now = date.today()
    dob = acc.get_birthday(flask.session['google_token'])
    report_title = dob + "\nDate: " + str(now)

    # get summary data
    summary = day_summary

    # get workout data
    workout_str = ""
    workout_split = workout_descriptions.split(desc_delimeter)
    for workout in workout_split:
        workout_str += workout + "\n"

    # get meal data
    meals_str = ""
    meal_split = meal_descriptions.split(desc_delimeter)
    for meal in meal_split:
        meals_str += meal + "\n"
    
        
    # get memory data
    memory_str = ""
    memory_topic_spilt = memory_topics.split(desc_delimeter)
    memory_description_split = memory_descriptions.split(desc_delimeter)
    for i in range(len(memory_topic_spilt)):
        memory_str += memory_topic_spilt[i] + "\n" + memory_description_split[i] + "\n"

    # build report from json data
    report = (
        "\nReport: " +
        str(report_title) +
        "\n\nSummary:\n\n" +
        str(summary) +
        "\n\nMeals:\n" +
        str(meals_str) +
        "Workouts:\n" +
        str(workout_str) +
        "Memories:\n" +
        str(memory_str) +
        "Images:\n"
        )

    return report_name, report

# init report

def init_report(token, report_name):
    service = drive_service(token)
    main_folder_id = get_main_folder_id(service)

    # create google doc in main folder
    file_metadata = {
        'name': report_name,
        'parents': [main_folder_id],
        'mimeType': 'application/vnd.google-apps.document'
    }
    file_base = service.files().create(body=file_metadata, fields='id').execute()

    doc_id = file_base.get("id")
    # return report link
    report_link = "https://drive.google.com/file/d/" + doc_id + "/view?usp=sharing"

    return doc_id, report_link

# add images to report

def get_aspect_ratio(image_path):
    im = Image.open(image_path)
    width, height = im.size
    aspect_ratio = width / height
    # round to nearest hundreth
    aspect_ratio = round(aspect_ratio, 3)
    return aspect_ratio

def add_images_to_report(token, document_id, user_folder):
    built_drive_service = drive_service(token)
    built_docs_service = docs_service(token)

    images_folder_id = get_images_folder_id(built_drive_service)

    # insert images into report
    local_images = os.listdir(user_folder)
    
    # if no images in folder

    if local_images:
        for image in local_images:
            # get full path to image
            image_path = user_folder + "/" + image
            aspect_ratio = get_aspect_ratio(image_path)
            #print("Using aspect ratio: ", aspect_ratio)

            # get image mime type
            mimeType = ""
            if image.endswith(".png"):
                mimeType = "image/png"
            elif image.endswith(".jpg"):
                mimeType = "image/jpeg"
            elif image.endswith(".jpeg"):
                mimeType = "image/jpeg"
            elif image.endswith(".gif"):
                mimeType = "image/gif"
            elif image.endswith(".bmp"):
                mimeType = "image/bmp"
            elif image.endswith(".svg"):
                mimeType = "image/svg+xml"
            elif image.endswith(".webp"):
                mimeType = "image/webp"

            # Read the image file and convert it to a MediaIoBaseUpload object
            with io.open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                media = MediaIoBaseUpload(io.BytesIO(image_data), mimetype=mimeType,chunksize=1024*1024, resumable=True)
            
            if images_folder_id:
                # Upload the image file to the folder

                # Get image name
                image_name = image_path.split("/")[-1]
                if not image_name:
                    image_name = image_path.split("\\")[-1]

                # Get metadata
                file_metadata = {'name': image_name,'parents': [images_folder_id]}
                upfile = built_drive_service.files().create(body=file_metadata, media_body=media, fields='id, webContentLink').execute()
                #print(F'File ID: {upfile.get("id")}')

                # Make image publicly accessable
                built_drive_service.permissions().create(fileId=upfile.get("id"), body={'role': 'reader', 'type': 'anyone'}).execute()

                # Get the image's link
                file_link = built_drive_service.files().get(fileId=upfile.get("id"), fields='webContentLink').execute().get('webContentLink')
                #print(F'File Link: {file_link}')

                # Insert new lines between images
                requests = [
                    {
                        'insertText': {
                            'text': '\n\n',
                            'location': {
                                'index': 1,
                            }
                        }
                    },
                ]
                result = built_docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

                

                # Calculate necessary height & round to nearest whole number
                width = int(flask.session['image_width'])
                #print("width: ", width, "type: ", type(width))
                height = width / aspect_ratio
                height = round(height, 0)

                # Insert Image On Last Line
                new_requests = [
                    {
                        'insertInlineImage': {
                            'objectSize': {
                                'width': {
                                    'magnitude': width,
                                    'unit': 'PT'
                                },
                                'height': {
                                    'magnitude': height,
                                    'unit': 'PT'
                                },
                            },
                            'uri': file_link,
                            'location': {
                                'segmentId': '',
                                'index': 1,
                            }
                        }
                    }
                ]

                new_result = built_docs_service.documents().batchUpdate(documentId=document_id, body={'requests': new_requests}).execute()
                #print(new_result)
                #print(F'Inserted image into document with ID: {document_id}')


        # remove images from uploads directory
        for image in local_images:
            image_path = user_folder + "/" + image
            os.remove(image_path)

# upload a report build

def upload_report(token, doc_id, report):
    built_docs_service = docs_service(token)

    # upload text to doc
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': '\n',
            }
        },
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': report,
            }
        }
    ]
    result = built_docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
    #print(f'Text uploaded to document with ID: {doc_id}')
   
def create_report(day_summary, workout_descriptions, meal_descriptions, memory_topics, memory_descriptions, user_folder):
    token = flask.session['google_token']
    username = flask.session['user_name']

    # build report
    #print("Building report...")
    report_name, report = build_report(token, day_summary, workout_descriptions, meal_descriptions, memory_topics, memory_descriptions)

    # init report
    #print("Initializing report...")
    doc_id, report_link = init_report(token, report_name)
    
    # insert images into report
    #print("Inserting images...")
    add_images_to_report(token, doc_id, user_folder)

    # upload report
    #print("Uploading report...")
    upload_report(token, doc_id, report)

    # add report to calendar
    #print("Adding report to calendar...")
    add_report_submission(token, flask.session['client_tz'], report_link)

