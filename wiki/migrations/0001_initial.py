# -*- coding: utf-8 -*-
from django.db import models, migrations
import django_autoslugfield.fields
from django.conf import settings
import rich_editor.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Page',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=255)),
				('slug', django_autoslugfield.fields.AutoSlugField(title_field='title', unique=True)),
				('original_text', rich_editor.fields.RichTextOriginalField(property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('page_type', models.CharField(default='p', max_length=1, choices=[('h', 'Domovsk\xe1 str\xe1nka'), ('i', 'Intern\xe1 str\xe1nka'), ('p', 'Str\xe1nka wiki')])),
				('lft', models.PositiveIntegerField(editable=False, db_index=True)),
				('rght', models.PositiveIntegerField(editable=False, db_index=True)),
				('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
				('level', models.PositiveIntegerField(editable=False, db_index=True)),
				('last_author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
				('parent', models.ForeignKey(related_name='children', blank=True, to='wiki.Page', null=True, on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'Wiki str\xe1nka',
				'verbose_name_plural': 'Wiki str\xe1nky',
			},
		),
	]
