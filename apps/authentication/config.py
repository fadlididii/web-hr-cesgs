# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = 'apps.auth'
    label = 'apps_auth'
    
    def ready(self):
        import apps.authentication.signals
