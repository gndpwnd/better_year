# 1. Get the list of current macro goals from specific google tasks list
# 2. Get the list of current micro goals from specific google tasks list
    # - today
    # - this week

# display macro on left side of page
# display micro on right side of page

import datetime
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
        macro_goals = list_macro_goals(flask.session['google_token']),
        micro_goals = list_micro_goals(flask.session['google_token']),
    ) 

def add_macro_goal(token):
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
    
    # get user input
    new_task_title = flask.request.form['macro_goal']
    due = flask.request.form['macro_due']

    # create task
    task = {
        'title': new_task_title,
        'due': due,
    }

    # add task to macro goals task list
    task = service.tasks().insert(tasklist=macro_tasks_list_id, body=task).execute()

def add_micro_goal(token):
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
    
    # get user input
    new_task_title = flask.request.form['micro_goal']
    due = flask.request.form['micro_due']

    # create task
    task = {
        'title': new_task_title,
        'due': due,
    }

    # add task to micro goals task list
    task = service.tasks().insert(tasklist=micro_tasks_list_id, body=task).execute()

def list_macro_goals(token):
    
    macro_task_titles = []

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
    # parse tasks
    for task in tasks:
        status = task['status']
        if status == 'needsAction':
            title = task['title']
            if title not in macro_task_titles:
                macro_task_titles.append(title)
        
    # if no tasks are found, create a task
    if not tasks:
        task = {
            'title': 'Create a macro goal!'
        }
        task = service.tasks().insert(tasklist=macro_tasks_list_id, body=task).execute()

     # if default task is found, and there are 2 tasks, delete the default task
    if len(tasks) == 2:
        for titles in tasks:
            title = titles['title']
            if title == 'Create a macro goal!':
                # delete the task
                service.tasks().delete(tasklist=macro_tasks_list_id, task=titles['id']).execute()
    
    # get tasks again
    results = service.tasks().list(tasklist=macro_tasks_list_id).execute()
    tasks = results.get('items', [])
    # parse tasks
    for task in tasks:
        status = task['status']
        if status == 'needsAction':
            title = task['title']
            if title not in macro_task_titles:
                macro_task_titles.append(title)

    # return tasks
    return macro_task_titles

def list_micro_goals(token):

    micro_tasks_titles = []

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
    # parse tasks
    for task in tasks:
        status = task['status']
        if status == 'needsAction':
            title = task['title']
            if title not in micro_tasks_titles:
                micro_tasks_titles.append(title)

    # if no tasks are found, create a task
    if not tasks:
        task = {
            'title': 'Create a micro goal!'
        }
        task = service.tasks().insert(tasklist=micro_tasks_list_id, body=task).execute()

    # if default task is found, and there are 2 tasks, delete the default task
    if len(tasks) == 2:
        for titles in tasks:
            title = titles['title']
            if title == 'Create a micro goal!':
                # delete the task
                service.tasks().delete(tasklist=micro_tasks_list_id, task=titles['id']).execute()
    
    # get tasks again
    # if micro goals task list is found, get tasks
    results = service.tasks().list(tasklist=micro_tasks_list_id).execute()
    tasks = results.get('items', [])
    # parse tasks
    for task in tasks:
        status = task['status']
        if status == 'needsAction':
            title = task['title']
            if title not in micro_tasks_titles:
                micro_tasks_titles.append(title)

    # return tasks
    return micro_tasks_titles

