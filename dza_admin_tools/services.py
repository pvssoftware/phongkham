"""
Liệt kê / chạy management command từ Django admin (chỉ superuser). Cấu hình: settings.DZA_ADMIN_COMMANDS,
xem dza_admin_tools/README.md. Chỉ command trong allowlist ALLOWED mới hiện / chạy được.

Port từ dza_rest_utils/services/admin_commands.py cho Python 3.9 + Django 2.2.
"""
import argparse
import logging
import os
import shlex
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Optional

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.management import get_commands, load_command_class
from django.utils.translation import gettext_lazy as _

from dza_admin_tools.command_utils import OUTPUT_DIR_ENV

logger = logging.getLogger("dza_admin_tools.commands")

PROG_NAME = "manage.py"
# Option chung của mọi BaseCommand: không hiện trên form / usage
COMMON_OPTION_DESTS = frozenset({
    "help", "version", "verbosity", "settings", "pythonpath", "traceback", "no_color", "force_color", "skip_checks",
})

DEFAULTS = {
    "ALLOWED": [],
    # request giữ tới khi command chạy xong: phải nhỏ hơn proxy_read_timeout của nginx (60s) và timeout gunicorn
    "TIMEOUT_SECONDS": 50,
    "MAX_OUTPUT_CHARS": 100_000,
}


def shell_join(args):
    """Tương đương shlex.join (chỉ có từ Python 3.8); production chạy Python 3.6."""
    return " ".join(shlex.quote(str(arg)) for arg in args)


def get_setting(name):
    raw = getattr(settings, "DZA_ADMIN_COMMANDS", None) or {}
    return raw.get(name, DEFAULTS[name])


class FieldKind:
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    CHECKBOX = "checkbox"
    PASSWORD = "password"


MASK = "***"
TRUNCATED_MARKER = "…\n"

REQUIRED_MESSAGE = _("This field is required.")
INVALID_NUMBER_MESSAGE = _("Enter a number.")
INVALID_DATE_MESSAGE = _("Enter a valid date (YYYY-MM-DD).")
INVALID_CHOICE_MESSAGE = _("Select a valid choice.")
INVALID_QUOTES_MESSAGE = _("Unbalanced quotes.")
DASH_VALUE_MESSAGE = _("Values of this option must not start with '-'.")

SECRET_DEST_MARKERS = ("password", "secret", "token")
NUMBER_TYPES = (int, float)


@dataclass
class FieldSpec:
    """Một input trên form, sinh từ một argparse action."""

    dest: str
    label: str
    kind: str
    option: Optional[str] = None  # None = positional
    required: bool = False
    multiple: bool = False  # nhiều giá trị, nhập cách nhau bởi dấu cách (shlex)
    choices: list = field(default_factory=list)
    initial: str = ""
    help: str = ""
    converter: Optional[object] = None  # argparse type dùng để kiểm tra giá trị (số / ngày)
    action_appends: bool = False

    @property
    def secret(self):
        return self.kind == FieldKind.PASSWORD


def _is_multiple(action):
    return (
        action.nargs in ("*", "+", argparse.REMAINDER)
        or (isinstance(action.nargs, int) and action.nargs > 1)
        or isinstance(action, argparse._AppendAction)
    )


def _field_kind(action, multiple):
    if action.nargs == 0:
        return FieldKind.CHECKBOX
    if multiple:
        return FieldKind.TEXT
    if action.choices:
        return FieldKind.SELECT
    if any(marker in action.dest.lower() for marker in SECRET_DEST_MARKERS):
        return FieldKind.PASSWORD
    if action.type in NUMBER_TYPES:
        return FieldKind.NUMBER
    if getattr(action.type, "form_kind", None) == FieldKind.DATE:
        return FieldKind.DATE
    return FieldKind.TEXT


def _initial(action, kind):
    default = action.default
    if kind == FieldKind.CHECKBOX or default is None or default == argparse.SUPPRESS:
        return ""
    if isinstance(default, (list, tuple)):
        return shell_join(default)
    if hasattr(default, "isoformat"):
        return default.isoformat()
    return str(default)


def _help_text(parser, action):
    if not action.help or action.help == argparse.SUPPRESS:
        return ""
    try:
        return parser._get_formatter()._expand_help(action)
    except (KeyError, TypeError, ValueError):
        return action.help


