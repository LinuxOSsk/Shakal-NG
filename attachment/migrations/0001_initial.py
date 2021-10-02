# -*- coding: utf-8 -*-
from django.db import migrations, models
import attachment.models


class Migration(migrations.Migration):

	dependencies = [
		('contenttypes', '0002_remove_content_type_name'),
	]

	operations = [
		migrations.CreateModel(
			name='Attachment',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('attachment', attachment.models.ThumbnailImageField(upload_to=attachment.models.upload_to)),
				('created', models.DateTimeField(auto_now_add=True)),
				('size', models.IntegerField(verbose_name='size')),
				('object_id', models.PositiveIntegerField()),
			],
			options={
				'verbose_name': 'attachment',
				'verbose_name_plural': 'attachments',
			},
		),
		migrations.CreateModel(
			name='UploadSession',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(auto_now_add=True)),
				('uuid', models.CharField(default=attachment.models.generate_uuid, unique=True, max_length=32)),
			],
		),
		migrations.CreateModel(
			name='AttachmentImage',
			fields=[
				('attachment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='attachment.Attachment', on_delete=models.CASCADE)),
				('width', models.IntegerField()),
				('height', models.IntegerField()),
			],
			bases=('attachment.attachment',),
		),
		migrations.AddField(
			model_name='attachment',
			name='content_type',
			field=models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE),
		),
	]
