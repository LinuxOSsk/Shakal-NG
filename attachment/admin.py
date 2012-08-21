# -*- coding: utf-8 -*-

from django.contrib import admin
from attachment.models import Attachment

class AttachmentAdmin(admin.ModelAdmin):
	exclude = ('size', )

admin.site.register(Attachment, AttachmentAdmin)
