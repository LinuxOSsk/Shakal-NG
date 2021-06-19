# -*- coding: utf-8 -*-
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

	dependencies = [
		('contenttypes', '0002_remove_content_type_name'),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Event',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('object_id', models.PositiveIntegerField(null=True, blank=True)),
				('time', models.DateTimeField(auto_now_add=True)),
				('action', models.CharField(default='m', max_length=1, choices=[('x', 'other'), ('c', 'create'), ('u', 'update'), ('d', 'delete'), ('m', 'message'), ('a', 'comment')])),
				('level', models.IntegerField(default=20)),
				('message', models.TextField()),
				('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
				('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True, on_delete=models.CASCADE)),
			],
		),
		migrations.CreateModel(
			name='Inbox',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('readed', models.BooleanField(default=False)),
				('event', models.ForeignKey(to='notifications.Event', on_delete=models.CASCADE)),
				('recipient', models.ForeignKey(related_name='inbox', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
		),
		migrations.AlterIndexTogether(
			name='event',
			index_together=set([('object_id', 'content_type', 'action', 'level')]),
		),
	]
