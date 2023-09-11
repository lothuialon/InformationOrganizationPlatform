from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify


from transformers import pipeline
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from nltk.stem import WordNetLemmatizer
import string
import math
from .models import *
from .auth import *
from .summarizer import *
import nltk
import random
import time



views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template("/index.html")

#---------------------------------------------------------------------------------
@views.route('/userhome', defaults={'folder_id': None})
@views.route('/userhome/<int:folder_id>')
def user_home(folder_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    username = session['username']
    user = get_user(username)

    if user is None:
        return "User not found"

    main_folder_id = user[4]  # Assuming the rootFolderId is stored at index 4
    if folder_id is None:
        folder_data = get_folder(main_folder_id, user[0])
        
    else:
        folder_data = get_folder(folder_id, user[0])

    if folder_data is None:
        return "Folder not found"

    parent_folder_id = folder_data.get('folderParent')
    current_folder_id = folder_data.get('folderId')
    return render_template(
        'user_home.html',
        folder_data=folder_data,
        parent_folder_data=parent_folder_id,
        current_folder=current_folder_id
    )

@views.route('/create_note/<int:folder_id>', methods=['GET', 'POST'])
def create_note_page(folder_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('note.html', folder_id=folder_id)

@views.route('/create_note', methods=['POST'])
def create_notes():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    folder_id = request.form.get('folder_id')
    title = request.form.get('title')
    content = request.form.get('input-text')

    # Code to create the note in the current folder
    note_id = create_note(content, title, folder_id)
    
    #if note_id:
        #flash('Note created successfully.', 'success')
    #else:
        #flash('Failed to create note.', 'error')
    
    return redirect(url_for('views.user_home', folder_id=folder_id))

@views.route('/view_note/<int:noteId>')
def view_note(noteId):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    note_data = get_note_by_id(noteId)  #

    if note_data:
        return render_template('view_note.html', note=note_data)
    else:
        #flash('Note not found', 'error')
        return redirect(url_for('home'))
    
    


@views.route('/delete_note/<int:noteId>', methods=['POST'])
def delete_note(noteId):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    note_data = get_note_by_id(noteId)  
    delete_note_by_id(noteId)

    if note_data:
        return redirect(url_for('views.user_home'))
    else:
        #flash('Note not found', 'error')
        return redirect(url_for('views.user_home'))
    
@views.route('/delete_summarization/<int:summarizationId>', methods=['POST'])
def delete_summarizations(summarizationId):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    summarization_data = get_summarization(summarizationId)
    delete_summarization(summarizationId)

    if summarization_data:
        return redirect(url_for('views.user_home'))
    else:
        #flash('Summarization not found', 'error')
        return redirect(url_for('views.user_home'))
    
@views.route('/delete_extraction/<int:extractionId>', methods=['POST'])
def delete_extractions(extractionId):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    extraction_data = get_summarization(extractionId) 
    delete_extraction(extractionId)

    if extraction_data:
        return redirect(url_for('views.user_home'))
    else:
        #flash('Summarization not found', 'error')
        return redirect(url_for('views.user_home'))
    
@views.route('/delete_folder/<int:folder_id>', methods=['GET', 'POST'])
def delete_folders(folder_id):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    username = session['username']
    user = get_user(username)

    folder_data = get_folder(folder_id, user[0])

    if folder_data:

        for summarization in folder_data['summarizations']:
            delete_summarization(summarization.summarizationId)

        for note in folder_data['notes']:
            delete_note(note['noteId'])

        for extraction in folder_data['keyword_extractions']:
            delete_extraction(extraction.extractionId)
        print("test")

        for folder in folder_data['folders']:
            if len(folder_data['folders']) != 0:
                print(folder)
                delete_folders(folder['folderId'])

        delete_folder(folder_id)

        #flash('Deletion Complete', 'success')
        return redirect(url_for('views.user_home'))
    else:
        #flash('Summarization not found', 'error')
        return redirect(url_for('views.user_home'))
#---
@views.route('/create_folder/<int:folder_id>', methods=['GET', 'POST'])
def create_folder_page(folder_id):
    
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    username = session['username']
    user = get_user(username)

    if user is None:
        return "User not found"

    main_folder_id = user[4]  # Assuming the rootFolderId is stored at index 4
    if folder_id is None:
        folder_data = get_folder(main_folder_id, user[0])
            
    else:
        folder_data = get_folder(folder_id, user[0])

    if folder_data is None:
        return "Folder not found"

    parent_folder_id = folder_data.get('folderParent')
    current_folder_id = folder_data.get('folderId')
    return render_template(
        'create_folder.html',
        folder_data=folder_data,
        parent_folder_data=parent_folder_id,
        current_folder=current_folder_id,
        folder_id=folder_id
     )


@views.route('/create_folder', methods=['POST'])
def create_folders():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    folder_id = request.form.get('folder_id')
    title = request.form.get('title')
    username = session['username']
    user = get_user(username)
    print(folder_id)
    
    folder_id = create_folder(title, folder_id, user[0])
    
    #if folder_id:
        #flash('Folder created successfully.', 'success')
    #else:
        #flash('Failed to create folder.', 'error')
    
    return redirect(url_for('views.user_home', folder_id=folder_id))


@views.route('/view_summarization/<int:summarizationId>')
def view_summarization(summarizationId):
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    summarization_data = get_summarization(summarizationId)  # Implement this function to fetch note data

    if summarization_data:
        return render_template('view_summarization.html', summarization_data=summarization_data)
    else:
        flash('Note not found', 'error')
        return redirect(url_for('home'))


#---------------------------------------------------------------------------------



@views.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

@views.route('/summarize')
def summarizePage():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('summarize.html')


@views.route('/summarize-text', methods=['POST'])
def summarize_text():
    #todo display number of words
    start_time = time.time()
    text = request.json['text']
    length = request.json['count']
    option = int(request.json['option'])

    #variable setting
    num_sentences = 0
    desired_word_count = 0
    keyword_number = 0
    sentences = len(nltk.sent_tokenize(text))
    print(option)
    if option == 1:
        #desired %10-15 of input

        desired_percentage = 0.10  # Adjust the desired percentage as needed

    elif option == 2:

        desired_percentage = 0.20  # Adjust the desired percentage as needed

    elif option == 3:

        desired_percentage = 0.30  # Adjust the desired percentage as needed

    elif option == 4:

        desired_percentage = 0.45  # Adjust the desired percentage as needed

    desired_word_count = length * desired_percentage
    avg_sentence_length = length / sentences
    num_sentences = math.ceil(desired_word_count / avg_sentence_length)
    print("Number of Sentences for Summary:", num_sentences)
    if desired_word_count < 100:
        desired_word_count = 100

    keyword_number = int(length/100)
    print(keyword_number)   
    print(desired_word_count)
    summary1 = summarize(text, num_sentences, length_weight=0.2, position_weight=0.3, keyword_weight=0.05, keyword_number=keyword_number)
    summary2 = abstractiveSummarization(text, desired_word_count)
    #summary = abstractiveSummarization(text)
    end_time= time.time()
    end_time = end_time-start_time
    return jsonify({'summary1': summary1, 'summary2': summary2, 'time': end_time})
    #return summary

@views.route('/save_summarization', methods=['POST'])
def save_summarization():
    data = request.json

    extractive = request.json['output1']
    abstractive = request.json['output2']
    input = request.json['input']
    folder_id = request.json['folder_id']
    title = request.json['title']
    #print(extractive)
    #print(abstractive)
    #text_input, parent_id, extractive_output, abstractive_output
    create_summarization(input, folder_id, extractive, abstractive, title)

    # Process the received data and save the summarization

    # Return a response indicating success

    return jsonify({'message': 'Summarization saved successfully'})

@views.route('/extract')
def extractPage():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    return render_template('extract_keywords.html')

@views.route('/extract-keyword', methods=['POST'])
def extract_keyword():
    text = request.json['text']
    number = int(request.json['number'])

    keywords = extract_keywords(text, number)
    formatted_keywords = '\n'.join(f'Keyword {i+1}: "{keyword}"' for i, keyword in enumerate(keywords))

    return jsonify({'keywords': formatted_keywords})

@views.route('/save_keywords', methods=['POST'])
def save_keywords():
    #data = request.json
    #title = request.json['title']
    output = request.json['output']
    input = request.json['input']
    folder_id = request.json['folder_id']
    title = request.json['title']
    print(title)
    add_extraction(input, folder_id, output, title)
    
    # def add_extraction(text_input, parent_id, output_text):
    #flash('Keywords saved successfully', 'success')
    #     query = "INSERT INTO keywordExtractions (textInput, parentId, outputText) VALUES (%s, %s, %s)"
    return jsonify({'message': 'Keywords saved successfully'})

@views.route('/view_extraction/<int:keywordId>')
def view_extraction(keywordId):
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    extraction_data = get_extraction(keywordId)  # Implement this function to fetch note data

    if extraction_data:
        return render_template('view_extraction.html', extraction_data=extraction_data)
    else:
        #flash('Note not found', 'error')
        return redirect(url_for('home'))
    


