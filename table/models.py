from django.db import models

# Create your models here.

class timetables(models.Model):
    title = models.CharField(max_length=256,default="")
    teacher = models.CharField(max_length=256,default="")
    level = models.IntegerField()
    week = models.IntegerField()
    time = models.IntegerField()
    start_time = models.IntegerField()
    end_time = models.IntegerField()
    room = models.CharField(max_length=256,default="")
    target_id = models.CharField(max_length=256,default="")
    quater = models.IntegerField()
    year = models.IntegerField()
    isNotification = models.BooleanField(default=False)

class users(models.Model):
    userName = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    admission_year = models.IntegerField()
    permission_level = models.IntegerField()

class notifications(models.Model):
    target = models.CharField(max_length=100)
    fireTime = models.IntegerField()
    status = models.IntegerField()
    targetTeacher = models.CharField(max_length=100, default="")
    isContact = models.BooleanField(default=False)
    title = models.CharField(max_length=100,default="")

class devices(models.Model):
    target_id = models.CharField(max_length=100,default="")
    device_type = models.IntegerField(default=0)
    device_token = models.CharField(max_length=100,default="")

class teachers(models.Model):
    name = models.CharField(max_length=100)
    mail = models.CharField(max_length=100)
    university = models.CharField(max_length=100,default="")

