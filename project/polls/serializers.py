# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
# Create your models here.

from rest_framework_mongoengine import serializers
from polls.models import UserModel,StoredFiles


class UserModelSerializer(serializers.DocumentSerializer):

    class Meta:
        model = UserModel
        fields = '__all__'

class FileSerializer(serializers.DocumentSerializer):

    class Meta:
        model = StoredFiles
        fields = '__all__'