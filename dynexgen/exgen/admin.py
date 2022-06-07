from django.contrib import admin
from .models import Exercise, Answer, Category, Course, ExercisePicture, AnswerPicture, ExerciseDependency, \
    CourseExercise, CourseCategory, ExerciseCategory


# Custom admin actions
@admin.action(description='Mark selected exercises as published')
def make_published(modeladmin, request, queryset):
    queryset.update(published=True)


@admin.action(description='Mark selected exercises as unpublished')
def make_unpublished(modeladmin, request, queryset):
    queryset.update(published=False)


# Inline elements
class ExerciseInline(admin.TabularInline):
    model = ExerciseDependency
    extra = 0
    fk_name = 'parent'


class ExercisePictureInline(admin.TabularInline):
    model = ExercisePicture
    extra = 0


class ExerciseCategoryInline(admin.TabularInline):
    model = ExerciseCategory
    extra = 1


class AnswerPictureInline(admin.TabularInline):
    model = AnswerPicture
    extra = 0


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


class CourseInline(admin.TabularInline):
    model = CourseExercise
    extra = 0
    classes = ['collapse']


class CourseCategoryInline(admin.TabularInline):
    model = CourseCategory
    extra = 1


# Custom admin forms
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('text', 'creator', 'text_type', 'published')
    list_filter = ('creator', 'published', 'text_type')
    search_fields = ('text', 'creator__surname__startswith', 'text_type__startswith')
    actions = (make_published, make_unpublished)

    fieldsets = [
        (None,               {'fields': ['text', 'text_type']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseInline, AnswerInline, ExercisePictureInline, ExerciseCategoryInline, CourseInline]

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Course, inlines=[CourseCategoryInline])
admin.site.register(Answer, inlines=[AnswerPictureInline])
admin.site.register(Category)
