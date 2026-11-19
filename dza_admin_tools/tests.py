import os
import subprocess
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from dza_admin_tools import services
from dza_admin_tools.command_utils import OUTPUT_DIR_ENV
from dza_admin_tools.services import FieldKind, build_argv, get_allowed_command
from user.models import User

COMMAND = "export_patient_visits"
ALLOWED = {"ALLOWED": [COMMAND], "TIMEOUT_SECONDS": 5}
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def make_user(email, **flags):
    return User.objects.create_user(email=email, password="pw-123456", **flags)


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


@override_settings(DZA_ADMIN_COMMANDS=ALLOWED)
class ServicesTests(TestCase):
    def test_describes_date_fields_from_argparse(self):
        command = get_allowed_command(COMMAND)

        self.assertTrue(command.runnable)
        self.assertEqual(
            [(spec.dest, spec.kind, spec.option, spec.required) for spec in command.fields],
            [
                ("from_date", FieldKind.DATE, "--from-date", True),
                ("to_date", FieldKind.DATE, "--to-date", True),
                ("unique_patients", FieldKind.CHECKBOX, "--unique-patients", False),
            ],
        )

    def test_build_argv_valid_and_invalid(self):
        command = get_allowed_command(COMMAND)

        built = build_argv(command, {"from_date": "2026-11-01", "to_date": "2026-11-19"})
        self.assertEqual(built.errors, {})
        self.assertEqual(built.argv, ["--from-date=2026-11-01", "--to-date=2026-11-19"])

        built = build_argv(command, {"from_date": "2026-11-01", "to_date": "2026-11-19", "unique_patients": "on"})
        self.assertEqual(built.argv, ["--from-date=2026-11-01", "--to-date=2026-11-19", "--unique-patients"])

        built = build_argv(command, {"from_date": "19/11/2026", "to_date": ""})
        self.assertEqual(set(built.errors), {"from_date", "to_date"})

    def test_not_allowed_command_is_hidden(self):
        self.assertIsNone(get_allowed_command("flush"))
        self.assertEqual([c.name for c in services.get_allowed_commands()], [COMMAND])

    @mock.patch("dza_admin_tools.services.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=5))
    def test_run_command_timeout(self, _run):
        command = get_allowed_command(COMMAND)
        result = services.run_command(command, build_argv(command, {"from_date": "2026-11-01", "to_date": "2026-11-01"}), user="admin")

        self.assertTrue(result.timed_out)
        self.assertFalse(result.succeeded)


@override_settings(DZA_ADMIN_COMMANDS=ALLOWED)
class AdminViewsTests(TestCase):
    def setUp(self):
        self.list_url = reverse("admin:dza_commands")
        self.run_url = reverse("admin:dza_commands_run", args=[COMMAND])

    def login_superuser(self):
        user = make_user("root@example.com", is_staff=True, is_superuser=True)
        self.client.force_login(user)
        return user

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response["Location"])

    def test_staff_without_superuser_forbidden_and_no_menu(self):
        self.client.force_login(make_user("staff@example.com", is_staff=True))

        self.assertEqual(self.client.get(self.list_url).status_code, 403)
        self.assertEqual(self.client.get(self.run_url).status_code, 403)
        self.assertNotContains(self.client.get(reverse("admin:index")), self.list_url)

    def test_superuser_sees_menu_list_and_form(self):
        self.login_superuser()

        self.assertContains(self.client.get(reverse("admin:index")), self.list_url)
        self.assertContains(self.client.get(self.list_url), COMMAND)
        form = self.client.get(self.run_url)
        self.assertContains(form, 'type="date"', count=2)

    def test_unknown_or_not_allowed_command_404(self):
        self.login_superuser()
        self.assertEqual(self.client.get(reverse("admin:dza_commands_run", args=["flush"])).status_code, 404)

    def test_invalid_post_rerenders_form_with_errors(self):
        self.login_superuser()
        with mock.patch("dza_admin_tools.services.subprocess.run") as run:
            response = self.client.post(self.run_url, {"from_date": "", "to_date": "2026-11-19"})

        self.assertEqual(response.status_code, 422)
        self.assertContains(response, "errorlist", status_code=422)
        run.assert_not_called()

    def test_failed_run_shows_result_page(self):
        self.login_superuser()
        with mock.patch("dza_admin_tools.services.subprocess.run", return_value=completed(1, stderr="CommandError: boom")) as run:
            response = self.client.post(self.run_url, {"from_date": "2026-11-20", "to_date": "2026-11-19"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CommandError: boom")
        self.assertContains(response, "exit code 1")
        argv = run.call_args[0][0]
        self.assertEqual(argv[-3:], [COMMAND, "--from-date=2026-11-20", "--to-date=2026-11-19"])


def fake_run_writing(filename, content=b"xlsx-bytes", returncode=0, seen_dirs=None):
    """subprocess.run giả: ghi file vào thư mục env DZA_COMMAND_OUTPUT_DIR như command thật."""
    def run(argv, **kwargs):
        output_dir = kwargs["env"][OUTPUT_DIR_ENV]
        if seen_dirs is not None:
            seen_dirs.append(output_dir)
        if filename:
            with open(os.path.join(output_dir, filename), "wb") as file:
                file.write(content)
        return completed(returncode, stdout="Exported 3 visits")
    return run


@override_settings(DZA_ADMIN_COMMANDS=ALLOWED)
class OutputFileTests(TestCase):
    run_data = {"from_date": "2026-11-01", "to_date": "2026-11-19"}

    def setUp(self):
        self.client.force_login(make_user("root@example.com", is_staff=True, is_superuser=True))
        self.run_url = reverse("admin:dza_commands_run", args=[COMMAND])

    def post(self, fake_run, **extra):
        with mock.patch("dza_admin_tools.services.subprocess.run", side_effect=fake_run):
            return self.client.post(self.run_url, {**self.run_data, **extra})

    def test_success_with_file_downloads_immediately_and_cleans_up(self):
        seen_dirs = []
        response = self.post(
            fake_run_writing("luot_kham_2026-11-01_2026-11-19.xlsx", seen_dirs=seen_dirs),
            _dza_download_token="abc123",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], XLSX_CONTENT_TYPE)
        self.assertIn('attachment; filename="luot_kham_2026-11-01_2026-11-19.xlsx"', response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), b"xlsx-bytes")
        self.assertEqual(response.cookies["dza_download_token"].value, "abc123")
        self.assertEqual(len(seen_dirs), 1)
        self.assertFalse(os.path.exists(seen_dirs[0]))

    def test_invalid_download_token_is_not_echoed(self):
        response = self.post(fake_run_writing("a.xlsx"), _dza_download_token="<script>")
        self.assertNotIn("dza_download_token", response.cookies)

    def test_success_without_file_shows_result_page(self):
        response = self.post(fake_run_writing(None))

        self.assertContains(response, "Exported 3 visits")
        self.assertNotIn("Content-Disposition", response)

    def test_failure_never_returns_file_and_cleans_up(self):
        seen_dirs = []
        response = self.post(fake_run_writing("partial.xlsx", returncode=1, seen_dirs=seen_dirs))

        self.assertNotIn("Content-Disposition", response)
        self.assertContains(response, "exit code 1")
        self.assertFalse(os.path.exists(seen_dirs[0]))

    def test_timeout_cleans_up(self):
        seen_dirs = []

        def fake_run(argv, **kwargs):
            seen_dirs.append(kwargs["env"][OUTPUT_DIR_ENV])
            open(os.path.join(seen_dirs[0], "x.xlsx"), "wb").close()
            raise subprocess.TimeoutExpired(cmd="x", timeout=5)

        response = self.post(fake_run)

        self.assertContains(response, "Timed out")
        self.assertFalse(os.path.exists(seen_dirs[0]))
