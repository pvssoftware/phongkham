import requests

from django.conf import settings

from dj7n_utils import base_service
from dj7n_utils.common_decorators import handle_exceptions
from doctors.models import MedicalHistory

@handle_exceptions
def get_invoice(history_id):
    try:
        history = MedicalHistory.objects.get(pk=history_id)
    except MedicalHistory.DoesNotExist:
        return base_service.make_error(
            [], "Bản ghi doanh thu không tồn tại", code=404
        )

    if not history.get_invoice_uuid():
        return base_service.make_error(
            [], "Không thấy hóa đơn liên kết với bản ghi doanh thu này", code=404
        )

    company_id = settings.GW_COMPANY_ID

    invoice_id = history.get_invoice_id()
    target_url = settings.INVOICE_SERVICE_HOST + '/e-invoices/get/' + str(invoice_id)

    headers = {'Content-Type': 'application/json'}
    if company_id:
        headers['X-Company-Id'] = str(company_id)

    try:
        resp = requests.get(target_url, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return base_service.make_error(
            [], f"Lỗi khi gọi dịch vụ hóa đơn: {str(exc)}", code=502
        )

    status_code = resp.status_code
    try:
        resp_data = resp.json()
    except ValueError:
        resp_data = resp.text

    # update invoice_uuid to history record if successful
    if status_code == 200:
        data = resp_data["data"]
        signed_pdf_url = data['signed_pdf']
        if history.get_invoice_signed_pdf_url() != signed_pdf_url:
            print(f"Updating signed PDF URL for history {history_id}")
            history.update_metadata_by_key('invoice_data', data)
    return base_service.make_success(resp_data, "OK", code=status_code)