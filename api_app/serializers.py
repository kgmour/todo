# encoding=utf-8
from marshmallow import Schema, fields
from enum import Enum
from datetime import date


# def check_list_of_occupations(occupation):
#
#     occupations = [
#         'Engineer',
#         'Doctor',
#         'Scientist',
#         'Professional Dancer',
#         'Publicist',
#         'Writer',
#         'Chicken'
#     ]
#
#     return occupation in occupations

# class ToDoTableEnum(Enum):
#     username = 0
#     title = 1
#     content = 2
#     created_at = 3
#     last_edited_at = 4
#
#
# class ToDoSchema(Schema):
#
#     enum_class = ToDoTableEnum
#
#     username = fields.Str(validate=lambda s: 1 <= len(s) <= 128)
#     title = fields.Str(validate=lambda s: 1 <= len(s) <= 100)
#     content = fields.Str(validate=lambda s: 1 <= len(s) <= 250)
#     created_at = fields.Date()
#     last_edited_at = fields.Date()
#
#     @classmethod
#     def serialize_from_table_rows(cls, table_row):
#
#         return cls().load({
#             attr.name: table_row[attr.value] for attr in cls.enum_class
#         })
#
# class UserSchema(Schema):
#
#     username = fields.Str(validate=lambda s: 1 <= len(s) <= 128)
#     title = fields.Str(validate=lambda s: 1 <= len(s) <= 100)
#     content = fields.Str(validate=lambda s: 1 <= len(s) <= 250)
    # created_at = date.today()
    # last_edited_at = date.today()


# serializers

class UserSchema(Schema):
    username = fields.Str(validate=lambda s: 1 <= len(s) <= 128)
    email = fields.Email()
    password = fields.String(validate=lambda s: 4 <= len(s) <= 128)


class TodoTitleSchema(Schema):
    title = fields.Str(validate=lambda s: 1 <= len(s) <= 128)


class TodoSchema(Schema):
    title = fields.Str(validate=lambda s: 1 <= len(s) <= 128)
    username = fields.Str(validate=lambda s: 1 <= len(s) <= 128)
    item = fields.Str(validate=lambda s: 1<= len(s) <= 128)


class TodoItemSchema(Schema):
    description = fields.Str(validate=lambda s: 1 <= len(s) <= 256)
    priority = fields.Int(validate=lambda s: 1<= s <=5)
    is_done = fields.Boolean()


class LoginSchema(Schema):
    username = fields.Str(validate=lambda s: 1 <= len(s) <= 128, required=True)
    password = fields.Str(validate=lambda s: 1 <= len(s) <= 128, required=True)