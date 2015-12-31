# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

	dependencies = [
		('article', '0001_initial'),
	]

	operations = [
		migrations.AlterField(
			model_name='article',
			name='pub_time',
			field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='\u010das publik\xe1cie', db_index=True),
		),
	]
