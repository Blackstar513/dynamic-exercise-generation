from django.http import HttpResponse, HttpResponseNotFound
from tempfile import TemporaryDirectory
from ..models import Exercise, ExerciseDependency
from ..utils.pandoc_base import exercise_as_file



def converted_file_response_view(request, exercise_id, doctype):
    print(f"convert_file_response_view({exercise_id=}, {doctype=})")
    exercise = Exercise.objects.get(pk=exercise_id).get_all_parent_dependencies_correctly_nested()
    with TemporaryDirectory() as tempdir:
        response_file = exercise_as_file(exercise, tempdir, doctype)
        response = HttpResponse(content=response_file)
        response['Content-Type'] = 'application/pdf'
        return response
    return HttpResponseNotFound('Not Implemented')


