"""
Tiện ích cho management command chạy được từ trang "Django commands" trong admin.

- parse_date_arg: argparse `type` cho ngày YYYY-MM-DD; form admin render thành <input type="date">.
- get_output_dir: thư mục command ghi file kết quả. Khi chạy từ admin, view tạo thư mục tạm và truyền qua
  env OUTPUT_DIR_ENV; file trong đó được trả thẳng cho trình duyệt rồi xoá. Chạy CLI: thư mục hiện tại.
"""
import argparse
import os
from datetime import datetime

OUTPUT_DIR_ENV = "DZA_COMMAND_OUTPUT_DIR"
DATE_FORMAT = "%Y-%m-%d"


def parse_date_arg(value):
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("Invalid date %r, expected YYYY-MM-DD." % value)


parse_date_arg.form_kind = "date"


def get_output_dir():
    return os.environ.get(OUTPUT_DIR_ENV) or os.getcwd()
