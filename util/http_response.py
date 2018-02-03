import sys
import json
import traceback
from django.http import HttpResponse

debug_mode = False


def get_request_with_default(request, key, default_value):
    """
    Try to get value by specific key in request object, if can't find key in keySet, return default value.
    :param request: request object created by django
    :param key: key
    :param default_value: default value
    :return: 
    """
    try:
        return request.GET[key]
    except:
        return default_value


def get_request_get_with_default_none(request, key):
    """
    Try to get value by specific key in request object, if can't find key in keySet, return None.
    :param request: request object created by django
    :param key: key
    :return: 
    """
    return get_request_with_default(request, key, None)


def create_http_json_response(obj, indent=None) -> HttpResponse:
    """
    Create a http response 
    :param indent: if format json, use indent size
    :param obj: object which json serializable 
    :return: 
    """
    return HttpResponse(
        json.dumps(
            obj,
            indent=indent
        ),
        content_type="application/json"
    )


def get_host(request):
    """
    Get host info from request META
    :param request: 
    :return: 
    """
    return request.META["HTTP_HOST"].split(":")[0]


def response_json(func):
    """
    Trying to run function, if exception caught, return error details with json format, else return json formatted object
    :param func: 
    :return: 
    """

    def wrapper(request):
        try:
            return create_http_json_response(func(request))
        except Exception as ex:
            formatted_stack_trace = traceback.format_exc()
            print(formatted_stack_trace, file=sys.stderr)
            if debug_mode:
                return create_http_json_response({
                    "status": "error",
                    "error_info": str(ex),
                    "trace_back": formatted_stack_trace.split("\n")
                })
            else:
                return create_http_json_response({
                    "status": "error"
                })

    return wrapper
