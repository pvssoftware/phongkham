import importlib
from typing import Any, Iterable, Dict, Optional


def export_any_excel(
    exporter_class_path: str,
    data_iterator: Optional[Iterable[Dict[str, Any]]] = None
):
    """
    Generic Task: Khởi tạo Exporter động, generate excel.
    Return excel file as bytes.
    """
    # 1. Dynamic import Exporter Class từ path
    module_name, class_name = exporter_class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    exporter_class = getattr(module, class_name)

    # 2. Khởi tạo instance & Re-apply Filter từ filter_params
    exporter = exporter_class()

    # 3. Generate file excel dạng bytes
    excel_bytes = exporter.to_bytes(data_iterator)

    return excel_bytes


def import_data_from_any_excel(
    importer_class_path: str,
    file_bytes: bytes,
    is_dry_run: bool = False
) -> Dict[str, Any]:
    """
    Generic Task: Khởi tạo Importer động, validate rows, persist data.
    Return validated excel file as bytes.
    """
    # 1. Dynamic import
    module_name, class_name = importer_class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    importer_class = getattr(module, class_name)

    # 2. Khởi tạo Importer
    importer = importer_class()

    # 3. Parse & Validate
    valid_rows, invalid_rows = importer.parse_file(file_bytes)
    valid_rows_count = len(valid_rows)
    invalid_rows_count = len(invalid_rows)
    total_rows_count = valid_rows_count + invalid_rows_count

    # 4. Lưu vào Database nếu có dữ liệu hợp lệ
    # Tùy nghiệp vụ: Bạn có thể chọn KHÔNG lưu nếu có bất kỳ lỗi nào (All or Nothing),
    # Hoặc lưu các dòng hợp lệ và trả về list các dòng lỗi.
    # Ở đây tôi thiết kế theo hướng lưu dòng đúng, báo cáo dòng sai.
    if not is_dry_run and valid_rows:
        # Gọi trực tiếp method persist_data do Subclass tự định nghĩa và thực thi
        db_errors = importer.persist_data(valid_rows)
        # Nếu có lỗi phát sinh từ tầng Database, gộp chung vào danh sách invalid_rows
        if db_errors:
            invalid_rows.extend(db_errors)
            invalid_rows_count = len(invalid_rows)
            valid_rows_count = total_rows_count - invalid_rows_count

    # 3. Luôn luôn sinh ra file report nếu có lỗi (hoặc sinh ra cả khi OK tùy nghiệp vụ)
    report_file_bytes = None
    if invalid_rows:
        report_file_bytes = importer.generate_validation_report(file_bytes, invalid_rows)
        # Tại đây Celery có thể upload report_file_bytes lên S3 và lưu link vào DB.

    return {
        "status": "success" if not invalid_rows else "partial_success",
        "valid_count": valid_rows_count,
        "invalid_count": invalid_rows_count,
        "report_file_bytes": report_file_bytes
    }


def generate_import_excel_template(
    importer_class_path: str,
) -> Dict[str, Any]:
    """
    Generic Task: Sinh file excel template để client
    điền dữ liệu vào excel đó
    """
    # 1. Dynamic import
    module_name, class_name = importer_class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    importer_class = getattr(module, class_name)

    # 2. Khởi tạo Importer
    importer = importer_class()

    # 3. Generate
    template_bytes = importer.generate_template_bytes()
    return template_bytes
