from django.shortcuts import render
from django.db.models import Q
from ..forms.search_forms import ExerciseSearchForm
from ..models import Exercise


def search_for_exercises(request):
    search_results = None
    if request.GET.get('text') or request.GET.get('categories'):
        text = request.GET.get('text')
        text = text if text is not None else ""

        categories = request.GET.getlist('categories')

        if categories:
            search_queries = []
            for categorie in categories:
                search_queries.append(Exercise.objects.filter(Q(text__icontains=text),
                                                              Q(category__pk__exact=categorie)))

            if len(search_queries) > 1:
                search_results = search_queries[0].intersection(*search_queries[1:])
            else:
                search_results = search_queries[0]
        else:
            search_results = Exercise.objects.filter(text__icontains=text).distinct()

        form = ExerciseSearchForm(request.GET)
    else:
        form = ExerciseSearchForm()

    return render(request, 'exgen/search_for_exercise.html',
                  {'search_results': search_results,
                   'form': form})
