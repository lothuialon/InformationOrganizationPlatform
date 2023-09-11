from flask import Flask, request, redirect, url_for, session, render_template
import mysql.connector

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="platformdb"
)
# USER FUNCTIONS------------------------------------------
# Function to check if a user exists in the database
def user_exists(username):
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    return result is not None

# Function to get a user from the database

def get_user(username):
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    return result

def get_user_by_email(email):
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE emailAddress = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    print(result[0])
    return result[0] if result else None

def update_password_by_email(email, new_password):
    id = get_user_by_email(email)
    print(id)
    cursor = db.cursor()
    query = "UPDATE users SET password = %s WHERE id = %s"
    values = (new_password, id)
    cursor.execute(query, values)
    db.commit()

def remove_code(code):
    cursor = db.cursor()
    query = "DELETE FROM code WHERE code = %s"
    cursor.execute(query, (code,))
    db.commit()

def get_email_by_code(code):
    cursor = db.cursor()
    query = "SELECT * FROM code WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    return result[2] if result else None

# Function to validate a user's login credentials
def validate_login(username, password):
    user = get_user(username)
    if user is None:
        return False
    else:
        return password == user[2]
    
# Function to register an user
def add_user(username, password, email):
    cursor = db.cursor()
    query = "INSERT INTO users (username, password, emailAddress) VALUES (%s, %s, %s)"
    values = (username, password, email)
    cursor.execute(query, values)
    db.commit()

    # Create a main folder for the user
    user_id = cursor.lastrowid
    main_folder_id = create_folder("Main Folder", None, user_id)

    # Update the rootFolderId in the users table
    update_user_root_folder(user_id, main_folder_id)

    return username

# Function to update the rootFolderId for a user
def update_user_root_folder(user_id, root_folder_id):
    cursor = db.cursor()
    query = "UPDATE users SET rootFolderId = %s WHERE id = %s"
    values = (root_folder_id, user_id)
    cursor.execute(query, values)
    db.commit()

#-------------------------------------------------------------
#text summarizaiton functions---------------------------------

# Function to create a new summarization
def create_summarization(text_input, parent_id, extractive_output, abstractive_output, title):
    cursor = db.cursor()
    query = "INSERT INTO summarizations (textInput, parentId, extractiveOutput, abstractiveOutput, title) VALUES (%s, %s, %s, %s, %s)"
    values = (text_input, parent_id, extractive_output, abstractive_output, title)
    cursor.execute(query, values)
    db.commit()
    return cursor.lastrowid

# Function to retrieve a specific summarization by ID
def get_summarization(summarization_id):
    cursor = db.cursor()
    query = "SELECT * FROM summarizations WHERE summarizationId = %s"
    cursor.execute(query, (summarization_id,))
    result = cursor.fetchone()
    return result


# Function to update an existing summarization
def update_summarization(summarization_id, text_input=None, parent_id=None, extractive_output=None, abstractive_output=None, title=None):
    cursor = db.cursor()
    query = "UPDATE summarizations SET "
    updates = []
    values = []
    if text_input is not None:
        updates.append("textInput = %s")
        values.append(text_input)
    if parent_id is not None:
        updates.append("parentId = %s")
        values.append(parent_id)
    if extractive_output is not None:
        updates.append("extractiveOutput = %s")
        values.append(extractive_output)
    if abstractive_output is not None:
        updates.append("abstractiveOutput = %s")
        values.append(abstractive_output)
    if title is not None:
        updates.append("title = %s")
        values.append(title)
    query += ", ".join(updates)
    query += " WHERE summarizationId = %s"
    values.append(summarization_id)
    cursor.execute(query, values)
    db.commit()

# Function to delete an existing summarization
def delete_summarization(summarization_id):
    cursor = db.cursor()
    query = "DELETE FROM summarizations WHERE summarizationId = %s"
    cursor.execute(query, (summarization_id,))
    db.commit()


#-------------------------------------------------------------
#keyword extraction funtions---------------------------------

# CREATE
def add_extraction(text_input, parent_id, output_text, title):
    cursor = db.cursor()
    query = "INSERT INTO keywordExtractions (textInput, parentId, outputText, title) VALUES (%s, %s, %s, %s)"
    values = (text_input, parent_id, output_text, title)
    cursor.execute(query, values)
    db.commit()
    return cursor.lastrowid

# READ
def get_extraction(extraction_id):
    cursor = db.cursor()
    query = "SELECT * FROM keywordExtractions WHERE extractionId = %s"
    cursor.execute(query, (extraction_id,))
    result = cursor.fetchone()
    return result

# UPDATE
def update_extraction(extraction_id, text_input=None, parent_id=None, output_text=None, title=None):
    cursor = db.cursor()
    query = "UPDATE keywordExtractions SET"
    if text_input:
        query += " textInput = %s,"
    if parent_id:
        query += " parentId = %s,"
    if output_text:
        query += " outputText = %s,"
    query = query[:-1] # remove trailing comma
    if title:
        query += " title = %s,"
    query = query[:-1] # remove trailing comma
    query += " WHERE extractionId = %s"
    values = []
    if text_input:
        values.append(text_input)
    if parent_id:
        values.append(parent_id)
    if output_text:
        values.append(output_text)
    if title:
        values.append(title)
    values.append(extraction_id)
    cursor.execute(query, tuple(values))
    db.commit()

