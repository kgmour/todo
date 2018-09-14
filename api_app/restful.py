# from flask import Flask, request
# from flask_restful import Resource, Api
#
# app = Flask(__name__)
# api = Api(app)
#
# todos = {}
#
# class TodoSimple(Resource):
#     def get(self, todo_id):
#         return {todo_id: todos[todo_id]}
#
#     def put(self, todo_id):
#         todos[todo_id] = request.form['data']
#         return {todo_id: todos[todo_id]}
#
# api.add_resource(TodoSimple, '/<string:todo_id>')
#
# if __name__ == '__main__':
#     app.run(debug=True)

# encoding=utf-8

import redis
from flask import Flask, request
from flask_restful import Resource, Api
from .models import (User,
                    ToDo, Session, generate_password_hash, check_password_hash)
from .serializers import UserSchema, TodoSchema, TodoTitleSchema, LoginSchema

r = redis.StrictRedis(host='localhost', port=6379, db=0)
app = Flask(__name__)
api = Api(app)

# sess = Session()

# def key_exists(userid):
#     return userid in r.keys()
#
# def check_rate(userid):
#     if key_exists(userid):
#         return r.get(userid)
#     else:
#         return 0
#
# def incr_key_value(userid):
#     r.incr(userid)


class ResponseMessage(object):


    def __init__(self, message, **kwargs):
        self.message = message
        self.extra = kwargs


    def to_dict(self):
        return dict(message=self.message, extra=self.extra)

# class Authentication(object):
#
#     def __init__(self, token):
#         self.authenticated = User.authenticate_user(token)
#
#         if self.authenticated:



# class Todos(Resource):
#     def get(self, todo_id):
#         return {todo_id: ToDo.show()}
#
#
#     def put(self, ):
#         pass
#
#
# class TodoID(Resource):
#     def get(self, todo_title):
#         pass
#
#
# class Users(Resource):
#     def post(self, username, email):
#
#
#         data_validator = UserSchema().load(request.json)
#
#         if data_validator.errors:
#             # We send back the errors with a 400
#             return jsonify(data_validator.errors), 400
#         else:
#
#             User.create_user(username, email)

class UserListResource(Resource):

    def post(self):

        userschema = UserSchema()

        response, errors = userschema.load(request.json)

        if errors:
            return errors

        print(request)

        User.create_user(response['username'],
                         response['email'],
                         generate_password_hash(f'{response["password"]}',
                                                    method='pbkdf2:sha256',
                                                    salt_length=8))

        sess = Session()
        user = sess.query(User).filter_by(username=response['username']).first()
        sess.close()

        return ResponseMessage(message=f"User {user.username} created").to_dict(), 201


class UserResource(Resource):

    def get(self, username):

        sess = Session()
        u = sess.query(User).filter_by(username=username).first()
        sess.close()

        if not u:
            return ResponseMessage(message=f"User {username} not found").to_dict(), 404

        info = User.get_all_info(username=username)

        return ResponseMessage(message=info).to_dict(), 200


    def delete(self, username):

        if not User.authenticate_user(request.json['token']):
            return ResponseMessage(message="Not authenticated. Please log in to receive a token").to_dict(), 403

        response = User.delete_user(username)

        return ResponseMessage(message=response).to_dict(), 200

    def put(self, username):

        userschema = UserSchema()

        response, errors = userschema.load(request.json)

        if errors:
            return errors

        info = User.update_username_and_email(username, response)

        return ResponseMessage(message=info).to_dict(), 201


class TodoListResource(Resource):

    def post(self):

        if not User.authenticate_user(request.json['token']):
            return ResponseMessage(message="Not authenticated. Please log in to receive a token").to_dict(), 403

        todoschema = TodoSchema()

        response, errors = todoschema.load(request.json)

        if errors:
            return errors

        ToDo.create_todo(username=response['username'], title=response['title'], item=response['item'])

        sess = Session()
        todo = sess.query(ToDo).filter_by(title=response['title']).first()
        sess.close()

        return ResponseMessage(message=f'Todo {todo.title} has been created').to_dict(), 201


class LoginResource(Resource):

    def post(self):

        loginschema = LoginSchema()

        response, errors = loginschema.load(request.json)

        if errors:
            return errors

        token = User.login_return_token(response['username'], response['password'])

        return token


class TodoResource(Resource):

    def get(self, username, title):

        if not User.authenticate_user(request.json['token']):
            return ResponseMessage(message="Not authenticated. Please log in to receive a token").to_dict(), 403

        response = ToDo.get_todo(username, title)
        if response:
            return ResponseMessage(message=response).to_dict(), 200
        else:
            return ResponseMessage(message=f'User {username} does not exist').to_dict(), 404


    def delete(self, username, title):

        response = ToDo.delete_todo(username, title)

        if 'Either' in response:
            return ResponseMessage(message=response).to_dict(), 404
        else:
            return ResponseMessage(message=response).to_dict(), 200


    def put(self, username, title):

        todotitleschema = TodoTitleSchema()

        response, errors = todotitleschema.load(request.json)

        if errors:
            return errors

        info = ToDo.update_todo(username, title, response)

        if 'User' in info:
            return ResponseMessage(message=info).to_dict(), 404
        else:
            return ResponseMessage(message=info).to_dict(), 201



# User stuff
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<string:username>')
api.add_resource(LoginResource, '/users/login')
#
#
api.add_resource(TodoListResource, '/users/')
api.add_resource(TodoResource, '/users/<string:username>/todos/<string:title>')
# api.add_resource(Users, '/<string:todo_id')
# api.add_resource(TodoID, '/<string:todo_title')

if __name__ == '__main__':
    app.run(debug=True)




