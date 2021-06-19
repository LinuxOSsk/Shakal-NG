# -*- coding: utf-8 -*-
from django.db import migrations, models
from django.conf import settings
import rich_editor.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Section',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('name', models.CharField(max_length=255)),
				('slug', models.SlugField(unique=True)),
				('description', models.TextField(verbose_name='popis')),
			],
			options={
				'verbose_name': 'sekcia',
				'verbose_name_plural': 'sekcie',
			},
		),
		migrations.CreateModel(
			name='Topic',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=100)),
				('original_text', rich_editor.fields.RichTextOriginalField(max_length=3000, property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('authors_name', models.CharField(max_length=50)),
				('is_removed', models.BooleanField(default=False)),
				('is_resolved', models.BooleanField(default=False)),
				('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
				('section', models.ForeignKey(to='forum.Section', on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 't\xe9ma vo f\xf3re',
				'verbose_name_plural': 't\xe9my vo f\xf3re',
			},
		),
	]
