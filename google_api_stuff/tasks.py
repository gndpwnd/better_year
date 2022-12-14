# 1. Get the list of current macro goals from specific google tasks list
# 2. Get the list of current micro goals from specific google tasks list
    # - today
    # - this week

# display macro on left side of page
# display micro on right side of page

import flask
from flask import Flask, Blueprint, render_template
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import date

goals_app = Blueprint('goals', __name__, template_folder='templates')

@goals_app.route('/goals')
def goals():
    return render_template(
        'goals/goals.html',
        macro = get_macro(flask.session['google_token']),
        micro = get_micro(flask.session['google_token']),
        ) 

def get_macro(token):
    # use token to get macro goals task list
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/tasks']
    )

    service = build('tasks', 'v1', credentials=creds)

    # Call tasks API

    # get macro goals task list
    results = service.tasklists().list().execute()
    tasklists = results.get('items', [])

    # get macro goals task list id
    macro_tasks_list_id = 0
    for tasklist in tasklists:
        if tasklist['title'] == 'Macro Goals':
            macro_tasks_list_id = tasklist['id']
            break
    
    # if macro goals task list is not found, create it
    if macro_tasks_list_id == 0:
        tasklist = {
            'title': 'Macro Goals'
        }
        tasklist = service.tasklists().insert(body=tasklist).execute()
        macro_tasks_list_id = tasklist['id']
    
    # if macro goals task list is found, get tasks
    results = service.tasks().list(tasklist=macro_tasks_list_id).execute()
    tasks = results.get('items', [])

    # if no tasks are found, create a task
    if not tasks:
        task = {
            'title': 'Create a macro goal!'
        }
        task = service.tasks().insert(tasklist=macro_tasks_list_id, body=task).execute()

    # if default task is found, and there are 2 tasks, delete the default task
    if len(tasks) == 2:
        title = tasks[0]['title']
        if title == 'Create a macro goal!':
            # delete the task
            service.tasks().delete(tasklist=macro_tasks_list_id, task=tasks[0]['id']).execute()

    # get tasks again
    tasks = service.tasks().list(tasklist=macro_tasks_list_id).execute().get('items', [])

    # return tasks
    return tasks

def get_micro(token):
    # use token to get micro goals task list
    creds = Credentials(
        token=token['access_token'],
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=os.environ.get('FN_CLIENT_ID'),
        client_secret=os.environ.get('FN_CLIENT_SECRET'),
        scopes=['https://www.googleapis.com/auth/tasks']
    )

    service = build('tasks', 'v1', credentials=creds)

    # Call tasks API

    # get micro goals task list
    results = service.tasklists().list().execute()
    tasklists = results.get('items', [])

    # get micro goals task list id
    micro_tasks_list_id = 0
    for tasklist in tasklists:
        if tasklist['title'] == 'Micro Goals':
            micro_tasks_list_id = tasklist['id']
            break
    
    # if micro goals task list is not found, create it
    if micro_tasks_list_id == 0:
        tasklist = {
            'title': 'Micro Goals'
        }
        tasklist = service.tasklists().insert(body=tasklist).execute()
        micro_tasks_list_id = tasklist['id']
    
    # if micro goals task list is found, get tasks
    results = service.tasks().list(tasklist=micro_tasks_list_id).execute()
    tasks = results.get('items', [])

    # if no tasks are found, create a task
    if not tasks:
        task = {
            'title': 'Create a micro goal!'
        }
        task = service.tasks().insert(tasklist=micro_tasks_list_id, body=task).execute()

    # if default task is found, and there are 2 tasks, delete the default task
    if len(tasks) == 2:
        title = tasks[0]['title']
        if title == 'Create a micro goal!':
            # delete the task
            service.tasks().delete(tasklist=micro_tasks_list_id, task=tasks[0]['id']).execute()

    # get tasks again
    tasks = service.tasks().list(tasklist=micro_tasks_list_id).execute().get('items', [])

    # return tasks
    return tasks