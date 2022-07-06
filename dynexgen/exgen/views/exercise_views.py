from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from tempfile import TemporaryDirectory
from ..models import Exercise, ExerciseDependency
from ..utils.pandoc_base import exercise_as_file


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


def converted_file_response_view(request, exercise_id):
    configuration = request.GET
    if (response := sanitize_configuration(configuration)) is not None:
        return response

    exercise = Exercise.objects.get(pk=exercise_id).get_all_parent_dependencies_correctly_nested()
    with TemporaryDirectory() as tempdir:
        response_file = exercise_as_file(exercise, tempdir, configuration)
        response = HttpResponse(content=response_file)
        response['Content-Type'] = _content_types.get(configuration["doctype"],
                                                      'text/plain')
        return response
    return HttpResponseNotFound('Not Implemented')