# DELETE
def delete_extraction(extraction_id):
    cursor = db.cursor()
    query = "DELETE FROM keywordExtractions WHERE extractionId = %s"
    cursor.execute(query, (extraction_id,))
    db.commit()

#-------------------------------------------------------------
# Notes table---------------------------------

def create_note(textInput, title, parentId):
    cursor = db.cursor()
    query = "INSERT INTO notes (textInput, title, parentId) VALUES (%s, %s, %s)"
    values = (textInput, title, parentId)
    cursor.execute(query, values)
    db.commit()
    return cursor.lastrowid

# Function to retrieve a note by ID
def get_note_by_id(noteId):
    cursor = db.cursor()
    query = "SELECT * FROM notes WHERE noteId = %s"
    cursor.execute(query, (noteId,))
    result = cursor.fetchone()
    return result

# Function to update an existing note
def update_note_by_id(noteId, textInput, title, parentId):
    cursor = db.cursor()
    query = "UPDATE notes SET textInput = %s, title = %s, parentId = %s WHERE noteId = %s"
    values = (textInput, title, parentId, noteId)
    cursor.execute(query, values)
    db.commit()
    return cursor.rowcount

# Function to delete a note by ID
def delete_note_by_id(noteId):
    cursor = db.cursor()
    query = "DELETE FROM notes WHERE noteId = %s"
    cursor.execute(query, (noteId,))
    db.commit()
    return cursor.rowcount

# ------------------------------------------------------
# Folder functions--------------------------------------
# ------------------------------------------------------

# Create a new folder
def create_folder(folderTitle, parentId, userId):
    cursor = db.cursor()
    query = "INSERT INTO folders (folderTitle, parentId, userId) VALUES (%s, %s, %s)"
    values = (folderTitle, parentId, userId)
    cursor.execute(query, values)
    db.commit()
    return cursor.lastrowid

# Read a folder
def get_folder(folderId, userId):
    cursor = db.cursor()
    query = "SELECT * FROM folders WHERE folderId = %s AND userId = %s"
    cursor.execute(query, (folderId, userId))
    folder = cursor.fetchone()


    if folder is not None:
        folder_data = {
            'folderTitle': folder[1],
            'folderParent': folder[2],
            'folderId': folderId,            
            'folders': get_child_folders(folderId),
            'notes': get_notes_in_folder(folderId),
            'keyword_extractions': get_keyword_extractions_in_folder(folderId),
            'summarizations': get_summarizations_in_folder(folderId)
        }
        return folder_data
    else:
        return None

# Update a folder
def update_folder(folderId, folderTitle=None, parentId=None, userId=None):
    cursor = db.cursor()
    query = "UPDATE folders SET"
    values = []
    if folderTitle is not None:
        query += " folderTitle = %s,"
        values.append(folderTitle)
    if parentId is not None:
        query += " parentId = %s,"
        values.append(parentId)
    if userId is not None:
        query += " userId = %s,"
        values.append(userId)
    query = query[:-1] + " WHERE folderId = %s"
    values.append(folderId)
    cursor.execute(query, values)
    db.commit()

# Delete a folder
def delete_folder(folderId):
    cursor = db.cursor()
    query = "DELETE FROM folders WHERE folderId = %s"
    cursor.execute(query, (folderId,))
    db.commit()


# Get child folders of a parent folder
def get_child_folders(parentId):
    cursor = db.cursor()
    query = "SELECT * FROM folders WHERE parentId = %s"
    cursor.execute(query, (parentId,))
    child_folders = []
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        child_folders.append(dict(zip(columns, row)))
    return child_folders

# Get notes inside a folder
def get_notes_in_folder(folderId):
    cursor = db.cursor()
    query = "SELECT * FROM notes WHERE parentId = %s"
    cursor.execute(query, (folderId,))
    notes = []
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        notes.append(dict(zip(columns, row)))
    return notes
    

def get_keyword_extractions_in_folder(folderId):
    cursor = db.cursor()
    query = "SELECT * FROM keywordExtractions WHERE parentId = %s"
    cursor.execute(query, (folderId,))
    keyword_extractions = []
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        keyword_extractions.append(dict(zip(columns, row)))
    return keyword_extractions

def get_summarizations_in_folder(folderId):
    cursor = db.cursor()
    query = "SELECT * FROM summarizations WHERE parentId = %s"
    cursor.execute(query, (folderId,))
    summarizations = []
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        summarizations.append(dict(zip(columns, row)))
    return summarizations

def get_folder_title(folder_id):
    cursor = db.cursor()
    query = "SELECT folderTitle FROM folders WHERE folderId = %s"
    cursor.execute(query, (folder_id,))
    result = cursor.fetchone()

    if result:
        folder_title = result[0]
        return folder_title
    else:
        return None

def get_code(code):
    cursor = db.cursor()
    query = "SELECT * FROM code WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    return result


