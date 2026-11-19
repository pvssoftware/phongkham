import io
import os
import tempfile
from datetime import date, datetime
from unittest import mock

import openpyxl
import pytz
from django.core.management import CommandError, call_command
from django.test import TestCase

from doctors.exporters import PatientVisitExcelExporter, parse_money
from doctors.factories import MedicalHistoryFactory, MedicalRecordFactory

VN = pytz.timezone("Asia/Ho_Chi_Minh")

EXPECTED_HEADERS = [
    "STT", "Ngày khám", "Số thứ tự", "Phòng khám", "Bác sĩ", "Mã BN", "Họ tên BN", "Ngày sinh",
    "Giới tính", "SĐT", "Địa chỉ", "Dịch vụ", "Triệu chứng", "Chẩn đoán", "Phí khám", "Phí siêu âm",
    "Phí xét nghiệm", "Trạng thái",
]


def vn_datetime(*args):
    return VN.localize(datetime(*args))


def read_rows(content):
    workbook = openpyxl.load_workbook(io.BytesIO(content))
    sheet = workbook.worksheets[0]
    return sheet.title, [list(row) for row in sheet.iter_rows(values_only=True)]


class ParseMoneyTests(TestCase):
    def test_parses_plain_and_formatted_numbers(self):
        self.assertEqual(parse_money("150000"), 150000)
        self.assertEqual(parse_money("150.000"), 150000)
        self.assertEqual(parse_money(" 1,200,000 đ"), 1200000)

    def test_garbage_becomes_zero(self):
        for value in (None, "", "abc", "   "):
            self.assertEqual(parse_money(value), 0)


class PatientVisitExcelExporterTests(TestCase):
    def test_exports_visits_in_range_with_all_columns(self):
        record = MedicalRecordFactory(
            full_name="Nguyễn Thị A", birth_date=date(1990, 5, 17), sex=True,
            phone="0901234567", address="12 Lê Lợi",
        )
        profile = record.doctor.doctor
        MedicalHistoryFactory(
            medical_record=record, date_booked=vn_datetime(2026, 11, 5, 9, 30), ordinal_number="3",
            service="khám phụ khoa", disease_symptom="đau bụng", diagnostis="viêm",
            medical_examination_cost="150.000",
            medical_ultrasonography_cost="100000", medical_ultrasonography_cost_2="50000",
            medical_ultrasonography_cost_3="",
            medical_test_cost="20000", medical_test_cost_2="abc", medical_test_cost_3="30000",
            is_waiting=False,
        )

        exporter = PatientVisitExcelExporter(date(2026, 11, 1), date(2026, 11, 30))
        title, rows = read_rows(exporter.to_bytes())

        self.assertEqual(title, "Lượt khám")
        self.assertEqual(rows[0], EXPECTED_HEADERS)
        self.assertEqual(rows[1], [
            1, "05/11/2026 09:30", "3", profile.clinic_name, profile.full_name, record.id, "Nguyễn Thị A",
            "17/05/1990", "Nữ", "0901234567", "12 Lê Lợi", "khám phụ khoa", "đau bụng", "viêm",
            150000, 150000, 50000, "Đã khám",
        ])
        self.assertEqual(exporter.row_count, 1)
        self.assertEqual(exporter.filename, "luot_kham_2026-11-01_2026-11-30.xlsx")

    def test_range_is_inclusive_in_local_timezone_and_sorted(self):
        inside_late = MedicalHistoryFactory(date_booked=vn_datetime(2026, 11, 2, 23, 50))
        inside_early = MedicalHistoryFactory(date_booked=vn_datetime(2026, 11, 1, 0, 10))  # UTC: 31/10
        MedicalHistoryFactory(date_booked=vn_datetime(2026, 10, 31, 23, 59))
        MedicalHistoryFactory(date_booked=vn_datetime(2026, 11, 3, 0, 0))
        MedicalHistoryFactory(date_booked=None)

        _, rows = read_rows(PatientVisitExcelExporter(date(2026, 11, 1), date(2026, 11, 2)).to_bytes())

        self.assertEqual([row[0] for row in rows[1:]], [1, 2])
        self.assertEqual(
            [row[5] for row in rows[1:]],
            [inside_early.medical_record_id, inside_late.medical_record_id],
        )

    def test_maps_male_and_waiting(self):
        record = MedicalRecordFactory(sex=False, birth_date=None)
        MedicalHistoryFactory(medical_record=record, date_booked=vn_datetime(2026, 11, 1, 8, 0), is_waiting=True)

        _, rows = read_rows(PatientVisitExcelExporter(date(2026, 11, 1), date(2026, 11, 1)).to_bytes())

        self.assertEqual(rows[1][8], "Nam")
        self.assertIsNone(rows[1][7])
        self.assertEqual(rows[1][17], "Đang chờ")


