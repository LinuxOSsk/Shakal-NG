# Generated by Django 4.2.11 on 2024-04-06 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('wiki', '0003_auto_20210619_0756'),
	]

	operations = [
		migrations.AlterIndexTogether(
			name='page',
			index_together=set(),
		),
		migrations.AlterField(
			model_name='page',
			name='parent',
			field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='wiki.page'),
		),
		migrations.RemoveField(
			model_name='page',
			name='level',
		),
		migrations.RemoveField(
			model_name='page',
			name='lft',
		),
		migrations.RemoveField(
			model_name='page',
			name='rght',
		),
		migrations.RemoveField(
			model_name='page',
			name='tree_id',
		),
	]
