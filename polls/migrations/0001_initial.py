# -*- coding: utf-8 -*-
from django.db import models, migrations
import django_autoslugfield.fields
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('contenttypes', '0002_remove_content_type_name'),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Choice',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('choice', models.CharField(max_length=255)),
				('votes', models.PositiveIntegerField(default=0)),
			],
			options={
				'verbose_name': 'odpove\u010f',
				'verbose_name_plural': 'odpovede',
			},
		),
		migrations.CreateModel(
			name='Poll',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('question', models.TextField(verbose_name='ot\xe1zka')),
				('slug', django_autoslugfield.fields.AutoSlugField(title_field='question', unique=True)),
				('object_id', models.PositiveIntegerField(null=True, blank=True)),
				('active_from', models.DateTimeField(null=True, blank=True)),
				('checkbox', models.BooleanField(default=False)),
				('approved', models.BooleanField(default=False)),
				('answer_count', models.PositiveIntegerField(default=0)),
				('content_type', models.ForeignKey(blank=True, limit_choices_to={'model__in': ('article',)}, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
			],
			options={
				'verbose_name': 'anketa',
				'verbose_name_plural': 'ankety',
			},
		),
		migrations.CreateModel(
			name='RecordIp',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('ip', models.GenericIPAddressField()),
				('date', models.DateTimeField(auto_now_add=True)),
				('poll', models.ForeignKey(to='polls.Poll', on_delete=models.CASCADE)),
			],
		),
		migrations.CreateModel(
			name='RecordUser',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('date', models.DateTimeField(auto_now_add=True)),
				('poll', models.ForeignKey(to='polls.Poll', on_delete=models.CASCADE)),
				('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
		),
		migrations.AddField(
			model_name='choice',
			name='poll',
			field=models.ForeignKey(to='polls.Poll', on_delete=models.CASCADE),
		),
		migrations.AlterUniqueTogether(
			name='recorduser',
			unique_together=set([('poll', 'user')]),
		),
		migrations.AlterUniqueTogether(
			name='recordip',
			unique_together=set([('poll', 'ip')]),
		),
	]
