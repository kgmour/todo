# encoding=utf-8
# Created by Quazi Nafiul Islam on 10/04/2018
from typing import Dict, Union, Optional, ByteString

import redis


class RedisNamespaceSession(object):

    def __init__(self, namespace: str, pool: Optional[redis.ConnectionPool] = None):

        self.namespace = namespace
        self.rc = self._get_redis_client(pool)

    def get(self, key: str) -> Union[ByteString, int, float, None, bool]:
        """
        Gets a particular key from the hashmap set associated with
        the username
        :param key: The key you want from the username hashmap (dictionary)
        :return: Returns the value of the key in bytestring format
        """

        # The hmget functions returns a list, and
        # therefore, we will try to get the first
        # item of that list
        try:
            value = self.rc.hmget(self.namespace, key)
            if isinstance(value, list):
                return value[0]
            else:
                return value
        except IndexError:
            return None

    def get_all(self) -> Dict[ByteString, Union[ByteString, int, float]]:
        """
        Gets all the keys associated with the user.
        :return: A dictionary with bystring keys.
        """
        return self.rc.hgetall(self.namespace)

    def set(self, key: str, value: Union[str, int, float]) -> int:
        """
        Sets a particular key on the username hashmap. Does not support
        complex structures such as lists or dictionaries.
        :param key: The key you want to set
        :param value: The value you want to set your key to
        :return:
        """
        return self.rc.hset(self.namespace, key, value)

    def setex(self, key: str, value: Union[str, int, float], time: str) -> int:
        """
        Like set but adds expiration time to key/value in redis database
        :param key: The key you want to set
        :param value: The value you want to set your key to
        :param time: How long you want the key/value to live in redis
        :return:
        """
        return self.rc.setex(self.namespace, key, time, value)

    def delete(self, key):
        """
        Deletes a particular key from the HashMap set in redis.
        :param key:
        :return:
        """
        return self.rc.hdel(self.namespace, key)

    def _get_redis_client(self, pool: Optional[redis.ConnectionPool] = None):
        """
        Private function that creates the redis client, that is used
        internally for all communication.
        :param pool: Redis Pool ob
        :return:
        """
        # We start off with the default strict
        # redis constructor arguments
        creation_args = dict(host='localhost', port=6379, decode_responses=True)

        # If we have a connection pool object,
        # then we us to create it.
        if pool:
            creation_args['connection_pool'] = pool

        return redis.StrictRedis(**creation_args)

    @property
    def is_connected(self) -> bool:
        """
        Sends a ping as to whether or not the client is
        able to connect to the redis server.
        :return: True if connected, False otherwise.
        """
        return self.rc.ping()

    @property
    def exists(self) -> bool:
        """
        Checks to see whether or not the username exists
        :return: True if it exists, False otherwise
        """
        if self.rc.get(self.namespace):
            return True
        else:
            return False


class RedisNamespaceModel(object):

    def __init__(self, namespace: str):
        """
        Initializes the redis user session.
        All session creation is done automatically.

        Underneath, this uses the RedisUserSession object,
        this object is created as a convenience in order
        to have easy access to redis information.

        :param namespace: The key used for the main hashmap.
        """
        self._create_session(namespace)
        self._create_type_dict()

    def _create_type_dict(self):
        self.__dict__['_type_dict'] = dict()

    def _create_session(self, namespace):
        self.__dict__['sess'] = RedisNamespaceSession(namespace)

    def __getattr__(self, item: str):
        """
        Gets the item in question. First it will check the
        main object body, and then it will check redis for
        the key.
        """

        try:
            object_item = super().__getattribute__(item) # TODO
            return object_item
        except AttributeError:
            # In case of an attribute error (which will
            # usually be the case), we will look for the
            # key in redis.
            redis_item = self.sess.get(item)
            redis_item = str(redis_item)
            if redis_item:
                return self._type_dict[item](redis_item) # TODO
            elif redis_item is None:

                # In case we do not find it, we will
                # raise the same kind of error as
                # the original __getattribute__
                # method.
                raise AttributeError(f"{item} does not exist"
                                     f" on either object or"
                                     f" in redis.")

    def __setattr__(self, key: str, value: Union[str, int, float]):
        """
        Sets the key to the value in redis. Unfortunately,
        with this model, we give up the ability to set
        attributes on the model object itself.
        """

        if hasattr(self, 'sess'):
            self._type_dict[key] = type(value)
            if isinstance(value, bool):
                return self.sess.set(key, 1) if value else self.sess.set(key, str(''))
            return self.sess.set(key, value)

        return super().__setattr__(key, value)

    @property
    def items(self):
        """
        Gets all the keys and values of this
        """
        return self.sess.get_all()