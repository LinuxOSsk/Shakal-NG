from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models


class UserProfileManager(models.Manager):
	def get_query_set(self):
		return  super(UserProfileManager, self).get_query_set().select_related(depth = 1)

class UserProfile(models.Model):
	objects = UserProfileManager()
	user = models.OneToOneField(User, name = _('user'))
	pass_reset = models.DateTimeField(_('password reset date'), null = True, blank = True)
	signature = models.CharField(_('signature'), max_length = 100, null = True, blank = True)
	distribution = models.CharField(_('distribution'), max_length = 30, null = True, blank = True)
	info = models.TextField(_('informations'), null = True, blank = True)
	birth_year = models.IntegerField(_('birth year'), null = True, blank = True)

	def __unicode__(self):
		return unicode(self.user)
