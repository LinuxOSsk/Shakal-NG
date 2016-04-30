# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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


class NodeAdmin(admin.ModelAdmin):
	list_display = ('title', 'vocabulary', 'is_published',)
	raw_id_fields = ('author',)
	inlines = (NodeRevisionInline,)

	def get_queryset(self, request):
		return super(NodeAdmin, self).get_queryset(request).select_related('vocabulary')


admin.site.register(VocabularyNodeType, VocabularyNodeTypeAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(Node, NodeAdmin)
