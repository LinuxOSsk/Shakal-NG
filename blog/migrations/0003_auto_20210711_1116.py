# Generated by Django 3.2.4 on 2021-07-11 09:16

import autoimagefield.fields
from django.db import migrations


class Migration(migrations.Migration):

	dependencies = [
		('blog', '0002_auto_20170603_1644'),
	]

	operations = [
		migrations.AddField(
			model_name='blog',
			name='image',
			field=autoimagefield.fields.AutoImageField(blank=True, upload_to='blog/info/images'),
		),
		migrations.AddField(
			model_name='post',
			name='image',
			field=autoimagefield.fields.AutoImageField(blank=True, upload_to='blog/title/images'),
		),
	]