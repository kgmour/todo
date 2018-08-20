# encoding=utf-8

from sqlalchemy import (create_engine,
                        MetaData,
                        Column, String, Integer, Boolean, ForeignKey)
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from api_app.my_hash import salt, hash_password, unhash_password
from werkzeug.security import generate_password_hash, check_password_hash
from strgen import StringGenerator
# from creds import salt
from api_app.redis_model import RedisNamespaceModel, RedisNamespaceSession
#
engine = create_engine('postgres://todoapi:todoapi@localhost:5432/postgres')
metadata = MetaData(bind=engine)
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)


class PrimaryMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


# class Salt(Base, PrimaryMixin):
#     __tablename__ = 'salts'
#
#     _salt = Column('salt', String(), nullable=False)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship('User', back_populates='salt')


class User(Base, PrimaryMixin):
    __tablename__ = 'users'

    username = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False)
    password = Column('password', String())
    _salt = Column('salt', String())
    todos = relationship('ToDo', back_populates='user')
    # salt = relationship('Salt', back_populates='user')

    # @property
    # def password(self):
    #     sess = Session()
    #     r = sess.query(User).filter_by(username=self.username).first()
    #     return check_password_hash()

    # @password.setter
    # def password(self, password):
    #     self._password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    @classmethod
    def get_all_info(cls, username):
        sess = Session()
        r = sess.query(User).filter_by(username=username).first()

        return {
            'username': username,
            'email': r.email,
            'todos': [todo.show() for todo in r.todos]
        }

    @classmethod
    def get_user_info(cls, username):
        sess = Session()
        r = sess.query(User).filter_by(username=username).first()
        sess.close()
        return {'username': r.username,
                'email': r.email,
                'id': r.id}

    @classmethod
    def login_return_token(cls, username, password):
        """Takes username and password and validates user.
        Also returns token to be used for future validation.
        """

        sess = Session()
        r = sess.query(User).filter_by(username=username)
        sess.close()

        is_user = check_password_hash(r.password, password)

        if is_user:
            secret_key = StringGenerator("[\d\w]{10}").render()
            rc = RedisNamespaceSession('users')
            rc.setex('username', secret_key, 900) #need to create setex method in redis_model
            token = hash_password(username+'-'+secret_key, salt)
            return token

    @classmethod
    def authenticate_user(cls, token):
        username, secret_key = unhash_password(token, salt).split('-')

        rc = RedisNamespaceSession('users')
        is_authenticated = rc.get(username)

        return True if is_authenticated else False


    @classmethod
    def create_user(cls, username, email, password):
        sess = Session()
        u = User(username=username, email=email)
        u.password = password
        sess.add(u)
        sess.commit()
        sess.close()


    @classmethod
    def delete_user(cls, username):
        sess = Session()
        user_exists = sess.query(User).filter_by(username=username).delete()
        if user_exists:
            sess.commit()
            sess.close()
            return 'User {} has been deleted'.format(username)
        else:
            sess.close()
            return 'User {} does not exist'.format(username)


    @classmethod
    def update_username_and_email(cls, username, response):

        sess = Session()
        user = sess.query(User).filter_by(username=username).first()

        if not user:
            return 'User {} does not exist'.format(username)

        user.username = response['username']
        user.email = response['email']
        sess.commit()
        sess.close()

        sess = Session()
        user = sess.query(User).filter_by(username=response['username']).first()

        sess.close()
        return {'user': user.username,
                'email': user.email}


class ToDo(Base, PrimaryMixin):
    __tablename__ = 'todos'

    title = Column(String(length=255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='todos')
    items = relationship('ToDoItem', back_populates='todo', cascade='all, delete-orphan')

    def show(self):
        return dict(title=self.title, items=[item.show() for item in self.items])


    @classmethod
    def get_todo(self, username, title):

        sess = Session()
        td = sess.query(ToDo).filter_by(title=title).first()
        if td:
            info = td.show()
        else:
            info = 'Todo {} does not exist'.format(title)
        sess.close()
        return info


    @classmethod
    def create_todo(cls, username, title, item, is_done=False, priority=None):
        sess = Session()
        u = sess.query(User).filter_by(username=username).first()
        if u:
            todo = sess.query(ToDo).filter_by(title=title).first()
            if todo:
                tdi = ToDoItem(description=item, priority=priority, is_done=is_done, todo=todo)
                todo.user = u
            else:
                todo = ToDo(title=title, user=u)
                tdi = ToDoItem(description=item, priority=priority, is_done=is_done, todo=todo)
            sess.add(u)
            sess.commit()
            sess.close()
        else:
            raise Exception('User does not exist')


    @classmethod
    def delete_todo(cls, username, title):

        sess = Session()
        try:
            q = sess.query(ToDo).filter(ToDo.title==title, User.username==username)
            td = q.first()
            sess.delete(td)
            sess.commit()
        except ProgrammingError:
            sess.rollback()
            return f'Either User {username} or ToDo {title} not found'
        finally:
            sess.close()
        return 'Todo {} has been removed for user {}'.format(title, username)


    @classmethod
    def update_todo(cls, username, title, response):

        sess = Session()
        q = sess.query(ToDo).filter(ToDo.title==title, User.username==username)
        td = q.first()
        if not td:
            return f'Todo {title} or User {username} do not exist'

        td.title = response['title']

        check = sess.query(ToDo).filter(ToDo.title==response['title'], User.username==username)

        return f'Todo {title} has been updated to {check.title}'


    def get_todoid_for_todo(self, sess, title):
        ids = sess.query(ToDo).all()


# does the user exist
# No - raise exception
# Yes - continue
# does the todo exist
# No - create the todo and add the item to the todo
# Yes - add the item to the todo


class ToDoItem(Base, PrimaryMixin):
    __tablename__ = 'items'

    description = Column(String(length=255), nullable=False)
    priority = Column(Integer)
    is_done = Column(Boolean)
    todo_id = Column(Integer, ForeignKey('todos.id'))

    todo = relationship('ToDo', back_populates='items')

    def show(self):
        return dict(priority=self.priority, description=self.description, is_done=self.is_done)


#8asdkwj3rkddaKd