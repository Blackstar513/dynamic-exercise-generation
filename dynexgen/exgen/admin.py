import nested_admin
from django.utils.html import format_html
from django.contrib import admin
from .models import Exercise, Answer, Category, Course, ExercisePicture, AnswerPicture, ExerciseDependency, \
    CourseExercise, CourseCategory, ExerciseCategory, Assembly, ExerciseAssembly, AssemblyCategory


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


class ExerciseAssemblyInline(admin.TabularInline):
    model = ExerciseAssembly
    extra = 1


class AssemblyCategoryInline(admin.TabularInline):
    model = AssemblyCategory
    extra = 1


# Custom admin forms
class ExerciseAdmin(nested_admin.NestedModelAdmin):
    list_display = ('__str__', 'creator', 'text_type', 'short_comment', 'date_modified', 'published')
    #list_display_links = list_display
    list_filter = ('creator', 'published', 'text_type', ('date_modified', admin.DateFieldListFilter))

    search_fields = ('title', 'text', 'creator__last_name__startswith', 'text_type__startswith')
    search_help_text = "Searches anywhere in titles and text;\nSearches if creator or texttype start with the query"

    actions = (make_published, make_unpublished, make_clone)

    save_as = True  # overwrites "save and add another" with "save as new" -> allows cloning of exercises

    fieldsets = [
        (None,               {'fields': ['title', 'text', 'text_type']}),
        ("Comment",               {'fields': ['comment'],
                              'classes': ['collapse']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseInline, AnswerInline, ExercisePictureInline, ExerciseCategoryInline, CourseInline]

    @admin.display(description="comment")
    def short_comment(self, obj):
        s_comment = obj.comment
        if len(s_comment) > 150:
            s_comment = f"{s_comment[:150]}..."
        return format_html("<span title='{}'>{}</span>", obj.comment, s_comment)

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


class AssemblyAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'date_modified', 'published')

    actions = (make_published, make_unpublished, make_clone)
    save_as = True  # overwrites "save and add another" with "save as new" -> allows cloning of exercises

    fieldsets = [
        (None, {'fields': ['title']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseAssemblyInline, AssemblyCategoryInline]

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Course, inlines=[CourseCategoryInline])
admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Category)
