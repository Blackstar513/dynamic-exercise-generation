from django.contrib import admin
from .models import Exercise, Answer, Category, Course, Lecturer, ExercisePicture, AnswerPicture, ExerciseDependency, \
    CourseExercise, CourseCategory, ExerciseCategory


# Register your models here.
class ExerciseInline(admin.TabularInline):
    model = ExerciseDependency
    extra = 0
    fk_name = 'parent'


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


class ExercisePictureInline(admin.TabularInline):
    model = ExercisePicture
    extra = 0


class ExerciseCategoryInline(admin.TabularInline):
    model = ExerciseCategory
    extra = 1


class CourseInline(admin.TabularInline):
    model = CourseExercise
    extra = 0


class CourseCategoryInline(admin.TabularInline):
    model = CourseCategory
    extra = 1


class ExerciseAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['text', 'text_type']}),
        ('Lecturer', {'fields': ['creator']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseInline, AnswerInline, ExercisePictureInline, ExerciseCategoryInline, CourseInline]


class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseCategoryInline]


admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lecturer)
admin.site.register(Category)
