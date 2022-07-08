from django.urls import path

from . import views

app_name = 'exgen'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:pk>/exercise', views.ExerciseBottomUpView.as_view(), name='bottom_up'),
    path('<int:pk>/exercise_root', views.ExerciseTopDownView.as_view(), name='top_down'),
    path('<int:pk>/exercise_answers', views.ExerciseAnswerBottomUpView.as_view(), name='answer_bottom_up'),
    path('generator', views.converted_file_response_view,name="generator"),
    path('exercise_search', views.search_for_exercises, name='exercise_search'),
    path('assembly_search', views.search_for_assemblies, name='assembly_search'),
    path('type_selector', views.type_views, name='type_views')
]
