# -*- coding: utf-8 -*-
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
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('password', models.CharField(max_length=128)),
				('last_login', models.DateTimeField(null=True, blank=True)),
				('is_superuser', models.BooleanField(default=False)),
				('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True)),
				('first_name', models.CharField(max_length=30, blank=True)),
				('last_name', models.CharField(max_length=30, blank=True)),
				('email', models.EmailField(max_length=254, blank=True)),
				('is_staff', models.BooleanField(default=False)),
				('is_active', models.BooleanField(default=True)),
				('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
				('jabber', models.CharField(max_length=127, blank=True)),
				('url', models.CharField(max_length=255, blank=True)),
				('signature', models.CharField(max_length=255, blank=True)),
				('display_mail', models.BooleanField(default=False)),
				('distribution', models.CharField(max_length=50, blank=True)),
				('original_info', rich_editor.fields.RichTextOriginalField(blank=True, property_name='info', filtered_field='filtered_info', validators=[django.core.validators.MaxLengthValidator(1000000)])),
				('filtered_info', rich_editor.fields.RichTextFilteredField(editable=False, blank=True)),
				('year', models.SmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2015)])),
				('avatar', autoimagefield.fields.AutoImageField(upload_to='accounts/avatars', blank=True)),
				('settings', models.TextField(blank=True)),
				('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True)),
				('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True)),
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
				('user', models.ForeignKey(related_name='remember_me_tokens', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
		),
		migrations.CreateModel(
			name='UserRating',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('comments', models.IntegerField(default=0)),
				('articles', models.IntegerField(default=0)),
				('helped', models.IntegerField(default=0)),
				('news', models.IntegerField(default=0)),
				('wiki', models.IntegerField(default=0)),
				('rating', models.IntegerField(default=0)),
				('user', models.OneToOneField(related_name='rating', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
			],
		),
	]
