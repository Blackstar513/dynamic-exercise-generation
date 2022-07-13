from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple


class SelectFileTypeForm(forms.Form):

    doctype = forms.ChoiceField(label="filetypes", choices=(('pdf', "PDF"),
                                                            ('pdf_present', "PDF as Presentation"),
                                                            ('docx', "DOCX"),
                                                            ('latex', "Latex"),
                                                            ('beamer', "Beamer"),
                                                            ('html', "HTML"),
                                                            ('markdown', "MarkDown")),
                                #widget=forms.RadioSelect(),
                                initial='pdf',
                                required=True)

    full_exercise = forms.BooleanField(label="use full exercises?", required=False)
    include_answers = forms.BooleanField(label="include answers?", required=False)
    exercise = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput())
    assembly = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput())


class SelectExercisesForm(forms.Form):
    def __init__(self, exercise_choices: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        for exercise in exercise_choices:
            categories = [str(c) for c in exercise.category.all()]
            creator_name = f"{exercise.creator.last_name}, {exercise.creator.first_name}" if exercise.creator.last_name else str(exercise.creator)
            choices.append((exercise.id, f"{exercise} | {creator_name} | {','.join(categories)}"))
        self.fields['exercise'] = forms.MultipleChoiceField(label="Exercises", choices=tuple(choices),
                                                            widget=FilteredSelectMultiple("Exercises", is_stacked=False),
                                                            required=True)


class SingleAssemblyForm(forms.Form):
    assembly = forms.CharField(widget=forms.HiddenInput())


