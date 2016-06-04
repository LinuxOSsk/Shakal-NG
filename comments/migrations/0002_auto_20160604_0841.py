# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('comments', '0001_initial'),
	]

	operations = [
		migrations.AlterField(
			model_name='comment',
			name='object_id',
			field=models.PositiveIntegerField(verbose_name='ID objektu'),
		),
	]
