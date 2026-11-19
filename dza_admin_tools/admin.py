"""
Trang "Django commands" trong Django admin (chỉ superuser): liệt kê command trong allowlist
settings.DZA_ADMIN_COMMANDS["ALLOWED"], form tham số sinh từ argparse, chạy ngay. Logic ở services.py.
Cài vào site bằng cách wrap get_urls / get_app_list (gọi từ AppConfig.ready), không cần sửa urls.py.

Port từ dza_rest_utils/admin_commands.py cho Django 2.2: không htmx/modal, dùng trang form + trang kết quả.
"""
import io
import mimetypes
import re
from dataclasses import dataclass, field

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View

from dza_admin_tools.services import (
    FieldSpec,
    build_argv,
    get_allowed_command,
    get_allowed_commands,
    get_setting,
    run_command,
    shell_join,
)

APP_LABEL = "dza_system_tools"
TEMPLATE_DIR = "dza_admin_tools/commands"

# Form gửi kèm token ngẫu nhiên; response file set cookie cùng giá trị để JS biết đã tải xong
DOWNLOAD_TOKEN_FIELD = "_dza_download_token"
DOWNLOAD_TOKEN_COOKIE = "dza_download_token"
DOWNLOAD_TOKEN_RE = re.compile(r"^[A-Za-z0-9]{1,40}$")

# Python 3.6 (production) không có sẵn .xlsx trong mimetypes, image slim cũng không có /etc/mime.types
mimetypes.add_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")

INVALID_FORM_MESSAGE = _("Please fix the errors below.")
FAILED_MESSAGE = _("Command %(name)s failed (exit code %(code)s).")
TIMED_OUT_MESSAGE = _("Command %(name)s was stopped after %(timeout)s seconds.")
SUCCESS_MESSAGE = _("Command %(name)s finished successfully.")


class AdminSiteViewMixin:
    """Context giống trang admin gốc (header, breadcrumbs) + chỉ superuser."""

    site = None
    title = ""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        request.current_app = self.site.name
        return super().dispatch(request, *args, **kwargs)

    def admin_context(self, **kwargs):
        return {**self.site.each_context(self.request), "title": self.title, **kwargs}


class CommandListView(AdminSiteViewMixin, TemplateView):
    template_name = "%s/index.html" % TEMPLATE_DIR
    title = _("Django commands")

    def get_context_data(self, **kwargs):
        return self.admin_context(
            commands=get_allowed_commands(),
            timeout_seconds=get_setting("TIMEOUT_SECONDS"),
            **super().get_context_data(**kwargs),
        )


@dataclass
class BoundField:
    field: FieldSpec
    value: str = ""
    checked: bool = False
    errors: list = field(default_factory=list)


class CommandRunView(AdminSiteViewMixin, View):
    """GET: form tham số. POST: chạy command, hiện kết quả."""

    form_template = "%s/run_form.html" % TEMPLATE_DIR
    result_template = "%s/run_result.html" % TEMPLATE_DIR

    def get_command(self, name):
        command = get_allowed_command(name)
        if command is None or not command.runnable:
            raise Http404
        return command

    def render_form(self, command, bound_fields, status=200):
        self.title = _("Run command %(name)s") % {"name": command.name}
        context = self.admin_context(
            command=command,
            bound_fields=bound_fields,
            timeout_seconds=get_setting("TIMEOUT_SECONDS"),
        )
        return TemplateResponse(self.request, self.form_template, context, status=status)

    def get(self, request, name):
        command = self.get_command(name)
        return self.render_form(command, [BoundField(spec, value=spec.initial) for spec in command.fields])

    def post(self, request, name):
        command = self.get_command(name)
        built = build_argv(command, request.POST)
        if built.errors:
            bound_fields = [
                BoundField(
                    spec,
                    value="" if spec.secret else request.POST.get(spec.dest, ""),
                    checked=bool(request.POST.get(spec.dest)),
                    errors=built.errors.get(spec.dest, []),
                )
                for spec in command.fields
            ]
            messages.error(request, INVALID_FORM_MESSAGE)
            return self.render_form(command, bound_fields, status=422)

        result = run_command(command, built, user=request.user)
        messages.add_message(request, *self.result_message(command, result))
        if result.succeeded and result.output_file:
            return self.file_response(request, result.output_file)
        self.title = _("Result of %(name)s") % {"name": command.name}
        context = self.admin_context(
            command=command,
            result=result,
            command_line=shell_join(["manage.py", command.name, *built.display_argv]),
        )
        return TemplateResponse(request, self.result_template, context)

    @staticmethod
    def file_response(request, output_file):
        """Trả file cho trình duyệt tải ngay; cookie token báo cho JS ở form biết đã tải xong (bật lại nút Run)."""
        content_type = mimetypes.guess_type(output_file.name)[0] or "application/octet-stream"
        response = FileResponse(
            io.BytesIO(output_file.content), as_attachment=True, filename=output_file.name, content_type=content_type,
        )
        token = request.POST.get(DOWNLOAD_TOKEN_FIELD, "")
        if DOWNLOAD_TOKEN_RE.match(token):
            response.set_cookie(DOWNLOAD_TOKEN_COOKIE, token, max_age=120, samesite="Lax")
        return response

    @staticmethod
    def result_message(command, result):
        if result.timed_out:
            timeout = get_setting("TIMEOUT_SECONDS")
            return messages.WARNING, TIMED_OUT_MESSAGE % {"name": command.name, "timeout": timeout}
        if result.succeeded:
            return messages.SUCCESS, SUCCESS_MESSAGE % {"name": command.name}
        return messages.ERROR, FAILED_MESSAGE % {"name": command.name, "code": result.exit_code}


def _tools_app(site):
    url = reverse("admin:dza_commands", current_app=site.name)
    return {
        "name": _("System tools"),
        "app_label": APP_LABEL,
        "app_url": url,
        "has_module_perms": True,
        "models": [{
            "name": _("Django commands"),
            "object_name": "DjangoCommand",
            "perms": {"add": False, "change": False, "delete": False, "view": True},
            "admin_url": url,
            "add_url": None,
            "view_only": True,
        }],
    }


def install_admin_commands(site):
    if getattr(site.get_urls, "dza_admin_commands", False):
        return
    original_get_urls = site.get_urls
    original_get_app_list = site.get_app_list

    def get_urls():
        list_view = CommandListView.as_view(site=site)
        run_view = CommandRunView.as_view(site=site)
        return [
            path("dza-commands/", site.admin_view(list_view), name="dza_commands"),
            path("dza-commands/<str:name>/run/", site.admin_view(run_view), name="dza_commands_run"),
        ] + original_get_urls()

    def get_app_list(request):  # Django 2.2: không có tham số app_label
        app_list = original_get_app_list(request)
        if request.user.is_active and request.user.is_superuser:
            app_list = [*app_list, _tools_app(site)]
        return app_list

    get_urls.dza_admin_commands = True
    site.get_urls = get_urls
    site.get_app_list = get_app_list
