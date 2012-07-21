# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	jabber = models.CharField(max_length = 127, blank = True)
	url = models.CharField(max_length = 255, blank = True)
	display_mail = models.BooleanField(default = False, verbose_name = _('display mail'))
	last_password_reset = models.DateTimeField(blank = True, verbose_name = _('password reset date'))
	distribution = models.CharField(max_length = 50, blank = True, verbose_name = _('linux distribution'))
	info = models.TextField(validators = [MaxLengthValidator(100000)], blank = True, verbose_name = _('informations'))
	year = models.SmallIntegerField(validators = [MinValueValidator(1900), MaxValueValidator(lambda: 2000)], blank = True, verbose_name = _('year of birth'))
