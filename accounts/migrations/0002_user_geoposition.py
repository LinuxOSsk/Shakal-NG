# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_geoposition_field.fields


class Migration(migrations.Migration):

	dependencies = [
		('accounts', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='user',
			name='geoposition',
			field=django_geoposition_field.fields.GeopositionField(max_length=100, verbose_name='poloha', blank=True),
		),
	]
