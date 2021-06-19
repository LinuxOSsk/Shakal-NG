# -*- coding: utf-8 -*-
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS

from common_utils.admin_widgets import RichEditorWidget
from rich_editor.fields import RichTextOriginalField


FORMFIELD_FOR_DBFIELD_DEFAULTS[RichTextOriginalField] = {'widget': RichEditorWidget}
