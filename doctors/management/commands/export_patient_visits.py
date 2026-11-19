import logging
import os

from django.core.management.base import BaseCommand, CommandError

from doctors.exporters import PatientVisitExcelExporter
from dza_admin_tools.command_utils import get_output_dir, parse_date_arg

logger = logging.getLogger(__name__)

MAX_RANGE_DAYS = 366


class Command(BaseCommand):
    help = (
        "Xuất Excel danh sách lượt khám (toàn hệ thống) có ngày khám (date_booked, giờ VN) trong khoảng "
        "[--from-date, --to-date]. Lượt khám chưa có ngày khám sẽ không được xuất. Tối đa %d ngày." % MAX_RANGE_DAYS
    )

    def add_arguments(self, parser):
        parser.add_argument("--from-date", dest="from_date", type=parse_date_arg, required=True,
                            help="Từ ngày (YYYY-MM-DD), tính cả ngày này.")
        parser.add_argument("--to-date", dest="to_date", type=parse_date_arg, required=True,
                            help="Đến ngày (YYYY-MM-DD), tính cả ngày này.")
        parser.add_argument("--unique-patients", dest="unique_patients", action="store_true",
                            help="Bỏ trùng theo hồ sơ bệnh nhân: mỗi bệnh nhân 1 dòng (lượt khám gần nhất trong "
                                 "khoảng, phí của lượt đó), thêm cột 'Số lần khám'.")

    def handle(self, *args, from_date, to_date, unique_patients=False, **options):
        if from_date > to_date:
            raise CommandError("--from-date must be on or before --to-date.")
        if (to_date - from_date).days + 1 > MAX_RANGE_DAYS:
            raise CommandError("Date range must not exceed %d days." % MAX_RANGE_DAYS)

        exporter = PatientVisitExcelExporter(from_date, to_date, unique_patients=unique_patients)
        content = exporter.to_bytes()  # sinh hết vào memory trước, lỗi giữa chừng không để lại file dở
        path = os.path.join(get_output_dir(), exporter.filename)
        with open(path, "wb") as file:
            file.write(content)

        unit = "patients" if unique_patients else "visits"
        logger.info("Exported %d %s (%s..%s) to %s", exporter.row_count, unit, from_date, to_date, path)
        self.stdout.write(self.style.SUCCESS("Exported %d %s to %s" % (exporter.row_count, unit, path)))
