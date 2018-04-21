from rest_framework_mongoengine import serializers
from university.models import *

class StudentSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class TeacherSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


class CourseSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Course
        fields = '__all__'