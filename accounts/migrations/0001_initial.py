# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import rich_editor.fields
import autoimagefield.fields


class Migration(migrations.Migration):

	dependencies = [
		('auth', '0006_require_contenttypes_0002'),
	]

	operations = [
		migrations.CreateModel(
			name='User',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('password', models.CharField(max_length=128, verbose_name='password')),
				('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
				('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
				('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
				('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
				('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
				('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
				('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
				('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
				('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
				('jabber', models.CharField(max_length=127, blank=True)),
				('url', models.CharField(max_length=255, blank=True)),
				('signature', models.CharField(max_length=255, verbose_name='podpis', blank=True)),
				('display_mail', models.BooleanField(default=False, verbose_name='zobrazova\u0165 e-mail')),
				('distribution', models.CharField(max_length=50, verbose_name='linuxov\xe1 distrib\xfacia', blank=True)),
				('original_info', rich_editor.fields.RichTextOriginalField(blank=True, verbose_name='inform\xe1cie', property_name='info', filtered_field='filtered_info', validators=[django.core.validators.MaxLengthValidator(100000)])),
				('filtered_info', rich_editor.fields.RichTextFilteredField(editable=False, blank=True)),
				('year', models.SmallIntegerField(blank=True, null=True, verbose_name='rok narodenia', validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2015)])),
				('avatar', autoimagefield.fields.AutoImageField(upload_to='article/thumbnails', null=True, verbose_name='fotografia', blank=True)),
				('settings', models.TextField(verbose_name='nastavenia', blank=True)),
				('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
				('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
			],
			options={
				'db_table': 'auth_user',
				'verbose_name': 'pou\u017e\xedvate\u013e',
				'verbose_name_plural': 'pou\u017e\xedvatelia',
			},
			managers=[
				('objects', django.contrib.auth.models.UserManager()),
			],
		),
		migrations.CreateModel(
			name='RememberToken',
			fields=[
				('token_hash', models.CharField(max_length=255, serialize=False, primary_key=True)),
				('created', models.DateTimeField(auto_now_add=True)),
				('user', models.ForeignKey(related_name='remember_me_tokens', to=settings.AUTH_USER_MODEL)),
			],
		),
		migrations.CreateModel(
			name='UserRating',
			fields=[
				('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
				('comments', models.IntegerField(default=0)),
				('articles', models.IntegerField(default=0)),
				('helped', models.IntegerField(default=0)),
				('news', models.IntegerField(default=0)),
				('wiki', models.IntegerField(default=0)),
				('rating', models.IntegerField(default=0)),
				('user', models.OneToOneField(related_name='rating', to=settings.AUTH_USER_MODEL)),
			],
		),
	]
