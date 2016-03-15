import os

from django.contrib.auth.models import User
from django.db import models

from trec_project.enumTypes import runTypes, feedbackTypes, queryTypes
from trec_project.settings import MEDIA_ROOT


class Researcher(models.Model):

    user = models.OneToOneField(User)
    profile_pic = models.ImageField(upload_to=os.path.join(MEDIA_ROOT, 'profile_pics'), blank=True)
    website = models.URLField(max_length=1024, default="")
    display_name = models.CharField(max_length=128, default="")
    organisation = models.CharField(max_length=128, default="")

    def __unicode__(self):
        return self.user.username

class Track(models.Model):

    title = models.CharField(max_length=128, unique=True)
    track_url = models.URLField(max_length=1024, default="")
    description = models.CharField(max_length=1024, default="")
    genre = models.CharField(max_length=1024, default="")

    def __unicode__(self):
        return self.title

class Task(models.Model):

    track = models.ForeignKey(Track)
    title = models.CharField(max_length=128, default="")
    task_url = models.URLField(max_length=1024, default="")
    description = models.CharField(max_length=1024)
    year = models.CharField(max_length=4, default="")
    judgement_file = models.FileField(upload_to=os.path.join(MEDIA_ROOT, 'judgement_files'))

    def __unicode__(self):
        return self.track.__unicode__()

class Run(models.Model):

    researcher = models.ForeignKey(Researcher)
    task = models.ForeignKey(Task)
    name = models.CharField(max_length=128, default="")
    description = models.CharField(max_length=1024, default="")
    results_file = models.FileField(upload_to=os.path.join(MEDIA_ROOT, 'results'))
    map = models.FloatField(null=True)
    p10 = models.FloatField(null=True)
    p20 = models.FloatField(null=True)
    run_type = models.CharField(max_length=1, choices=runTypes, default=runTypes[0][0])
    query_type = models.CharField(max_length=6, choices=queryTypes, default=queryTypes[0][0])
    feedback_type = models.CharField(max_length=5, choices=feedbackTypes, default=feedbackTypes[0][0])

    def __unicode__(self):
        return self.researcher.__unicode__() + " - " + self.task.__unicode__() + " - " + self.id.__str__()
