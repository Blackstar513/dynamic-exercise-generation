from traceback import print_exception, format_exception

from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import BadRequest
from django.conf import settings as django_settings
from django.http import (
        HttpResponse,
        HttpResponseNotFound,
        HttpResponseBadRequest,
        HttpResponseServerError,
        )


#from ..models import Exercise, ExerciseDependency
from ..utils.file_generator import generate_file


def sanitize_configuration(configuration):
    if len(configuration) == 0:
        return HttpResponseBadRequest("needs parameters")
    if len(configuration.getlist("doctype",[])) != 1:
        return HttpResponseBadRequest("doctype has to be defined only once")
    return None


_content_types = {
        "pdf":"application/pdf",
        #"beamer":"application/pdf",
        "docx":'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        "odt":'application/vnd.oasis.opendocument.text',
        }


def converted_file_response_view(request):
    configuration = request.GET
    try:
        response_file = generate_file(configuration)
        response = HttpResponse(content=response_file)
        response['Content-Type'] = _content_types.get(configuration["doctype"],
                                                      'text/plain;charset=utf-8')
        return response

    except MultiValueDictKeyError as e:
        parameter=str(e)[1:-1]
        msg = f"Needs {parameter} as query parameter."
        msg += f"Please append an appropriate &{parameter}= to url"
        return HttpResponseBadRequest(msg)

    except BadRequest as e:
        return HttpResponseBadRequest(e)

    except Exception as e:
        print_exception(e)
        if django_settings.DEBUG:
            err = "<br>".join(format_exception(e)).replace("\n","<br>")
            return HttpResponseServerError("Raised error:<br>"+err)
        else:
            return HttpResponseServerError("Server error in generator")




    return HttpResponseNotFound('Not Implemented')


