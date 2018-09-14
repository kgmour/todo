# encoding=utf-8
import sqlite3

from flask import Flask, jsonify, request, g
from api_app.serializers import UserSchema

from util import get_db

app = Flask(__name__)


@app.route('/', methods=['POST'])
@app.route('/<username>', methods=['GET'])
def user(username=None):

    # User creation
    if request.method == 'POST':

        # We are using a serializer to validate data
        data_validator = UserSchema().load(request.json)

        # If we have errors
        if data_validator.errors:
            # We send back the errors with a 400
            return jsonify(data_validator.errors), 400
        else:

            # Are getting the cursor to the database
            cursor = get_db()
            try:

                to_commit = """
                INSERT INTO users (username, age, occupation) 
                VALUES ('{username}', '{age}', '{occupation}')
                """.format(**data_validator.data).strip()

                cursor.execute(to_commit)
                cursor.commit()
            except sqlite3.DatabaseError as e:
                return jsonify("Error in creation"), 400
            return jsonify("User {} successfully created.".format(username)), 201
    # Getting the user
    elif request.method == 'GET':

        cursor = get_db().cursor()
        try:

            to_commit = """
            SELECT username, age, occupation
            FROM users where username = '{}'""".format(username)

            cursor.execute(to_commit)

            b = cursor.fetchone()
        except sqlite3.DatabaseError as e:
            return jsonify("User not found"), 400
        return jsonify({'username': b[0],
                       'age': b[1],
                       'occupation': b[2]}), 200



@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('init.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)