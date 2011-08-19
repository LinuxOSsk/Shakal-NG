from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from shakal.account.models import UserProxy

class Category(models.Model):
	name = models.CharField(_('name'), max_length = 50)
	slug = models.SlugField(_('slug'))

	def __unicode__(self):
		return unicode(self.name)

	class Meta():
		verbose_name = _('category')
		verbose_name_plural = _('categories')

class ArticleManager(models.Manager):
	def get_query_set(self):
		return super(ArticleManager, self).get_query_set().select_related('author', 'category')

class Article(models.Model):
	title = models.CharField(_('title'), max_length = 250)
	slug = models.SlugField(_('slug'))
	author = models.ForeignKey(UserProxy, null = True, blank = True)
	author.verbose_name = _('author')
	pubtime = models.DateTimeField(_('publication date'))
	category = models.ForeignKey(Category, null = True, blank = True)
	category.verbose_name = _('category')
	published = models.BooleanField(_('published'))
	anotation = models.TextField(_('anotation'))
	article = models.TextField(_('article'))

	objects = ArticleManager()

	def __unicode__(self):
		return unicode(self.title)

	@permalink
	def get_absolute_url(self):
		return ('article_detail', None, { 'slug': self.slug })

	class Meta():
		verbose_name = _('article')
		verbose_name_plural = _('articles')

