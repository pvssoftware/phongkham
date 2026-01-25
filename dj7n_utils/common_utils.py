import time, requests
from django.core.cache import cache
from django.conf import settings

class HeaderSpector:
    @classmethod
    def get_specific_header_in_request(cls, request, header_key: str):
        try:
            headers = dict(request.headers)
            header = ""
            if header_key in headers:
                header = headers.get(header_key)
            elif header_key.lower() in headers:
                header = headers.get(header_key.lower())
            return header
        except Exception as e:
            return ""

class LogTool:
    DISCORD_WEBHOOK_URL_TBPH = "https://discord.com/api/webhooks/1448699875876409549/86nfzpNKgcrd6Mhi1iMLDxQJxZb9ttYOEfLBDK3dxvNubmn2CDFahS60E_mMpVMgqWbW"
    # "https://discord.com/api/webhooks/1390355295808655370/hOxa4e0om7sz1_kKPCAOyjNrdrB7BHoIggQnpk5xvM04ltiYrLHlLcsEbFzW_EqgX7pu"
    PINVOICE_ORIGIN_PATTERN = "ei.pvssolution"

    @classmethod
    def send_discord_message(cls, content: str):
        data = {
            "content": content
        }
        requests.post(cls.DISCORD_WEBHOOK_URL_TBPH, json=data)

    @classmethod
    def print_log(cls, content: str):
        app_env = settings.APP_ENV
        cls.send_discord_message(
            content=f"({app_env}) {content}"
        )

    @classmethod
    def log_request_if_pinvoice_origin(cls, request, company_id: str, company_name: str = ""):
        header_value = HeaderSpector.get_specific_header_in_request(request, "Origin")
        cache_key = f"message_log_pinvoice_origin_request:{company_id}"
        cached = cache.get(cache_key)
        if not cached and cls.PINVOICE_ORIGIN_PATTERN in header_value:
            cls.print_log(f"Company ID {company_id}: {company_name} is using Pinvoice: {header_value}")
            cache.set(cache_key, header_value, 60*60*24)

def retry_task(task_func, input_data, max_retries, delay=1):
    attempt = 0
    while attempt < max_retries:
        try:
            print(f"🚀 Attempt {attempt + 1}...")
            return task_func(input_data)
        except Exception as e:
            attempt += 1
            print(f"⚠️ Task failed: {e}")
            if attempt < max_retries:
                time.sleep(delay)  # Optional: sleep 1s giữa các lần retry
            else:
                print("❌ All retries failed.")
                raise("{e}")  # Re-raise exception nếu hết retry