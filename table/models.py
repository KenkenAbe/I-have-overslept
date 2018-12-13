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