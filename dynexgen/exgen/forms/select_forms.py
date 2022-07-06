from django import forms
from ..models import Category, Exercise

class SelectFileTypeForm(forms.Form):

    filetype=forms.ChoiceField(label="filetypes", choices=(("pdf","PDF"),("html","HTML"),("docx","DOCX"),("latex","LATEX")),widget=forms.RadioSelect(),initial="pdf",required=True)
    full_exercise=forms.BooleanField(label="use full exercises?", required=False)
