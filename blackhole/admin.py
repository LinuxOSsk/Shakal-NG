# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import VocabularyNodeType, Term, Node, NodeRevision


class VocabularyNodeTypeAdmin(admin.ModelAdmin):
	list_display = ('name',)


class TermAdmin(MPTTModelAdmin):
	list_display = ('name', 'vocabulary',)

	def get_queryset(self, request):
		return super(TermAdmin, self).get_queryset(request).select_related('vocabulary')


class NodeRevisionInline(admin.StackedInline):
	model = NodeRevision
	raw_id_fields = ('author',)
	extra = 0


class NodeAdmin(admin.ModelAdmin):
	list_display = ('title', 'node_type', 'is_published',)
	raw_id_fields = ('author',)
	list_filter = ('node_type', 'terms')
	inlines = (NodeRevisionInline,)


admin.site.register(VocabularyNodeType, VocabularyNodeTypeAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(Node, NodeAdmin)
