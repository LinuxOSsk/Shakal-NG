# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import attachment.models


class Migration(migrations.Migration):

	dependencies = [
		('contenttypes', '0002_remove_content_type_name'),
	]

	operations = [
		migrations.CreateModel(
			name='AttachmentImageRaw',
			fields=[
				('attachment_ptr', models.PositiveIntegerField(serialize=False, primary_key=True, db_column='attachment_ptr_id')),
				('width', models.IntegerField()),
				('height', models.IntegerField()),
			],
			options={
				'db_table': 'attachment_attachmentimage',
				'managed': False,
			},
		),
		migrations.CreateModel(
			name='Attachment',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('attachment', attachment.models.ThumbnailImageField(upload_to=attachment.models.upload_to, verbose_name='attachment')),
				('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
				('size', models.IntegerField(verbose_name='size')),
				('object_id', models.PositiveIntegerField()),
			],
			options={
				'verbose_name': 'attachment',
				'verbose_name_plural': 'attachments',
			},
		),
		migrations.CreateModel(
			name='TemporaryAttachment',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('attachment', attachment.models.ThumbnailImageField(upload_to=attachment.models.upload_to, verbose_name='attachment')),
				('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
				('size', models.IntegerField(verbose_name='size')),
				('object_id', models.PositiveIntegerField()),
				('content_type', models.ForeignKey(to='contenttypes.ContentType')),
			],
			options={
				'abstract': False,
			},
		),
		migrations.CreateModel(
			name='UploadSession',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(auto_now_add=True)),
				('uuid', models.CharField(default=attachment.models.generate_uuid, unique=True, max_length=32)),
			],
		),
		migrations.CreateModel(
			name='AttachmentImage',
			fields=[
				('attachment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='attachment.Attachment')),
				('width', models.IntegerField()),
				('height', models.IntegerField()),
			],
			options={
				'abstract': False,
			},
			bases=('attachment.attachment',),
		),
		migrations.AddField(
			model_name='temporaryattachment',
			name='session',
			field=models.ForeignKey(to='attachment.UploadSession'),
		),
		migrations.AddField(
			model_name='attachment',
			name='content_type',
			field=models.ForeignKey(to='contenttypes.ContentType'),
		),
	]
