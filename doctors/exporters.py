import re

from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.utils import timezone

from doctors.models import MedicalHistory
from dza_excel_utils.utils import BaseExcelExporter, ExcelColumn

MONEY_FORMAT = "#,##0"
ULTRASOUND_COST_FIELDS = ("medical_ultrasonography_cost", "medical_ultrasonography_cost_2", "medical_ultrasonography_cost_3")
TEST_COST_FIELDS = ("medical_test_cost", "medical_test_cost_2", "medical_test_cost_3")


def parse_money(value):
    """Các trường tiền là CharField ("150000", "150.000", "", rác...) -> int VND; không đọc được -> 0."""
    digits = re.sub(r"\D", "", str(value or ""))
    return int(digits) if digits else 0


def format_local_datetime(value):
    # BaseExcelExporter không bật remove_timezone: không được ghi datetime có tz
    return timezone.localtime(value).strftime("%d/%m/%Y %H:%M") if value else None


def format_date(value):
    return value.strftime("%d/%m/%Y") if value else None


def format_sex(value):
    return "Nữ" if value else "Nam"  # MedicalRecord.sex: True là nữ


def format_status(value):
    return "Đang chờ" if value else "Đã khám"


class PatientVisitExcelExporter(BaseExcelExporter):
    """Danh sách lượt khám (MedicalHistory) toàn hệ thống có date_booked (giờ local) trong [from_date, to_date]."""

    sheet_name = "Lượt khám"
    columns = [
        ExcelColumn(field="stt", header="STT", width=6),
        ExcelColumn(field="date_booked", header="Ngày khám", width=17, formatter=format_local_datetime),
        ExcelColumn(field="ordinal_number", header="Số thứ tự", width=10),
        ExcelColumn(field="medical_record__doctor__doctor__clinic_name", header="Phòng khám", width=28),
        ExcelColumn(field="medical_record__doctor__doctor__full_name", header="Bác sĩ", width=24),
        ExcelColumn(field="medical_record_id", header="Mã BN", width=9),
        ExcelColumn(field="medical_record__full_name", header="Họ tên BN", width=24),
        ExcelColumn(field="medical_record__birth_date", header="Ngày sinh", width=12, formatter=format_date),
        ExcelColumn(field="medical_record__sex", header="Giới tính", width=9, formatter=format_sex),
        ExcelColumn(field="medical_record__phone", header="SĐT", width=14),
        ExcelColumn(field="medical_record__address", header="Địa chỉ", width=30),
        ExcelColumn(field="service", header="Dịch vụ", width=18),
        ExcelColumn(field="disease_symptom", header="Triệu chứng", width=30),
        ExcelColumn(field="diagnostis", header="Chẩn đoán", width=30),
        ExcelColumn(field="medical_examination_cost", header="Phí khám", width=13,
                    number_format=MONEY_FORMAT, formatter=parse_money),
        ExcelColumn(field="ultrasound_cost", header="Phí siêu âm", width=13, number_format=MONEY_FORMAT),
        ExcelColumn(field="test_cost", header="Phí xét nghiệm", width=14, number_format=MONEY_FORMAT),
        ExcelColumn(field="is_waiting", header="Trạng thái", width=11, formatter=format_status),
    ]
    value_fields = (
        "date_booked", "ordinal_number", "medical_record_id",
        "medical_record__doctor__doctor__clinic_name", "medical_record__doctor__doctor__full_name",
        "medical_record__full_name", "medical_record__birth_date", "medical_record__sex",
        "medical_record__phone", "medical_record__address",
        "service", "disease_symptom", "diagnostis", "medical_examination_cost", "is_waiting",
    ) + ULTRASOUND_COST_FIELDS + TEST_COST_FIELDS

    def __init__(self, from_date, to_date, unique_patients=False):
        """unique_patients: mỗi hồ sơ bệnh nhân 1 dòng = lượt khám gần nhất trong khoảng, thêm cột "Số lần khám"."""
        prefix, sheet_name = ("benh_nhan", "Bệnh nhân") if unique_patients else ("luot_kham", None)
        super().__init__(
            filename="%s_%s_%s.xlsx" % (prefix, from_date.isoformat(), to_date.isoformat()),
            sheet_name=sheet_name,
        )
        self.from_date = from_date
        self.to_date = to_date
        self.unique_patients = unique_patients
        self.row_count = 0
        if unique_patients:
            self.columns.append(ExcelColumn(field="visit_count", header="Số lần khám", width=12))

    def get_queryset(self):
        in_range = MedicalHistory.objects.filter(date_booked__date__range=(self.from_date, self.to_date))
        value_fields = self.value_fields
        queryset = in_range
        if self.unique_patients:
            same_patient = in_range.filter(medical_record=OuterRef("medical_record"))
            latest_id = same_patient.order_by("-date_booked", "-id").values("id")[:1]
            # order_by() rỗng: không để Meta.ordering (-date_booked) lọt vào GROUP BY làm đếm sai
            visit_count = same_patient.order_by().values("medical_record").annotate(n=Count("id")).values("n")
            queryset = in_range.filter(id=Subquery(latest_id)).annotate(
                visit_count=Subquery(visit_count, output_field=IntegerField()),
            )
            value_fields += ("visit_count",)
        return queryset.order_by("date_booked", "id").values(*value_fields)

    def get_data_iterator(self):
        self.row_count = 0
        for row in self.get_queryset().iterator(chunk_size=self.chunk_size):
            self.row_count += 1
            row["stt"] = self.row_count
            row["ultrasound_cost"] = sum(parse_money(row[field]) for field in ULTRASOUND_COST_FIELDS)
            row["test_cost"] = sum(parse_money(row[field]) for field in TEST_COST_FIELDS)
            yield row
