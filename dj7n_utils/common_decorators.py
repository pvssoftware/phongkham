import functools
import traceback
from rest_framework.response import Response
from .common_utils import LogTool

DEFAULT_DICT_RETURN = {
    'success': False,
    'message': 'An error/exception occurred',
    'status_code': 500,
    'message_code': 'SERVER_ERROR_CODE',
    'dev_message': 'SERVER ERROR',
    'data': []
}

def handle_exceptions(default_return=DEFAULT_DICT_RETURN, catch=(Exception,), log_trace=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except catch as e:
                # Xác định tên class nếu có (args[0] thường là `self` hoặc `cls`)
                class_name = None
                if args:
                    instance = args[0]
                    if hasattr(instance, '__class__'):
                        class_name = instance.__class__.__name__

                func_name = func.__name__
                if class_name:
                    print(f"⚠️ Exception in {class_name}.{func_name}: {e}")
                    LogTool.print_log(f"⚠️ Exception in {class_name}.{func_name}: {e}")
                else:
                    print(f"⚠️ Exception in {func_name}: {e}")
                    LogTool.print_log(f"⚠️ Exception in {func_name}: {e}")

                if log_trace:
                    traceback.print_exc()
                res = default_return
                res["message"] = str(e)
                return Response(res, status=res.get("status_code", 500))
        return wrapper
    return decorator