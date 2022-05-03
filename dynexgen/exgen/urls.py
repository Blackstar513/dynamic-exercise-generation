from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/exercise', views.ExerciseBottomUpView.as_view(), name='bottom_up')
]
