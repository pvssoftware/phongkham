import io
import openpyxl
import xlsxwriter

from dataclasses import dataclass
from openpyxl.styles import PatternFill, Font
from pydantic import BaseModel, ValidationError
from typing import Callable, Any, Iterable, List, Dict, Optional, Type, Tuple


@dataclass
class ExcelColumn:
    field: str
    header: str
    width: int = 15
    number_format: Optional[str] = None
    formatter: Optional[Callable[[Any], Any]] = None


class BaseExcelExporter:
    filename: str = "export.xlsx"
    sheet_name: str = "Data"
    columns: List[ExcelColumn] = []
    chunk_size: int = 2000 

    def __init__(self, filename: Optional[str] = None, sheet_name: Optional[str] = None):
        self.filename = filename or self.__class__.filename
        self.sheet_name = sheet_name or self.__class__.sheet_name
        self.columns = list(self.__class__.columns)
        
        # Có thể gán lại chunk_size ở instance level nếu cần
        self.chunk_size = self.__class__.chunk_size

        if not self.columns:
            raise ValueError("Subclass need to define the list 'columns'")

    # [MỚI] Feedback 1: Abstract function cho việc lấy dữ liệu
    def get_data_iterator(self) -> Iterable[Dict[str, Any]]:
        """
        Subclass cần override hàm này và trả về một Generator/Iterator.
        Ví dụ: queryset.values().iterator(chunk_size=self.chunk_size)
        """
        raise NotImplementedError(
            "Subclass need to override 'get_data_iterator()' "
            "or pass data_iterator to func generate()."
        )

    def _extract_value(self, data_dict: dict, field_path: str):
        if isinstance(data_dict, dict) and field_path in data_dict:
            return data_dict.get(field_path)
        return ""

    def to_bytes_io(self, data_iterator: Optional[Iterable[Dict[str, Any]]] = None) -> io.BytesIO:
        # Nếu không truyền data_iterator từ ngoài vào, tự động gọi self.get_data_iterator()
        iterator = data_iterator if data_iterator is not None else self.get_data_iterator()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'constant_memory': True})
        worksheet = workbook.add_worksheet(self.sheet_name)

        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white',
            'align': 'center', 'valign': 'vcenter', 'border': 1
        })

        col_formats = []
        for col_idx, col in enumerate(self.columns):
            worksheet.set_column(col_idx, col_idx, col.width)
            worksheet.write(0, col_idx, col.header, header_format)
            fmt = workbook.add_format({'num_format': col.number_format}) if col.number_format else None
            col_formats.append(fmt)

        row_idx = 1
        for item_dict in iterator:
            for col_idx, col in enumerate(self.columns):
                val = self._extract_value(item_dict, col.field)
                if col.formatter and callable(col.formatter):
                    val = col.formatter(val)

                cell_fmt = col_formats[col_idx]
                if cell_fmt:
                    worksheet.write(row_idx, col_idx, val, cell_fmt)
                else:
                    worksheet.write(row_idx, col_idx, val)
            row_idx += 1

        workbook.close()
        output.seek(0)
        return output

    # ------------------------------------------------------------------
    # 2. OUTPUT STRATEGIES (Các cách trả về / phân phối dữ liệu)
    # ------------------------------------------------------------------
    def to_bytes(self, data_iterator: Optional[Iterable[Dict[str, Any]]] = None) -> bytes:
        """Trả về byte thuần (Dùng để upload S3, lưu file trên server...)"""
        return self.to_bytes_io(data_iterator).getvalue()

    def to_http_response(self, data_iterator: Optional[Iterable[Dict[str, Any]]] = None) -> Any:
        """Trả về HttpResponse để Client download trực tiếp
        
        E.g:
        excel_file = self.to_bytes_io(data_iterator)
        download_filename = filename or self.filename
        response = HttpResponse(
            excel_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        return response
        """
        raise NotImplementedError("Subclass need to override 'to_response()'.")


@dataclass
class ImportColumn:
    field: str              # Tên field tương ứng trong Pydantic Model / Database
    header: str             # Tên cột hiển thị trên file Excel Template
    width: int = 15
    required: bool = True   # Đánh dấu cột bắt buộc phải có trên file Excel
    parser: Optional[Callable[[Any], Any]] = None # Hàm custom xử lý data thô (VD: parse date)


