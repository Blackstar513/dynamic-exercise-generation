import nested_admin
from django.contrib import admin
from .models import Exercise, Answer, Category, Course, ExercisePicture, AnswerPicture, ExerciseDependency, \
    CourseExercise, CourseCategory, ExerciseCategory


# Custom admin actions
@admin.action(description='Clone selected objects')
def make_clone(modeladmin, request, queryset):
    for obj in queryset:
        obj.id = None
        obj.save()


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
    sortable_options = None  # needed, because of nested_admin errors


class ExercisePictureInline(admin.TabularInline):
    model = ExercisePicture
    extra = 0
    sortable_options = None  # needed, because of nested_admin errors


class ExerciseCategoryInline(admin.TabularInline):
    model = ExerciseCategory
    extra = 1
    sortable_options = None  # needed, because of nested_admin errors


class AnswerPictureInline(nested_admin.NestedTabularInline):
    model = AnswerPicture
    extra = 0


class AnswerInline(nested_admin.NestedTabularInline):
    model = Answer
    extra = 0
    inlines = [AnswerPictureInline]


class CourseInline(admin.TabularInline):
    model = CourseExercise
    extra = 0
    classes = ['collapse']
    sortable_options = False  # needed, because of nested_admin errors


class CourseCategoryInline(admin.TabularInline):
    model = CourseCategory
    extra = 1


# Custom admin forms
class ExerciseAdmin(nested_admin.NestedModelAdmin):
    list_display = ('__str__', 'creator', 'text_type', 'comment', 'date_modified', 'published')
    #list_display_links = list_display
    list_filter = ('creator', 'published', 'text_type')
    search_fields = ('title', 'text', 'creator__last_name__startswith', 'text_type__startswith')
    search_help_text = "Searches anywhere in titles and text;\nSearches if creator or texttype start with the query"
    actions = (make_published, make_unpublished, make_clone)
    save_as = True  # overwrites "save and add another" with "save as new" -> allows cloning of exercises

    fieldsets = [
        (None,               {'fields': ['title', 'text', 'text_type']}),
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
#admin.site.register(Answer, inlines=[AnswerPictureInline])
admin.site.register(Category)
