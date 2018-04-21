# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .  import models
from django.template import loader

# def index(request):
#     if request.method == 'POST':
#        # save new post
#        first_name = request.POST['first_name']
#        last_name = request.POST['last_name']
#        username = request.POST['username']
#        try:
#            user = models.User(first_name=first_name, last_name= last_name,
#             username= username)
#            user.save()
#            return HttpResponse("sign up Done successfully.")
#        except:
#            return HttpResponse("something went wrong!")
#
#     # Get all posts from DB
#     else:
#         template = loader.get_template('index.html')
#         return HttpResponse(template.render({}, request))

from rest_framework_mongoengine import viewsets

from rest_framework.views import APIView
from polls.serializers import UserModelSerializer, FileSerializer
from polls.models import UserModel, StoredFiles
import os

from werkzeug.utils import secure_filename
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import project.settings as settings
from datetime import datetime
from rest_framework.response import Response
import mimetypes
import urllib
import json
import pickle
import base64
import PIL

ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])


class UserModelViewSet(viewsets.ModelViewSet):

    serializer_class = UserModelSerializer
    # permission_classes = (permissions.IsAuthenticated)
    # authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return UserModel.objects.all()

class FileViewSet(APIView):

    serializer_class = FileSerializer
    # permission_classes = (permissions.IsAuthenticated)
    # authentication_classes = (TokenAuthentication,)

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def post(self, request, *args, **kwargs):
        request.META.get('HTTP_FILENAME')
        file = request.FILES.get('newfile')
        if not file is None and file.name:
            filename = secure_filename(file.name)
            temp_name = str(uuid.uuid4()) + '.' + filename.split('.')[-1]
            date_folder = datetime.utcnow().date()
            date_folder = datetime.strftime(date_folder, "%Y-%m-%d")
            hour_folder = str(datetime.utcnow().hour)
            tmp_file = os.path.join(settings.MEDIA_ROOT, date_folder+'/'+hour_folder+'/'+temp_name)
            path = default_storage.save(tmp_file, ContentFile(file.read()))
            StoredFiles.objects.get_or_create(file_name=filename, upload_path=path, stored_name=temp_name)
            url = request.build_absolute_uri()
            if self.allowed_file(file.name):
                im = PIL.Image.open(path)
                size = 200, 200
                im.thumbnail(size)
                im.save(tmp_file.split('.')[:-1][0] + "_thumbnail.jpg", "JPEG")
                StoredFiles.objects.get_or_create(file_name=filename, upload_path=(tmp_file.split('.')[:-1][0] +
                                                                                   "_thumbnail.jpg"), stored_name=
                (tmp_file.split('/')[-1].split('.')[0] + "_thumbnail.jpg"))
                return Response({'url': url + temp_name,
                             'thumbnail': url + tmp_file.split('/')[-1].split('.')[0] + "_thumbnail.jpg"})
            else:
                return Response({'url': url + temp_name})
        return {'error': 'something went wrong!'}

    def get(self, request, pk, format=None):
        if pk:
            selected_file = StoredFiles.objects(stored_name=pk)[0]
            file_path = selected_file.upload_path
            original_filename = selected_file.file_name
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    type, encoding = mimetypes.guess_type(original_filename)
                    if type is None:
                        type = 'application/octet-stream'
                    #encoded = base64.encodebytes(fh.read()).decode("ascii")

                    response = HttpResponse(fh.read())
                    response['Content-Type'] = type
                    response['Content-Length'] = str(os.stat(file_path).st_size)
                    if encoding is not None:
                        response['Content-Encoding'] = encoding
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    if u'WebKit' in request.META['HTTP_USER_AGENT']:
                        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
                        filename_header = 'filename=%s' % original_filename
                    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
                        # IE does not support internationalized filename at all.
                        # It can only recognize internationalized URL, so we do the trick via routing rules.
                        filename_header = ''
                    else:
                        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
                        filename_header = 'filename*=UTF-8\'\'%s' % urllib.parse.quote(original_filename)
                    response['Content-Disposition'] = 'attachment; ' + filename_header
                    return response
            else:
                selected_file.delete()

        return Response({'error': 'not found'})
