from django.shortcuts import render
from django.db.models import Q
from ..forms.select_forms import SelectFileTypeForm
from ..models import Exercise


# Create your views here.
def type_views(request):
  
  # render function takes argument - request
  # and return HTML as response
    return render(request, "exgen/type_selector.html",
                  {"form": SelectFileTypeForm(initial={'exercises': request.POST.getlist('exercises'),
                                                       'assembly': request.POST.get('assembly')})})
