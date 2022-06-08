from django.http import HttpResponse, HttpResponseNotFound
from ..models import Exercise, ExerciseDependency



def converted_file_response_view(request,exercise_id,doctype):
    print(f"convert_file_response_view({exercise_id=}, {doctype=})")
    exercise = Exercise.objects.get(pk=exercise_id).get_all_parent_dependencies_correctly_nested()
    print(f"{exercise=}")
    #breakpoint()
    test_file = open('/home/cyriax/uni/bremm/pandoc_tests/autoconvert/out/pdf-out.pdf', 'rb')
    response = HttpResponse(content=test_file)
    response['Content-Type'] = 'application/pdf'
    #response['Content-Disposition'] = 'attachment; filename="%s.pdf"'
    return response
        



    # get exercise
    # convert file
    # build response
    return HttpResponseNotFound('Not Implemented')


