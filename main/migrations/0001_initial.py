# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('viewed_hint', models.BooleanField(default=False)),
                ('attempts', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('info', models.TextField(blank=True)),
                ('time_limit', models.DurationField(verbose_name='Time limit to complete exam', default=datetime.timedelta(0))),
                ('shuffle_sections', models.BooleanField(verbose_name='Randomly shuffle sections', default=False)),
                ('can_attempt_again', models.BooleanField(verbose_name='Can a user attempt this exam multiple times', default=True)),
                ('author', models.TextField(blank=True)),
                ('comment', models.TextField(blank=True)),
                ('postinfo', models.TextField(blank=True)),
                ('attempt_group', models.ForeignKey(to='auth.Group', null=True, related_name='attexam_set')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('solutions_group', models.ForeignKey(to='auth.Group', null=True, related_name='solexam_set')),
            ],
        ),
        migrations.CreateModel(
            name='ExamAnswerSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('exam', models.ForeignKey(to='main.Exam')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='McqAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('answer', models.OneToOneField(to='main.Answer')),
            ],
            options={
                'ordering': ('id',),
            },
            bases=(models.Model, main.models.SpecialAnswer),
        ),
        migrations.CreateModel(
            name='McqAnswerToMcqOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('mcq_answer', models.ForeignKey(to='main.McqAnswer')),
            ],
        ),
        migrations.CreateModel(
            name='McqOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=30, blank=True)),
                ('text', models.TextField()),
                ('is_correct', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='McqQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('multicorrect', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('id',),
            },
            bases=(models.Model, main.models.SpecialQuestion),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=120, blank=True)),
                ('text', models.TextField(blank=True)),
                ('hint', models.TextField(blank=True)),
                ('solution', models.TextField(blank=True)),
                ('comment', models.TextField(blank=True)),
                ('metadata', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('info', models.TextField(blank=True)),
                ('comment', models.TextField(blank=True)),
                ('postinfo', models.TextField(blank=True)),
                ('correct_marks', models.IntegerField(verbose_name='Marks for correct answer', default=1)),
                ('wrong_marks', models.IntegerField(verbose_name='Marks for wrong answer', default=0)),
                ('na_marks', models.IntegerField(verbose_name='Marks for not attempting question', default=0)),
                ('hint_deduction', models.IntegerField(verbose_name='Marks deducted for viewing hint', default=0)),
                ('unlock_marks', models.IntegerField(verbose_name='Minimum marks to attempt this section', null=True)),
                ('unlock_questions', models.PositiveIntegerField(verbose_name='Minimum attempted questions to attempt this section', null=True)),
                ('unlock_both_needed', models.BooleanField(verbose_name='Should both minimum question and minimum marks requirements be fulfilled?', default=True)),
                ('shuffle_options', models.BooleanField(verbose_name='Randomly shuffle options of questions', default=False)),
                ('shuffle_questions', models.BooleanField(verbose_name='Randomly shuffle questions', default=False)),
                ('allowed_attempts', models.IntegerField(verbose_name='Number of attempts allowed per question', default=0)),
                ('show_correct_answer', models.BooleanField(verbose_name='Should correct answer be shown after attempting a question?', default=False)),
                ('show_solution', models.BooleanField(verbose_name='Should solution be shown after attempting a question?', default=False)),
                ('max_questions_to_attempt', models.PositiveIntegerField(verbose_name='Maximum number of questions a student is allowed to attempt', default=0)),
                ('exam', models.ForeignKey(to='main.Exam')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='SectionAnswerSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('exam_answer_sheet', models.ForeignKey(to='main.ExamAnswerSheet')),
                ('section', models.ForeignKey(to='main.Section')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TextAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('response', models.TextField(blank=True)),
                ('answer', models.OneToOneField(to='main.Answer')),
            ],
            options={
                'ordering': ('id',),
            },
            bases=(models.Model, main.models.SpecialAnswer),
        ),
        migrations.CreateModel(
            name='TextQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('ignore_case', models.BooleanField(default=True)),
                ('use_regex', models.BooleanField(default=False)),
                ('correct_answer', models.TextField()),
                ('question', models.OneToOneField(to='main.Question')),
            ],
            options={
                'ordering': ('id',),
            },
            bases=(models.Model, main.models.SpecialQuestion),
        ),
        migrations.AddField(
            model_name='textanswer',
            name='special_question',
            field=models.ForeignKey(to='main.TextQuestion'),
        ),
        migrations.AddField(
            model_name='section',
            name='tags',
            field=models.ManyToManyField(to='main.Tag'),
        ),
        migrations.AddField(
            model_name='question',
            name='section',
            field=models.ForeignKey(to='main.Section'),
        ),
        migrations.AddField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(to='main.Tag'),
        ),
        migrations.AddField(
            model_name='mcqquestion',
            name='question',
            field=models.OneToOneField(to='main.Question'),
        ),
        migrations.AddField(
            model_name='mcqoption',
            name='special_question',
            field=models.ForeignKey(to='main.McqQuestion'),
        ),
        migrations.AddField(
            model_name='mcqanswertomcqoption',
            name='mcq_option',
            field=models.ForeignKey(to='main.McqOption'),
        ),
        migrations.AddField(
            model_name='mcqanswer',
            name='chosen_options',
            field=models.ManyToManyField(to='main.McqOption', through='main.McqAnswerToMcqOption'),
        ),
        migrations.AddField(
            model_name='mcqanswer',
            name='special_question',
            field=models.ForeignKey(to='main.McqQuestion'),
        ),
        migrations.AddField(
            model_name='exam',
            name='tags',
            field=models.ManyToManyField(to='main.Tag'),
        ),
        migrations.AddField(
            model_name='answer',
            name='section_answer_sheet',
            field=models.ForeignKey(to='main.SectionAnswerSheet'),
        ),
    ]
