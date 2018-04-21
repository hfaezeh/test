from __future__ import unicode_literals

from django.template.response import TemplateResponse

from rest_framework_mongoengine.viewsets import ModelViewSet as MongoModelViewSet

from app.serializers import *
from app.models import Tool, Book, Author
from users.authentication import TokenAuthentication
from rest_framework import permissions, views
from Crypto.Cipher import AES
import base64
import json
from Crypto import Random
from rest_framework.response import Response

def index_view(request):
    context = {}
    return TemplateResponse(request, 'index.html', context)


class ToolViewSet(MongoModelViewSet):
    """
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    """
    lookup_field = 'id'
    serializer_class = ToolSerializer

    def get_queryset(self):
        return Tool.objects.all()

class BookViewSet(MongoModelViewSet):
    lookup_field = 'id'
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.all()

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]



class AESCipher:

    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        #iv = Random.new().read( AES.block_size )
        iv = (16 * '\x00').encode('utf-8')
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))



class AuthorViewSet(views.APIView):
    lookup_field = 'id'
    serializer_class = AuthorSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        key = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
        key = (32*'0' + key )[-32:]
        cipher = AESCipher(key)
        #data_str = json.dumps(request.data)
        data_bytes = request.data['data']
        #encrypted = cipher.encrypt(data_str)
        decrypted = cipher.decrypt(data_bytes)
        decrypted_data = json.loads(decrypted)
        author =Author(name=decrypted_data['name'])
        author.save()
        return Response({'name':author.name})

    def get(self, request, pk, format=None):
        if pk:
            selected_record = Author.objects(name=pk)[0]._data
            selected_record.pop('id', None)
            data_str = json.dumps(selected_record)
            key = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
            key = (32 * '0' + key)[-32:]
            cipher = AESCipher(key)
            encrypted = cipher.encrypt(data_str)
            return Response({'data': encrypted.decode('utf-8')})