class UniquePatientsExporterTests(TestCase):
    def export(self, from_date, to_date):
        exporter = PatientVisitExcelExporter(from_date, to_date, unique_patients=True)
        title, rows = read_rows(exporter.to_bytes())
        return exporter, title, rows

    def test_one_row_per_patient_with_latest_visit_and_count(self):
        record_a = MedicalRecordFactory(full_name="Bệnh nhân A")
        MedicalHistoryFactory(medical_record=record_a, date_booked=vn_datetime(2026, 11, 2, 8, 0),
                              diagnostis="lần 1", medical_examination_cost="100000", is_waiting=False)
        MedicalHistoryFactory(medical_record=record_a, date_booked=vn_datetime(2026, 11, 9, 15, 0),
                              diagnostis="lần 2", medical_examination_cost="200000",
                              medical_ultrasonography_cost="50000", is_waiting=True)
        MedicalHistoryFactory(medical_record=record_a, date_booked=vn_datetime(2026, 12, 1, 8, 0),
                              diagnostis="ngoài khoảng")
        record_b = MedicalRecordFactory(full_name="Bệnh nhân B")
        MedicalHistoryFactory(medical_record=record_b, date_booked=vn_datetime(2026, 11, 5, 10, 0), diagnostis="B")

        exporter, title, rows = self.export(date(2026, 11, 1), date(2026, 11, 30))

        self.assertEqual(title, "Bệnh nhân")
        self.assertEqual(exporter.filename, "benh_nhan_2026-11-01_2026-11-30.xlsx")
        self.assertEqual(rows[0], EXPECTED_HEADERS + ["Số lần khám"])
        self.assertEqual(len(rows), 3)
        # sắp theo ngày khám của lượt đại diện: B (05/11) trước A (09/11)
        row_b, row_a = rows[1], rows[2]
        self.assertEqual((row_b[0], row_b[6], row_b[13], row_b[18]), (1, "Bệnh nhân B", "B", 1))
        self.assertEqual(
            (row_a[0], row_a[1], row_a[6], row_a[13], row_a[14], row_a[15], row_a[17], row_a[18]),
            (2, "09/11/2026 15:00", "Bệnh nhân A", "lần 2", 200000, 50000, "Đang chờ", 2),
        )
        self.assertEqual(exporter.row_count, 2)

    def test_same_datetime_tie_breaks_by_latest_id(self):
        record = MedicalRecordFactory()
        MedicalHistoryFactory(medical_record=record, date_booked=vn_datetime(2026, 11, 3, 9, 0), diagnostis="cũ")
        MedicalHistoryFactory(medical_record=record, date_booked=vn_datetime(2026, 11, 3, 9, 0), diagnostis="mới")

        _, _, rows = self.export(date(2026, 11, 3), date(2026, 11, 3))

        self.assertEqual([(row[13], row[18]) for row in rows[1:]], [("mới", 2)])

    def test_default_mode_unchanged(self):
        record = MedicalRecordFactory()
        MedicalHistoryFactory(medical_record=record, date_booked=vn_datetime(2026, 11, 3, 9, 0))
        MedicalHistoryFactory(medical_record=record, date_booked=vn_datetime(2026, 11, 4, 9, 0))

        exporter = PatientVisitExcelExporter(date(2026, 11, 1), date(2026, 11, 30))
        title, rows = read_rows(exporter.to_bytes())

        self.assertEqual((title, rows[0], len(rows)), ("Lượt khám", EXPECTED_HEADERS, 3))


class ExportPatientVisitsCommandTests(TestCase):
    def make_output_dir(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return tmp.name

    def run_command(self, *args):
        output_dir = self.make_output_dir()
        stdout = io.StringIO()
        with mock.patch.dict(os.environ, {"DZA_COMMAND_OUTPUT_DIR": output_dir}):
            call_command("export_patient_visits", *args, stdout=stdout)
        return output_dir, stdout.getvalue()

    def test_writes_file_into_output_dir(self):
        MedicalHistoryFactory(date_booked=vn_datetime(2026, 11, 10, 10, 0))

        output_dir, stdout = self.run_command("--from-date", "2026-11-01", "--to-date", "2026-11-19")

        self.assertEqual(os.listdir(output_dir), ["luot_kham_2026-11-01_2026-11-19.xlsx"])
        with open(os.path.join(output_dir, "luot_kham_2026-11-01_2026-11-19.xlsx"), "rb") as file:
            _, rows = read_rows(file.read())
        self.assertEqual(len(rows), 2)
        self.assertIn("1", stdout)

    def test_unique_patients_flag(self):
        record = MedicalRecordFactory()
        MedicalHistoryFactory(medical_record=record, date_booked=vn_datetime(2026, 11, 10, 10, 0))
        MedicalHistoryFactory(medical_record=record, date_booked=vn_datetime(2026, 11, 11, 10, 0))

        output_dir, _ = self.run_command("--from-date", "2026-11-01", "--to-date", "2026-11-19", "--unique-patients")

        self.assertEqual(os.listdir(output_dir), ["benh_nhan_2026-11-01_2026-11-19.xlsx"])
        with open(os.path.join(output_dir, "benh_nhan_2026-11-01_2026-11-19.xlsx"), "rb") as file:
            _, rows = read_rows(file.read())
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][18], 2)

    def test_invalid_input_raises_and_writes_nothing(self):
        cases = [
            ("--from-date", "2026-11-20", "--to-date", "2026-11-19"),  # from > to
            ("--from-date", "2025-01-01", "--to-date", "2026-01-02"),  # > 366 ngày
            ("--from-date", "19/11/2026", "--to-date", "2026-11-19"),  # sai định dạng
        ]
        for args in cases:
            with self.subTest(args=args):
                output_dir = self.make_output_dir()
                with mock.patch.dict(os.environ, {"DZA_COMMAND_OUTPUT_DIR": output_dir}):
                    with self.assertRaises(CommandError):
                        call_command("export_patient_visits", *args, stdout=io.StringIO())
                self.assertEqual(os.listdir(output_dir), [])
