# dza_admin_tools — "Django commands" trong Django admin

Superuser chạy các management command được cho phép ngay trong admin:
**System tools › Django commands** (`/admin/dza-commands/`). Port từ `dza_rest_utils/admin_commands.py`
cho Python 3.9 + Django 2.2 (không htmx: trang form → chạy → trang kết quả hoặc tải file).

## Cài đặt

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "dza_admin_tools.apps.DzaAdminToolsConfig",  # ready() tự gắn URL + menu vào admin.site
]

DZA_ADMIN_COMMANDS = {
    "ALLOWED": ["export_patient_visits"],  # allowlist; command ngoài danh sách không hiện / không chạy được
    "TIMEOUT_SECONDS": 50,                 # phải nhỏ hơn nginx proxy_read_timeout (60s) và gunicorn --timeout (75s)
    "MAX_OUTPUT_CHARS": 100_000,           # cắt stdout/stderr hiển thị (giữ phần cuối)
}
```

Không cần sửa `urls.py`.

## Cách hoạt động

- Chỉ `is_superuser` thấy menu và mở được trang (user khác: 403; chưa đăng nhập: về trang login admin).
- Form sinh tự động từ `argparse` của command: option `--x` → input, `store_true` → checkbox, `choices` → select,
  `type=int/float` → number, `type=parse_date_arg` → `<input type="date">`, dest chứa password/secret/token → password.
- Command chạy trong process riêng: `python -m django <name> <argv>` (argv list, không shell, có timeout).
- Mỗi lần chạy view tạo một thư mục tạm và truyền qua env `DZA_COMMAND_OUTPUT_DIR`:
  - Chạy thành công và command ghi **đúng 1 file** vào đó → trình duyệt tải file ngay (không rời trang form).
  - Không có file / lỗi / timeout → trang kết quả (exit code, thời gian, stdout, stderr).
  - Thư mục tạm luôn bị xoá sau khi chạy: server không lưu file.
- Log: logger `dza_admin_tools.commands` ghi ai chạy, argv (đã che secret), exit code, thời gian, tên file.

## Thêm một command

1. Viết management command như bình thường. Nếu sinh file, ghi vào `get_output_dir()`:

   ```python
   from dza_admin_tools.command_utils import get_output_dir, parse_date_arg

   class Command(BaseCommand):
       def add_arguments(self, parser):
           parser.add_argument("--from-date", type=parse_date_arg, required=True)

       def handle(self, *args, from_date, **options):
           path = os.path.join(get_output_dir(), "report.xlsx")  # CLI: thư mục hiện tại
           ...
   ```

   Lỗi input → `raise CommandError(...)` (exit code ≠ 0, admin hiện stderr).
2. Thêm tên command vào `DZA_ADMIN_COMMANDS["ALLOWED"]`.

Command chạy lâu hơn `TIMEOUT_SECONDS` sẽ bị dừng → cân nhắc chạy nền (Celery) thay vì đưa vào đây.

## Command hiện có

| Command | Mô tả |
|---|---|
| `export_patient_visits --from-date YYYY-MM-DD --to-date YYYY-MM-DD` | Excel danh sách lượt khám toàn hệ thống theo ngày khám (`date_booked`, giờ VN), tối đa 366 ngày. Code: `doctors/exporters.py`, `doctors/management/commands/export_patient_visits.py`. |

## Test

```bash
docker exec phongkham-web-1 python manage.py test dza_admin_tools doctors --settings=Healthy_Care.settings_test
```

`settings_test` dựng test DB thẳng từ model (bỏ qua migration local, vì thư mục migrations đang bị `.gitignore`).
