# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('attachment', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='attachment',
			name='is_visible',
			field=models.BooleanField(default=True, blank=True),
		),
	]
