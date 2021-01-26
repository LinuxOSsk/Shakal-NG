# -*- coding: utf-8 -*-
from django.core import validators


class UsernameValidator(validators.RegexValidator):
	regex = r'^([\w]+[ ]?)*[\w]$'
	message = "Toto pole môže obsahovať maximálne jednu medzeru v strede."


username_validators = [UsernameValidator()]
