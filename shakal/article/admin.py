from django.contrib import admin
from django.db import models
from shakal.article.models import Category, Article
from django.utils.translation import ugettext_lazy as _

#class VerboseForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
#	def label_for_value(self, value):
#		key = self.rel.get_related_field().name
#		try:
#			obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
#			change_url = reverse(
#				"admin:%s_%s_change" % (obj._meta.app_label, obj._meta.object_name.lower()),
#				args=(obj.pk,)
#			)
#			return '&nbsp;<strong><a href="%s">%s</a></strong>' % (change_url, escape(obj))
#		except (ValueError, self.rel.to.DoesNotExist):
#			return ''

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', )
	search_fields = ('name', 'slug', )
	prepopulated_fields = {'slug': ('name', )}

class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'pubtime', 'category', 'published', )
	list_filter = ('pubtime', 'category', 'published', )
	search_fields = ('title', 'anotation', 'article', )
	prepopulated_fields = {'slug': ('title', )}
	raw_id_fields = ('author', )
	#formfield_overrides = {
	#	models.ForeignKey: {'widget': VerboseForeignKeyRawIdWidget(Article._meta.get_field('author').rel) },
	#}

#class ArticleAdminForm(forms.ModelForm):
#	class Meta:
#		model = Article
#		widgets = { 'author': VerboseForeignKeyRawIdWidget(Article._meta.get_field('author').rel) }

admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
