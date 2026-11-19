from django.apps import AppConfig


class DzaAdminToolsConfig(AppConfig):
    name = "dza_admin_tools"
    verbose_name = "System tools"

    def ready(self):
        from django.contrib import admin

        from dza_admin_tools.admin import install_admin_commands

        install_admin_commands(admin.site)
