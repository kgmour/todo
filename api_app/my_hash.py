import random
import string

characters = string.ascii_letters + string.digits
key = 'SlKkyQzavoEGh8iTHt9YVWmMqPgjsr34wxu6fFCeDN5L72dIJc1p0nXBORbAZU'
values = key[20:] + key[:20]

# user = {'username': ['faho723fjasdlasdf', 'salt']}

salt = 'id893Dlw'

def _get_salt(length=5):
    salt = ''
    for i in range(length):
        salt += random.choice(values)

    return salt

def hash_password(password, salt):
    salted_password = f'{salt}{password}{salt}'
    hashed_password = ''
    for c in salted_password:
        hashed_password += key[values.index(c)]

    return hashed_password

def unhash_password(hashed_password, salt):
    salt_length = len(salt)
    unhashed_password = ''.join([values[key.index(c)] for c in hashed_password])
    return unhashed_password[salt_length:-salt_length]
