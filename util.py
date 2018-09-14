# encoding=utf-8
import sqlite3

from flask import g

from settings import DATABASE


def get_db():

    # Check if we have already created
    # a database connection
    db = getattr(g, '_db', None)

    # There was no previous database
    # connection established
    if db is None:

        # We are assigning a connection
        # to _db attribute of g, and
        # are also saving that to
        # local variable called
        # db
        db = g._db = sqlite3.connect(DATABASE)

    return db

def validate_user_info(json_file, data_validation_json):

    if set(json_file.keys()) != set(data_validation_json.keys()):
        return "Missing/incorrect keys in submitted json"

    for key in json_file.keys():
        if not isinstance(json_file[key], data_validation_json[key]):
            return '"{}" value does not have the correct'.format(key) + \
                   ' type. Should be of type {}'.format(data_validation_json[key])

    return True