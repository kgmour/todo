# encoding=utf-8
import sqlite3

from flask import Flask, jsonify, request, g
from api_app.serializers import ToDoSchema
from datetime import date

from util import get_db

app = Flask(__name__)


@app.route('/', methods=('POST',))
@app.route('/<username>/<title>', methods=('GET',))
@app.route('/<username>/<title>', methods=('PUT',))
def user(username=None, title=None):

    # User creation
    if request.method == 'POST':

        created_at = date.today().strftime("%Y-%m-%d")
        last_edited_at = date.today().strftime("%Y-%m-%d")
        r_json = request.json
        r_json['created_at'] = created_at
        r_json['last_edited_at'] = last_edited_at
        # return jsonify(r_json)

        # We are using a serializer to validate data
        data_validator = ToDoSchema().load(r_json)

        # If we have errors
        if data_validator.errors:
            # We send back the errors with a 400
            return jsonify(data_validator.errors), 400
        else:

            # Are getting the cursor to the database
            cursor = get_db()
            try:

                to_commit = """
                INSERT INTO todo (username, title, content, created_at, last_edited_at) 
                VALUES ('{username}', '{title}', '{content}', '{created_at}', '{last_edited_at}')
                """.format(**data_validator.data).strip()

                cursor.execute(to_commit)
                cursor.commit()
            except sqlite3.DatabaseError as e:
                return jsonify({"error": str(e),
                                "message": "Error in creation"}), 400
            return jsonify("To do list item successfully created.".format()), 201
    # Getting the user
    elif request.method == 'GET':

        cursor = get_db().cursor()

        cursor.execute(
            """SELECT username, title, content, created_at, last_edited_at
            FROM todo where username = '{}' and title = '{}'""".format(username, title))

        results = cursor.fetchone()
        if results is None:
            return jsonify('{} or {} does not exist'.format(username, title))
        else:
            serialized_data = ToDoSchema.serialize_from_table_rows(results)
            return jsonify(serialized_data.data), 200

    elif request.method == 'PUT':

        last_edited_at = date.today().strftime("%Y-%m-%d")
        cursor = get_db().cursor()

        cursor.execute(
            """SELECT created_at from todo where username = '{}' 
            and title = '{}'""".format(username, title)
        )

        created_at = cursor.fetchone()
        # return jsonify(created_at)
        r_json = request.json
        r_json['created_at'] = created_at[0]

        data_validator = ToDoSchema().load(request.json)

        if data_validator.errors:
            return jsonify(data_validator.errors), 400
        else:

            cursor = get_db()
            try:
                to_commit = """
                    UPDATE todo SET title = '{}', content = '{}', last_edited_at = '{}' 
                    where title = '{}' and username = '{}'
                    """.format(request.json['title'], request.json['content'], last_edited_at, title, username)

                cursor.execute(to_commit)
                cursor.commit()

            except sqlite3.DatabaseError as e:
                return jsonify({"error": str(e),
                                "message": "Error in creation"}), 400
            return jsonify("To do list item successfully created.".format()), 204



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