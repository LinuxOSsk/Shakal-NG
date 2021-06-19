# -*- coding: utf-8 -*-
from django.db import migrations, models
import autoimagefield.fields


class Migration(migrations.Migration):

	dependencies = [
		('article', '0002_auto_20151231_1734'),
	]

	operations = [
		migrations.CreateModel(
			name='Series',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('created', models.DateTimeField(editable=False)),
				('updated', models.DateTimeField(editable=False)),
				('name', models.CharField(max_length=100)),
				('slug', models.SlugField(unique=True)),
				('image', autoimagefield.fields.AutoImageField(upload_to='article/thumbnails', blank=True)),
				('description', models.TextField(verbose_name='popis')),
			],
			options={
				'verbose_name': 'seri\xe1l',
				'verbose_name_plural': 'seri\xe1ly',
			},
		),
		migrations.CreateModel(
			name='SeriesArticle',
			fields=[
				('id', models.AutoField(serialize=False, auto_created=True, primary_key=True)),
				('article', models.OneToOneField(related_name='series', to='article.Article', on_delete=models.CASCADE)),
				('series', models.ForeignKey(to='article.Series', on_delete=models.CASCADE)),
			],
			options={
				'ordering': ('pk',),
				'verbose_name': 'seri\xe1lov\xfd \u010dl\xe1nok',
				'verbose_name_plural': 'seri\xe1lov\xe9 \u010dl\xe1nky',
			},
		),
	]
