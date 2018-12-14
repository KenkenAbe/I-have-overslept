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

class Users(models.Model):
    UserName = models.CharField(max_length=100)
    Token = models.CharField(max_length=100)
    Tag = models.CharField(max_length=100)
    Mail = models.CharField(max_length=100)

class Notifications(models.Model):
    Target = models.CharField(max_length=100)
    FireTime = models.IntegerField()
    Status = models.IntegerField()
    IsContact = models.BooleanField()

class Devices(models.Model):
    Device = models.IntegerField()
    Token = models.CharField(max_length=100)

class Teachers(models.Model):
    Name = models.CharField(max_length=100)
    Mail = models.CharField(max_length=100)