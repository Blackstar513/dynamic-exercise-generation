from django.views import generic
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.http import HttpResponse
from ..models import Exercise, ExerciseDependency


def index(request):
    return HttpResponse("HELLO WORLD!")


class ExerciseBottomUpView(generic.ListView):
    template_name = 'exgen/exercise_list.html'
    context_object_name = 'context'

    def get_queryset(self):
        return {'exercise_dependencies': Exercise.objects.get(pk=self.kwargs['pk']).get_all_parent_dependencies_correctly_nested(),
                'show_answers': False,
                'exercise_id': self.kwargs['pk']}


class ExerciseAnswerBottomUpView(generic.ListView):
    template_name = 'exgen/exercise_list.html'
    context_object_name = 'context'

    def get_queryset(self):
        return {'exercise_dependencies': Exercise.objects.get(pk=self.kwargs['pk']).get_all_parent_dependencies_correctly_nested(),
                'show_answers': True,
                'exercise_id': self.kwargs['pk']}


class ExerciseTopDownView(generic.ListView):
    template_name = 'exgen/exercise_list.html'
    context_object_name = 'context'

    def get_queryset(self):
        return {'exercise_dependencies': Exercise.objects.get(pk=self.kwargs['pk']).get_root().get_all_child_dependencies(),
                'show_answers': False,
                'exercise_id': self.kwargs['pk']}
            

