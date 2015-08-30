# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='attempt_group',
            field=models.ForeignKey(to='auth.Group', null=True, blank=True, related_name='attexam_set'),
        ),
        migrations.AlterField(
            model_name='exam',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='exam',
            name='solutions_group',
            field=models.ForeignKey(to='auth.Group', null=True, blank=True, related_name='solexam_set'),
        ),
        migrations.AlterField(
            model_name='examanswersheet',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='examanswersheet',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='unlock_marks',
            field=models.IntegerField(null=True, blank=True, verbose_name='Minimum marks to attempt this section'),
        ),
        migrations.AlterField(
            model_name='section',
            name='unlock_questions',
            field=models.PositiveIntegerField(null=True, blank=True, verbose_name='Minimum attempted questions to attempt this section'),
        ),
    ]
