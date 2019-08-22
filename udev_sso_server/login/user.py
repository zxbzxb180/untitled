#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from bson import ObjectId
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from udev_settings import settings
from udev_db import database

UserModel = get_user_model()

user_db = database(
    name='upermission',
    host=settings.UPERMISSIONDB_HOST,
    port=settings.UPERMISSIONDB_PORT,
)

cas_db = database(
    name=settings.CAS_ACCOUNT_TRANSFORM_DB,
    host=settings.CAS_ACCOUNT_TRANSFORM_HOST,
    port=settings.CAS_ACCOUNT_TRANSFORM_PORT,
)


def check_origin_auth(username, password):
    """
    查找 udev 用户数据库，根据给定的用户名和密码查找是否有这个用户
    :param username: 用户名
    :param password:  密码
    :return: boolean
    """
    hash_pass = hashlib.md5(password.encode('utf8')).hexdigest()
    user = user_db.user.find_one({'name': username, 'password': hash_pass})
    if user and not user.get('disable', False):
        return True
    else:
        return False


def create_or_get_user(username):
    try:
        user = UserModel._default_manager.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        # 新建用户
        user = User.objects.create_user(username=username)
        user.save()

    return user


def account_transform(login_url, username):
    client = cas_db.cas_client_map.find_one({'url': login_url})
    if not client:
        return username

    account = cas_db.cas_account_map.find_one({'client_id': str(client['_id']), 'from': username})
    if not account:
        return username

    else:
        return account.get('to', username)


class MongoUser(ModelBackend):
    """ 不检查 django 的用户密码，改为检查 udev 用户的密码
    在检查的时候发现 django 还没有这个用户，就创建一个
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if password is not None:
            if check_origin_auth(username, password):
                # 只要是在 udev 用户数据库找到了用户，那就能正确登录
                # 如果没有在本地数据库找到，就新建一个
                username = account_transform(request.GET.get('service'), username)
                user = create_or_get_user(username)
                return user
        else:
            super(MongoUser, self).authenticate(request, username=None, password=None, **kwargs)