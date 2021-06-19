# -*- coding: utf-8 -*-
from django.db import migrations, models
from django.conf import settings
import rich_editor.fields
import autoimagefield.fields


class Migration(migrations.Migration):

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Desktop',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('title', models.CharField(max_length=255)),
				('image', autoimagefield.fields.AutoImageField(upload_to='desktops')),
				('original_text', rich_editor.fields.RichTextOriginalField(max_length=10000, property_name='text', filtered_field='filtered_text')),
				('filtered_text', rich_editor.fields.RichTextFilteredField(editable=False)),
				('author', models.ForeignKey(related_name='my_desktops', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'desktop',
				'verbose_name_plural': 'desktopy',
			},
		),
		migrations.CreateModel(
			name='FavoriteDesktop',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('desktop', models.ForeignKey(to='desktops.Desktop', on_delete=models.CASCADE)),
				('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
		),
		migrations.AddField(
			model_name='desktop',
			name='favorited',
			field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='desktops.FavoriteDesktop'),
		),
		migrations.AlterUniqueTogether(
			name='favoritedesktop',
			unique_together=set([('desktop', 'user')]),
		),
	]
