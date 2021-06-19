# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

	dependencies = [
		('contenttypes', '0002_remove_content_type_name'),
	]

	operations = [
		migrations.CreateModel(
			name='HitCount',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('hits', models.PositiveIntegerField(default=0)),
				('object_id', models.PositiveIntegerField()),
				('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
			],
		),
		migrations.AlterUniqueTogether(
			name='hitcount',
			unique_together=set([('content_type', 'object_id')]),
		),
	]