def _option_string(action):
    if not action.option_strings:
        return None
    return next((option for option in action.option_strings if option.startswith("--")), action.option_strings[0])


def _own_actions(parser):
    return [action for action in parser._actions if action.dest not in COMMON_OPTION_DESTS]


def describe_fields(parser):
    fields = []
    for action in _own_actions(parser):
        multiple = _is_multiple(action)
        kind = _field_kind(action, multiple)
        option = _option_string(action)
        if option is None:
            required = action.nargs not in ("?", "*")
        else:
            required = bool(action.required)
        fields.append(FieldSpec(
            dest=action.dest,
            label=option or action.dest,
            kind=kind,
            option=option,
            required=required,
            multiple=multiple,
            choices=[str(choice) for choice in action.choices or []],
            initial=_initial(action, kind),
            help=_help_text(parser, action),
            converter=action.type if kind in (FieldKind.NUMBER, FieldKind.DATE) else None,
            action_appends=isinstance(action, argparse._AppendAction),
        ))
    return fields


@dataclass
class CommandInfo:
    name: str
    app: str
    help: str = ""
    usage: str = ""
    fields: list = field(default_factory=list)
    error: Optional[str] = None

    @property
    def runnable(self):
        return self.error is None


def _usage(parser, actions):
    formatter = parser._get_formatter()
    formatter.add_usage(parser.usage, actions, parser._mutually_exclusive_groups, prefix="")
    return " ".join(formatter.format_help().split())  # bỏ xuống dòng theo độ rộng terminal của argparse


def describe_command(name, app):
    try:
        command = load_command_class(app, name)
        parser = command.create_parser(PROG_NAME, name)
    except Exception as error:  # command hỏng không được làm sập cả trang
        return CommandInfo(name=name, app=app, error="%s: %s" % (type(error).__name__, error))
    return CommandInfo(
        name=name,
        app=app,
        help=str(command.help or ""),
        usage=_usage(parser, _own_actions(parser)),
        fields=describe_fields(parser),
    )


def get_allowed_commands():
    available = get_commands()
    return [describe_command(name, available[name]) for name in get_setting("ALLOWED") if name in available]


def get_allowed_command(name):
    """CommandInfo của command được phép, None nếu không có trong allowlist / không tồn tại."""
    available = get_commands()
    if name not in get_setting("ALLOWED") or name not in available:
        return None
    return describe_command(name, available[name])


@dataclass
class BuiltArgv:
    argv: list = field(default_factory=list)
    display_argv: list = field(default_factory=list)  # che giá trị secret, dùng để log / hiển thị
    errors: dict = field(default_factory=dict)  # dest -> [message]


class _FieldError(Exception):
    pass


def _check_value(spec, value):
    if spec.choices and value not in spec.choices:
        raise _FieldError(INVALID_CHOICE_MESSAGE)
    if spec.converter is not None:
        try:
            spec.converter(value)
        except (argparse.ArgumentTypeError, TypeError, ValueError):
            raise _FieldError(INVALID_DATE_MESSAGE if spec.kind == FieldKind.DATE else INVALID_NUMBER_MESSAGE)


def _clean_values(spec, raw):
    """Chuỗi form -> list giá trị đã kiểm tra (rỗng = không truyền)."""
    if spec.multiple:
        try:
            values = shlex.split(raw)
        except ValueError:
            raise _FieldError(INVALID_QUOTES_MESSAGE)
    else:
        value = raw if spec.secret else raw.strip()  # password giữ nguyên khoảng trắng
        values = [value] if value else []
    if not values:
        if spec.required:
            raise _FieldError(REQUIRED_MESSAGE)
        return []
    for value in values:
        _check_value(spec, value)
    return values


def _option_args(spec, values):
    """Dạng --opt=value để giá trị bắt đầu bằng '-' không bị argparse hiểu nhầm là option."""
    joiner = "=" if spec.option.startswith("--") else ""
    if not spec.multiple:
        return ["%s%s%s" % (spec.option, joiner, values[0])]
    if spec.action_appends:
        return ["%s%s%s" % (spec.option, joiner, value) for value in values]
    if any(value.startswith("-") for value in values):
        raise _FieldError(DASH_VALUE_MESSAGE)
    return [spec.option, *values]


