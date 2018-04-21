from __future__ import unicode_literals

from django.db import models
from mongoengine import Document, fields
from django.core.exceptions import ValidationError
import re


def check_student_id(value):
    pattern = re.compile("^([0-9]+)+$")
    if not pattern.match(value):
        raise ValidationError(
            _('%(value)s is not a valid student number'),
            params={'value': value},
        )


class Student(Document):
    
    name = fields.StringField(required=True)
    student_id = fields.StringField(required=True, validation=[check_student_id])

# Create your models here.


class Teacher(Document):
    
    name = fields.StringField(required=True)


class Course(Document):
    
    name = fields.StringField(required=True)
    capacity = fields.IntField()
    teacher = fields.ReferenceField(Teacher)
    students = fields.ListField(fields.ReferenceField(Student))
