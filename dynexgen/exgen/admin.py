from django.contrib import admin
from .models import Exercise, Answer, Category, Course, Lecturer, ExercisePicture, AnswerPicture, ExerciseDependency, \
    CourseExercise, CourseCategory, ExerciseCategory


# Register your models here.
admin.site.register(Exercise)
admin.site.register(Answer)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Lecturer)
admin.site.register(ExercisePicture)
admin.site.register(AnswerPicture)
admin.site.register(ExerciseDependency)
admin.site.register(CourseExercise)
admin.site.register(CourseCategory)
admin.site.register(ExerciseCategory)
