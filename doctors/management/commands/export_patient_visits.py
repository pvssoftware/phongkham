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

    def handle(self, *args, from_date, to_date, **options):
        if from_date > to_date:
            raise CommandError("--from-date must be on or before --to-date.")
        if (to_date - from_date).days + 1 > MAX_RANGE_DAYS:
            raise CommandError("Date range must not exceed %d days." % MAX_RANGE_DAYS)

        exporter = PatientVisitExcelExporter(from_date, to_date)
        content = exporter.to_bytes()  # sinh hết vào memory trước, lỗi giữa chừng không để lại file dở
        path = os.path.join(get_output_dir(), exporter.filename)
        with open(path, "wb") as file:
            file.write(content)

        logger.info("Exported %d patient visits (%s..%s) to %s", exporter.row_count, from_date, to_date, path)
        self.stdout.write(self.style.SUCCESS("Exported %d visits to %s" % (exporter.row_count, path)))
