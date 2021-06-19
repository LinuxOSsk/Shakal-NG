# -*- coding: utf-8 -*-
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
			field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
		),
	]
