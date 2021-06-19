# -*- coding: utf-8 -*-
from django.db import migrations, models
import mptt.fields
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
			name='Comment',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('object_id', models.PositiveIntegerField(verbose_name='ID objektu')),
				('subject', models.CharField(max_length=100)),
				('user_name', models.CharField(max_length=50, blank=True)),
				('original_comment', rich_editor.fields.RichTextOriginalField(max_length=50000, property_name='comment', filtered_field='filtered_comment')),
				('filtered_comment', rich_editor.fields.RichTextFilteredField(editable=False)),
				('ip_address', models.GenericIPAddressField(null=True, blank=True)),
				('is_public', models.BooleanField(default=True)),
				('is_removed', models.BooleanField(default=False)),
				('is_locked', models.BooleanField(default=False)),
				('lft', models.PositiveIntegerField(editable=False, db_index=True)),
				('rght', models.PositiveIntegerField(editable=False, db_index=True)),
				('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
				('level', models.PositiveIntegerField(editable=False, db_index=True)),
				('content_type', models.ForeignKey(related_name='content_type_set_for_comment', to='contenttypes.ContentType', on_delete=models.CASCADE)),
				('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='comments.Comment', null=True, on_delete=models.CASCADE)),
				('user', models.ForeignKey(related_name='comment_comments', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
			],
			options={
				'ordering': ('tree_id', 'lft'),
				'verbose_name': 'koment\xe1r',
				'verbose_name_plural': 'koment\xe1re',
			},
		),
		migrations.CreateModel(
			name='CommentFlag',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('flag', models.CharField(max_length=30, db_index=True)),
				('flag_date', models.DateTimeField(default=None)),
				('comment', models.ForeignKey(related_name='flags', to='comments.Comment', on_delete=models.CASCADE)),
				('user', models.ForeignKey(related_name='threadedcomment_flags', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'zna\u010dka komen\xe1ra',
				'verbose_name_plural': 'zna\u010dky koment\xe1rov',
			},
		),
		migrations.CreateModel(
			name='RootHeader',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('pub_date', models.DateTimeField(db_index=True)),
				('last_comment', models.DateTimeField(db_index=True)),
				('comment_count', models.PositiveIntegerField(default=0, db_index=True)),
				('is_locked', models.BooleanField(default=False)),
				('object_id', models.PositiveIntegerField()),
				('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
			],
			options={
				'verbose_name': 'diskusia',
				'verbose_name_plural': 'diskusie',
			},
		),
		migrations.CreateModel(
			name='UserDiscussionAttribute',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('time', models.DateTimeField(null=True, blank=True)),
				('watch', models.BooleanField(default=False)),
				('discussion', models.ForeignKey(to='comments.RootHeader', on_delete=models.CASCADE)),
				('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
		),
		migrations.AlterUniqueTogether(
			name='userdiscussionattribute',
			unique_together=set([('user', 'discussion')]),
		),
		migrations.AlterUniqueTogether(
			name='rootheader',
			unique_together=set([('content_type', 'object_id')]),
		),
		migrations.AlterUniqueTogether(
			name='commentflag',
			unique_together=set([('user', 'comment', 'flag')]),
		),
		migrations.AlterIndexTogether(
			name='comment',
			index_together=set([('object_id', 'content_type')]),
		),
	]
