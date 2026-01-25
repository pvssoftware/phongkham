import sys, traceback, logging

from django.utils.translation import gettext as _
from . import msg_codes

logger = logging.getLogger(__name__)

def make_success(result, message, message_code = '', dev_message = '', code = 200, page_info = {}):
    response = {
        'success' : True,
        'message' : message,
        'data' : result,
        'page_info': page_info,
        'status_code' : code,
        'message_code' : message_code,
        'dev_message' : dev_message
    }
    return response

def make_error(error_arr, error_msg='', message_code = '', dev_message = '', code = 400):
    if len(error_arr) > 0:
        code = 400
    elif message_code == msg_codes.SERVER_ERROR_CODE:
        code = 500
    
    # logger
    if code == 500:
        trace=traceback.extract_tb(sys.exc_info()[2])
        output = "\nTraceback is:\n"
        for (file,linenumber,affected,line)  in trace:
            output+="\t> Error at function %s\n" % (affected)
            output+="\t  At: %s:%s\n" % (file,linenumber)
            # output+="\t  Source: %s\n" % (line)
        logger.info(output)
    
    response = {
        'success' : False,
        'message' : error_msg,
        'status_code' : code,
        'message_code' : message_code,
        'dev_message' : dev_message,
        'data' : []
    }
    if error_arr:
        response['data'] = error_arr
    return response

def is_api_response_success(response):
    if response.status_code >= 200 and response.status_code < 300:
        return True 
    return False

def get_page_info_pagination(request_data, query_set):
    limit = 10
    page = 1
    if 'page_size' in request_data:
        limit = int(request_data['page_size'])
    if 'page' in request_data:
        page = int(request_data['page'])
    offset = (page - 1) * limit
    total = len(query_set)
    result = query_set[offset:offset+limit]
    hasNextPage = True
    hasPreviousPage = True
    result_count = len(result)

    if page <= 1:
        hasPreviousPage = False
    
    if result_count == total:
        hasNextPage = False
    elif (result_count <=1 ) or (result_count < limit and result_count < total):
        hasNextPage = False
    
    pageInfo = {
        'total': total,
        'current_limit': limit,
        'current_page': page,
        'has_next_page': hasNextPage,
        'has_previous_page': hasPreviousPage,
    }
    return result, pageInfo
