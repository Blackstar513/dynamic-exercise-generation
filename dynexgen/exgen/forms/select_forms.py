from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple


class SelectFileTypeForm(forms.Form):

    doctype = forms.ChoiceField(label="filetypes", choices=(('pdf', "PDF"),
                                                             ('html', "HTML"),
                                                             ('docx', "DOCX"),
                                                             ('latex', "LATEX")),
                                  widget=forms.RadioSelect(), initial='pdf',
                                  required=True)

    full_exercise = forms.BooleanField(label="use full exercises?", required=False)
    exercises = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput())
    assembly = forms.ChoiceField(widget=forms.HiddenInput())


class SelectExercisesForm(forms.Form):
    def __init__(self, exercise_choices: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for exercise in exercise_choices:
            categories = [str(c) for c in exercise.category.all()]
            choices.append((exercise.id, f"{exercise} | {exercise.creator} | {','.join(categories)}"))
        self.fields['exercises'] = forms.MultipleChoiceField(label="Exercises", choices=tuple(choices),
                                                             widget=FilteredSelectMultiple("Exercises", is_stacked=False),
                                                             required=True)


