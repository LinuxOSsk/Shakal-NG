# -*- coding: utf-8 -*-
from django.db import migrations, models
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
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=100)),
				('slug', django_autoslugfield.fields.AutoSlugField(title_field='title', unique=True)),
				('original_description', rich_editor.fields.RichTextOriginalField(max_length=1000, property_name='description', filtered_field='filtered_description', blank=True)),
				('filtered_description', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_sidebar', rich_editor.fields.RichTextOriginalField(max_length=1000, property_name='sidebar', filtered_field='filtered_sidebar', blank=True)),
				('filtered_sidebar', rich_editor.fields.RichTextFilteredField(editable=False)),
				('author', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'blog',
				'verbose_name_plural': 'blogy',
			},
		),
		migrations.CreateModel(
			name='Post',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=100)),
				('slug', django_autoslugfield.fields.AutoSlugField(in_respect_to=('blog',), title_field='title')),
				('original_perex', rich_editor.fields.RichTextOriginalField(max_length=1000, property_name='perex', filtered_field='filtered_perex')),
				('filtered_perex', rich_editor.fields.RichTextFilteredField(editable=False)),
				('original_content', rich_editor.fields.RichTextOriginalField(max_length=100000, property_name='content', filtered_field='filtered_content')),
				('filtered_content', rich_editor.fields.RichTextFilteredField(editable=False)),
				('pub_time', models.DateTimeField(db_index=True)),
				('linux', models.BooleanField(default=False)),
				('blog', models.ForeignKey(to='blog.Blog', on_delete=models.CASCADE)),
			],
			options={
				'ordering': ('-pub_time',),
				'verbose_name': 'z\xe1pis',
				'verbose_name_plural': 'z\xe1pisy',
			},
		),
		migrations.AlterUniqueTogether(
			name='post',
			unique_together=set([('blog', 'slug')]),
		),
	]
