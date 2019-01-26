# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum, Count, Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.urls import reverse


class StatisticsQuerySet(models.QuerySet):
	def refresh_statistics(self):
		rating_total = Subquery(Rating.objects
			.filter(statistics=OuterRef('pk'))
			.values('statistics')
			.order_by('statistics')
			.annotate(computed_value=Sum('value'))
			.values('computed_value')[:1])
		rating_count = Subquery(Rating.objects
			.filter(statistics=OuterRef('pk'))
			.values('statistics')
			.order_by('statistics')
			.annotate(computed_value=Count('value'))
			.values('computed_value')[:1])
		solution_count = Subquery(Rating.objects
			.filter(statistics=OuterRef('pk'))
			.values('statistics')
			.order_by('statistics')
			.annotate(computed_value=Count('marked_solution', filter=Q(marked_solution=True)))
			.values('computed_value')[:1])
		flag_count = Subquery(Rating.objects
			.filter(statistics=OuterRef('pk'))
			.values('statistics')
			.order_by('statistics')
			.annotate(computed_value=Count('marked_flag', filter=~Q(marked_flag='')))
			.values('computed_value')[:1])
		return self.update(
			rating_total=Coalesce(rating_total, 0),
			rating_count=Coalesce(rating_count, 0),
			solution_count=Coalesce(solution_count, 0),
			flag_count=Coalesce(flag_count, 0),
		)

	def get_statistics(self, instance):
		content_type = ContentType.objects.get_for_model(instance.__class__)
		object_id = instance.pk
		stat = Statistics.objects.filter(content_type=content_type, object_id=object_id).first()
		if stat is None:
			return Statistics(content_type=content_type, object_id=object_id)
		else:
			return stat


class Statistics(models.Model):
	objects = StatisticsQuerySet.as_manager()

	content_type = models.ForeignKey(
		ContentType,
		verbose_name="typ obsahu",
		on_delete=models.PROTECT
	)
	object_id = models.PositiveIntegerField(
		"ID objektu"
	)
	content_object = GenericForeignKey('content_type', 'object_id')

	rating_total = models.IntegerField(
		"Celkové hodnotenie",
		default=0
	)
	rating_count = models.IntegerField(
		"Počet hodnotiacich hlasov",
		default=0
	)
	solution_count = models.IntegerField(
		"Počet označení ako riešenie",
		default=0
	)
	flag_count = models.IntegerField(
		"Počet označení ako flag",
		default=0
	)

	class Meta:
		verbose_name = "Štatistika hodnotenia"
		verbose_name_plural = "Štatistiky hodnotenia"
		unique_together = (('content_type', 'object_id',),)


class RatingManager(models.Manager):
	def rate(self, instance, user, value=None, marked_solution=None, marked_flag=None, comment=None):
		defaults = {}
		if value is not None:
			if value is False:
				defaults['value'] = None
			else:
				defaults['value'] = value
		if marked_solution is not None:
			defaults['marked_solution'] = marked_solution
		if marked_flag is not None:
			defaults['marked_flag'] = marked_flag
		if comment is not None:
			defaults['comment'] = comment

		content_type = ContentType.objects.get_for_model(instance.__class__)
		object_id = instance.pk
		statistics = Statistics.objects.get_or_create(content_type=content_type, object_id=object_id)[0]
		rating = Rating.objects.update_or_create(
			statistics=statistics,
			user=user,
			defaults=defaults
		)[0]
		Statistics.objects.filter(pk=statistics.pk).refresh_statistics()
		return rating

	def get_rating(self, instance, user):
		content_type = ContentType.objects.get_for_model(instance.__class__)
		object_id = instance.pk
		return Rating.objects.get(
			statistics__content_type=content_type,
			statistics__object_id=object_id,
			user=user
		)


class Rating(models.Model):
	objects = RatingManager()

	FLAG_NONE = ''
	FLAG_SPAM = 's'
	FLAG_VULGARISM = 'v'
	FLAG_OTHER = 'x'
	FLAG_CHOICES = (
		(FLAG_NONE, "Príspevok je v poriadku"),
		(FLAG_SPAM, "Spam"),
		(FLAG_VULGARISM, "Vulgarizmus"),
		(FLAG_OTHER, "Iné"),
	)

	statistics = models.ForeignKey(
		Statistics,
		verbose_name="Hodnotený objekt",
		on_delete=models.CASCADE,
		related_name='rating_set'
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name="Používateľ",
		on_delete=models.CASCADE,
		related_name='object_ratings'
	)
	value = models.SmallIntegerField(
		"Hodnotenie",
		blank=True,
		null=True
	)
	marked_solution = models.BooleanField(
		"Označené hodnotenie",
		default=False
	)
	marked_flag = models.CharField(
		"Označené",
		blank=True,
		default='',
		max_length=1,
		choices=FLAG_CHOICES
	)
	comment = models.TextField(
		"Komentár",
		blank=True,
		default='',
	)

	def get_absolute_url(self):
		return reverse('rating:ratings', kwargs={'pk': self.pk})

	class Meta:
		verbose_name = "Hodnotenie"
		verbose_name_plural = "Hodnotenia"
		unique_together = (('statistics', 'user',),)
