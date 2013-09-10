# -*- coding: utf-8 -*-
from django.db import models


class Sample(models.Model):
    
    text = models.CharField(max_length=200)

    class Meta:
        db_table = 'comments'
        app_label= 'api'

    def __unicode__(self):
        return ""