class BaseExcelImporter:
    """
    Base class cho mọi logic Import Excel.
    """
    columns: List[ImportColumn] = []
    output_model: Type[BaseModel] = None  # Pydantic schema dùng để validate
    sheet_name: str = "Data"

    def __init__(self):
        if not self.columns:
            raise ValueError("Subclass need to define the 'columns'")
        if not self.output_model:
            raise ValueError("Subclass need to define the 'output_model' (Pydantic BaseModel)")

    # ------------------------------------------------------------------
    # 1. TEMPLATE GENERATOR (Tạo file mẫu cho Client B)
    # ------------------------------------------------------------------
    def generate_template_bytes(self) -> bytes:
        """Sinh ra file template Excel (.xlsx) dưới dạng bytes"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.sheet_name)

        # Format header như cách bạn làm ở Exporter
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white',
            'align': 'center', 'valign': 'vcenter', 'border': 1
        })

        for col_idx, col in enumerate(self.columns):
            worksheet.set_column(col_idx, col_idx, col.width)
            # Thêm dấu (*) nếu bắt buộc để user dễ nhìn
            header_text = f"{col.header} (*)" if col.required else col.header
            worksheet.write(0, col_idx, header_text, header_format)

        workbook.close()
        output.seek(0)
        return output.getvalue()

    # ------------------------------------------------------------------
    # 2. PARSE & VALIDATE DATA (Biến File B thành List C)
    # ------------------------------------------------------------------
    def parse_file(self, file_bytes: bytes) -> Tuple[List[BaseModel], List[Dict[str, Any]]]:
        """
        Đọc file, mapping header, validate từng dòng.
        Trả về: (Danh sách object hợp lệ, Danh sách lỗi)
        Lưu ý: Không nên throw exception ngay dòng đầu tiên lỗi,
               mà nên gom lỗi lại để báo cáo cho Client 1 lần.
        """
        wb = openpyxl.load_workbook(filename=io.BytesIO(file_bytes), read_only=True, data_only=True)
        sheet = wb[self.sheet_name] if self.sheet_name in wb.sheetnames else wb.active

        # Mapping header name -> column index
        # Việc này giúp file Excel không bị lỗi nếu User đổi thứ tự cột
        rows = sheet.iter_rows(values_only=True)
        try:
            header_row = next(rows)
        except StopIteration:
            raise ValueError("File Excel is empty, not found Header.")

        header_map = self._build_header_map(header_row)

        valid_rows: List[BaseModel] = []
        invalid_rows: List[Dict[str, Any]] = []

        for row_idx, row in enumerate(rows, start=2): # Row 1 là header, data bắt đầu từ row 2
            # Skip dòng trống hoàn toàn
            if all(cell is None or str(cell).strip() == "" for cell in row):
                continue

            row_data = {}
            for col in self.columns:
                col_idx = header_map.get(col.header)
                raw_value = row[col_idx] if col_idx is not None and col_idx < len(row) else None

                # Chạy custom parser nếu có
                if raw_value is not None and col.parser and callable(col.parser):
                    try:
                        raw_value = col.parser(raw_value)
                    except Exception as e:
                        invalid_rows.append({"row": row_idx, "error": f"Parse error on column '{col.header}': {str(e)}"})
                        continue

                row_data[col.field] = raw_value

            # Validate bằng Pydantic Model
            try:
                validated_obj = self.output_model(**row_data)
                valid_rows.append((row_idx, validated_obj))
            except ValidationError as e:
                # Format lại lỗi của pydantic cho dễ đọc
                err_msgs = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
                invalid_rows.append({
                    "row": row_idx,
                    "error": ", ".join(err_msgs),
                })

        wb.close()
        return valid_rows, invalid_rows

    def _build_header_map(self, header_row: Tuple[Any]) -> Dict[str, int]:
        """Tạo từ điển map giữa tên Cột (Header) và Index của nó trên file"""
        cleaned_headers = [str(h).replace(" (*)", "").strip() if h else "" for h in header_row]
        header_map = {header: idx for idx, header in enumerate(cleaned_headers)}

        # Kiểm tra xem các cột required có tồn tại không
        missing_cols = [
            col.header for col in self.columns
            if col.required and col.header not in header_map
        ]
        if missing_cols:
            raise ValueError(f"File Excel is missing some columns: {', '.join(missing_cols)}")

        return header_map

    # TÍNH NĂNG XUẤT FILE VALIDATION RESULT
    def generate_validation_report(self, file_bytes: bytes, invalid_rows: List[Dict[str, Any]]) -> bytes:
        """
        Nhận vào file excel gốc và danh sách lỗi.
        Trả về file excel mới có thêm cột 'Validation Result' ở cuối.
        """
        # Chuyển list lỗi thành dict mapping O(1) để tra cứu nhanh: {row_index: error_string}
        error_map = {item["row"]: item["error"] for item in invalid_rows}

        # Bắt buộc phải load file ở chế độ bình thường (không read_only) để có thể chỉnh sửa
        wb = openpyxl.load_workbook(filename=io.BytesIO(file_bytes))
        sheet = wb[self.sheet_name] if self.sheet_name in wb.sheetnames else wb.active

        # Xác định cột cuối cùng để chèn kết quả
        max_col = sheet.max_column
        result_col_idx = max_col + 1

        # Format cho header của cột kết quả (tùy chọn)
        header_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")

        # Thêm Header "Validation Result"
        header_cell = sheet.cell(row=1, column=result_col_idx, value="Validation Result")
        header_cell.fill = header_fill
        header_cell.font = Font(bold=True)
        sheet.column_dimensions[openpyxl.utils.get_column_letter(result_col_idx)].width = 40

        # Ghi kết quả cho từng dòng
        # Duyệt từ dòng 2 đến dòng cuối cùng có dữ liệu
        for row_idx in range(2, sheet.max_row + 1):
            # Kiểm tra xem dòng này có phải dòng trống hoàn toàn không (giống logic parse_file)
            is_empty_row = all(
                sheet.cell(row=row_idx, column=c).value is None or
                str(sheet.cell(row=row_idx, column=c).value).strip() == ""
                for c in range(1, max_col + 1)
            )

            if is_empty_row:
                continue

            result_cell = sheet.cell(row=row_idx, column=result_col_idx)

            if row_idx in error_map:
                result_cell.value = error_map[row_idx]
                result_cell.font = Font(color="FF0000")  # Chữ đỏ cho lỗi
            else:
                result_cell.value = "OK"
                result_cell.font = Font(color="00B050")  # Chữ xanh cho OK

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    # ------------------------------------------------------------------
    # 3. PERSISTENCE (Abstract - Dành cho Subclass)
    # ------------------------------------------------------------------
    def persist_data(self, valid_rows: List[Tuple[int, BaseModel]]) -> List[Dict[str, Any]]:
        """
        Subclass need to override this func to persist rows data to db.
        """
        raise NotImplementedError("Subclass need to override 'persist_data'.")