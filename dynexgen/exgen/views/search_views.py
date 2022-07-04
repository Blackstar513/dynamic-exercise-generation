from django.shortcuts import render
from django.db.models import Q
from ..forms.search_forms import ExerciseSearchForm
from ..models import Exercise


def search_for_exercises(request):
    search_results = None
    if request.GET.get('text') or request.GET.get('categories') or request.GET.get('lecturers'):
        text = request.GET.get('text')
        text = text if text is not None else ""

        categories = request.GET.getlist('categories')
        lecturers = request.GET.getlist('lecturers')

        category_include_all = request.GET.get('category_connect') == 'all'

        query_list = [Q(text__icontains=text), Q(published=True)]
        if lecturers:
            query_list.append(Q(creator__pk__in=lecturers))

        if categories:
            if category_include_all:
                search_results = Exercise.objects.all()
                for category in categories:
                    search_results = search_results.filter(*query_list,
                                                           Q(category__pk__exact=category))
            else:
                search_results = Exercise.objects.filter(*query_list,
                                                         Q(category__pk__in=categories))
        else:
            search_results = Exercise.objects.filter(*query_list)

        form = ExerciseSearchForm(request.GET)
    else:
        form = ExerciseSearchForm()

    return render(request, 'exgen/search_for_exercise.html',
                  {'search_results': search_results,
                   'form': form})
