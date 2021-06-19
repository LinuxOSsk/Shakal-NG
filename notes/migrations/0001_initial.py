# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import rich_editor.fields


class Migration(migrations.Migration):

	dependencies = [
		('contenttypes', '0002_remove_content_type_name'),
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Note',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('object_id', models.PositiveIntegerField(verbose_name='id objektu')),
				('subject', models.CharField(max_length=100)),
				('authors_name', models.CharField(max_length=255)),
				('original_text', rich_editor.fields.RichTextOriginalField(max_length=20000, property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
				('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'pozn\xe1mka',
				'verbose_name_plural': 'pozn\xe1mky',
			},
		),
	]
