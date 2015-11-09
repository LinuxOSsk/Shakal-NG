# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
			name='Blog',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(auto_now_add=True)),
				('updated', models.DateTimeField(auto_now=True)),
				('title', models.CharField(max_length=100, verbose_name='title')),
				('slug', django_autoslugfield.fields.AutoSlugField(unique=True)),
				('original_description', rich_editor.fields.RichTextOriginalField(max_length=1000, verbose_name='description', property_name='description', filtered_field='filtered_description')),
				('filtered_description', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_sidebar', rich_editor.fields.RichTextOriginalField(max_length=1000, verbose_name='sidebar', property_name='sidebar', filtered_field='filtered_sidebar')),
				('filtered_sidebar', rich_editor.fields.RichTextFilteredField(editable=False)),
				('author', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
			],
			options={
				'verbose_name': 'blog',
				'verbose_name_plural': 'blogy',
			},
		),
		migrations.CreateModel(
			name='Post',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('title', models.CharField(max_length=100, verbose_name='title')),
				('slug', django_autoslugfield.fields.AutoSlugField()),
				('original_perex', rich_editor.fields.RichTextOriginalField(max_length=1000, verbose_name='perex', property_name='perex', filtered_field='filtered_perex')),
				('filtered_perex', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_content', rich_editor.fields.RichTextOriginalField(max_length=100000, verbose_name='content', property_name='content', filtered_field='filtered_content')),
				('filtered_content', rich_editor.fields.RichTextFilteredField(editable=False)),
				('pub_time', models.DateTimeField(verbose_name='publication date', db_index=True)),
				('created', models.DateTimeField(auto_now_add=True)),
				('updated', models.DateTimeField(auto_now=True)),
				('linux', models.BooleanField(default=False, verbose_name='linux blog')),
				('blog', models.ForeignKey(to='blog.Blog')),
			],
			options={
				'ordering': ('-pub_time',),
				'verbose_name': 'pr\xedspevok blogu',
				'verbose_name_plural': 'pr\xedspevky blogu',
			},
		),
		migrations.AlterUniqueTogether(
			name='post',
			unique_together=set([('blog', 'slug')]),
		),
	]
