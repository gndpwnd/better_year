# Access google drive for creating, modifying, deleting, and accessing report history
import flask
from flask import Blueprint, render_template, request, current_app, redirect, url_for
from google_api_stuff.drive_funcs import *
from werkzeug.utils import secure_filename
import json
from time import sleep

report_app = Blueprint('report', __name__, template_folder='templates')

@report_app.route('/report')
def report():
    return render_template('report/report.html')

@report_app.route('/report/history')
def history():
    reports = view_history(flask.session['google_token'])
    return render_template('report/history.html', reports=reports)

@report_app.route('/report/delete', methods = ['POST', 'GET'])
def delete():
    if flask.request.method == 'POST':
        # get report id from url param
        report_id = flask.request.args.get('id')

        # delete report submission
        delete_report(flask.session['google_token'], report_id)

    # redirect to history page
    return redirect(url_for('report.history'))

@report_app.route('/report/submit', methods = ['POST', 'GET'])
def handle_data():
    # save data to temporary json file
    if flask.request.method == 'POST':
        user_folder = flask.session['user_folder']
        
        day_summary = request.form.get('day_summary_desc')
        
        # get all workout descriptions
        i = 1
        workout_descriptions = ''
        more_workouts = True
        
        while more_workouts:
            base_name = 'workout_description_'
            elem_name = base_name + str(i)
            # if request contains element name, append to workouts string
            if elem_name in request.form:
                workout_descriptions += request.form[elem_name] + ',\n'
                i += 1
            else:
                more_workouts = False
                break

        # get all meal descriptions
        i = 1
        meal_descriptions = ''
        more_meals = True
        while more_meals:
            base_name = 'meal_description_'
            elem_name = base_name + str(i)
            # if request contains element name, append to workouts string
            if elem_name in request.form:
                meal_descriptions += request.form[elem_name] + ',\n'
                i += 1
            else:
                more_meals = False
                break

        # get all memory topics
        i = 1
        memory_topics = ''
        more_memories = True
        while more_memories:
            base_name = 'memory_topic_'
            elem_name = base_name + str(i)
            # if request contains element name, append to workouts string
            if elem_name in request.form:
                memory_topics += request.form[elem_name] + ',\n'
                i += 1
            else:
                more_memories = False
                break
        
        # get all memory descriptions
        i = 1
        memory_descriptions = ''
        more_memories = True
        while more_memories:
            base_name = 'memory_description_'
            elem_name = base_name + str(i)
            # if request contains element name, append to workouts string
            if elem_name in request.form:
                memory_descriptions += request.form[elem_name] + ',\n'
                i += 1
            else:
                more_memories = False
                break
        
        # get all images
        images = request.files.getlist('image')
        #print(images)

        #print(
        #    day_summary, "\n\n",
        #    workout_descriptions, "\n\n",
        #    meal_descriptions, "\n\n",
        #    memory_topics, "\n\n",
        #    memory_descriptions, "\n\n",
        #    images,
        #)

        # if no images
        if str(images) != "[<FileStorage: '' ('application/octet-stream')>]":
            i = 1
            for image in images:
                save_path = user_folder + "/" + str(i) + '-' + image.filename
                image.save(save_path)
                #print("Image saved to:" + save_path)
                i += 1

        create_report(day_summary, workout_descriptions, meal_descriptions, memory_topics, memory_descriptions, user_folder)
        
        
        # return history page
        return redirect(url_for('report.history'))


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@report_app.route('/report/create', methods = ['POST', 'GET'])
def create():
    # build a form for user input
    return render_template('report/create.html', submission_url=url_for('report.handle_data'))