def build_argv(command, data):
    """Dữ liệu form (QueryDict / dict) -> argv cho command; option trước, '--', rồi positional."""
    built = BuiltArgv()
    positionals, display_positionals = [], []
    for spec in command.fields:
        if spec.kind == FieldKind.CHECKBOX:
            if data.get(spec.dest):
                built.argv.append(spec.option)
                built.display_argv.append(spec.option)
            continue
        try:
            values = _clean_values(spec, data.get(spec.dest) or "")
            if not values:
                continue
            if spec.option is None:
                positionals += values
                display_positionals += [MASK] * len(values) if spec.secret else values
            else:
                args = _option_args(spec, values)
                built.argv += args
                built.display_argv += ["%s=%s" % (spec.option, MASK)] if spec.secret else args
        except _FieldError as error:
            built.errors[spec.dest] = [str(error)]
    if positionals:
        built.argv += ["--", *positionals]
        built.display_argv += ["--", *display_positionals]
    return built


@dataclass
class OutputFile:
    name: str
    content: bytes


@dataclass
class RunResult:
    exit_code: Optional[int]
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    duration: float = 0.0
    stdout_truncated: bool = False
    stderr_truncated: bool = False
    output_file: Optional[OutputFile] = None  # file command ghi vào OUTPUT_DIR_ENV (chỉ khi chạy thành công)

    @property
    def succeeded(self):
        return self.exit_code == 0 and not self.timed_out


def _as_text(output):
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output


def _tail(output, limit):
    output = _as_text(output)
    if len(output) <= limit:
        return output, False
    return TRUNCATED_MARKER + output[-limit:], True


def _read_output_file(output_dir, display):
    """Đúng 1 file trong output_dir -> OutputFile; không có / nhiều file -> None (trang kết quả như thường)."""
    names = sorted(name for name in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, name)))
    if len(names) != 1:
        if names:
            logger.warning("Admin command %s wrote %d files, expected at most 1; not returned.", display, len(names))
        return None
    with open(os.path.join(output_dir, names[0]), "rb") as file:
        return OutputFile(name=names[0], content=file.read())


def run_command(command, built, *, user):
    """
    Chạy `python -m django <name> <argv>` trong process riêng (argv list, không shell, có timeout).
    Mỗi lần chạy có một thư mục tạm (env OUTPUT_DIR_ENV) để command ghi file kết quả; thư mục luôn bị xoá
    khi hàm kết thúc, file (nếu chạy thành công) được đọc vào RunResult.output_file. Server không lưu gì.
    """
    if get_allowed_command(command.name) is None:
        raise PermissionDenied("Command %r is not allowed." % command.name)
    timeout = get_setting("TIMEOUT_SECONDS")
    limit = get_setting("MAX_OUTPUT_CHARS")
    display = shell_join([command.name, *built.display_argv])
    username = getattr(user, "email", user)
    logger.info("Admin command started by %s: %s", username, display)

    with tempfile.TemporaryDirectory(prefix="dza-command-") as output_dir:
        env = {
            **os.environ,
            "DJANGO_SETTINGS_MODULE": os.environ.get("DJANGO_SETTINGS_MODULE") or settings.SETTINGS_MODULE,
            "PYTHONIOENCODING": "utf-8",
            OUTPUT_DIR_ENV: output_dir,
        }
        started = time.monotonic()
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "django", command.name, *built.argv],
                cwd=settings.BASE_DIR,
                env=env,
                stdin=subprocess.DEVNULL,
                # Python 3.6: chưa có capture_output / text
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
            exit_code, stdout, stderr, timed_out = completed.returncode, completed.stdout, completed.stderr, False
        except subprocess.TimeoutExpired as error:
            exit_code, stdout, stderr, timed_out = None, error.stdout, error.stderr, True
        duration = time.monotonic() - started

        stdout, stdout_truncated = _tail(stdout, limit)
        stderr, stderr_truncated = _tail(stderr, limit)
        result = RunResult(exit_code, stdout, stderr, timed_out, duration, stdout_truncated, stderr_truncated)
        if result.succeeded:
            result.output_file = _read_output_file(output_dir, display)

    level = logging.INFO if result.succeeded else logging.WARNING
    logger.log(
        level, "Admin command finished by %s: %s (exit code: %s, timed out: %s, %.1fs, file: %s)",
        username, display, exit_code, timed_out, duration, result.output_file and result.output_file.name,
    )
    return result
