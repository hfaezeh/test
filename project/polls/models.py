# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
# Create your models here.
from mongoengine import *


class UserModel(Document):
     first_name = StringField(max_length=30, required = True)
     last_name = StringField(max_length=30, required = True)
     username = StringField(max_length=30, required = True, unique = True)
     image = FileField(required=True)
     meta = {'strict': False}
    #comments = ListField()


class StoredFiles(Document):

    file_name = StringField(required=True)
    upload_path = StringField(required=True)
    stored_name = StringField(required=True)
