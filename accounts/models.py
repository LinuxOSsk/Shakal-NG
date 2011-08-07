from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models


class UserProfileManager(models.Manager):
	def get_query_set(self):
		return  super(UserProfileManager, self).get_query_set().select_related(depth = 1)

class UserProfile(models.Model):
	objects = UserProfileManager()
	user = models.OneToOneField(User)
	user.verbose_name = _('User')
	pass_reset = models.DateTimeField(null = True, blank = True)
	pass_reset.verbose_name = _('Password reset date')
	signature = models.CharField(max_length = 100, null = True, blank = True)
	signature.verbose_name = _('Signature')
	distribution = models.CharField(max_length = 30, null = True, blank = True)
	distribution.verbose_name = _('Distribution')
	info = models.TextField(null = True, blank = True)
	info.verbose_name = _('Informations')
	birth_year = models.IntegerField(null = True, blank = True)
	birth_year.verbose_name = _('Birth year')

	def __unicode__(self):
		return unicode(self.user)
