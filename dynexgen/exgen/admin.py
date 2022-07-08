import nested_admin
from django.utils.html import format_html
from django.contrib import admin, messages
from .models import Exercise, Answer, Category, Course, ExercisePicture, AnswerPicture, ExerciseDependency, \
    CourseExercise, CourseCategory, ExerciseCategory, Assembly, ExerciseAssembly, AssemblyCategory
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from datetime import datetime


admin.site.site_url = '/exgen/exercise_search'


# Custom admin actions
@admin.action(description='Clone selected objects')
def make_clone(modeladmin, request, queryset):
    for obj in queryset:
        obj.duplicate(request.user)


@admin.action(description='Mark selected objects as published')
def make_published(modeladmin, request, queryset):
    queryset.update(published=True)


@admin.action(description='Mark selected objects as unpublished')
def make_unpublished(modeladmin, request, queryset):
    queryset.update(published=False)


# admin Filters
class IsRootFilter(admin.EmptyFieldListFilter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = _('is root')

    def choices(self, changelist):
        for lookup, title in (
            (None, _("All")),
            ("1", _("Yes")),
            ("0", _("No")),
        ):
            yield {
                "selected": self.lookup_val == lookup,
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: lookup}
                ),
                "display": title,
            }


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "exercise":
            kwargs["queryset"] = Exercise.root.filter(published=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        exercise = formset.form.base_fields['exercise']
        exercise.widget.can_add_related = False
        exercise.widget.can_change_related = False
        exercise.widget.can_delete_related = False
        return formset


class AssemblyCategoryInline(admin.TabularInline):
    model = AssemblyCategory
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        category = formset.form.base_fields['category']
        category.widget.can_add_related = False
        category.widget.can_change_related = False
        category.widget.can_delete_related = False
        return formset


# Custom admin forms
class ExerciseAdmin(nested_admin.NestedModelAdmin):
    list_display = ('__str__', 'creator', 'category_list', 'text_type', 'short_comment', 'date_modified', 'published')
    #list_display_links = list_display
    list_filter = ('creator', 'published', 'text_type', ('date_modified', admin.DateFieldListFilter), ('children', IsRootFilter), 'category')

    search_fields = ('title', 'text', 'creator__last_name__startswith', 'text_type__startswith')
    search_help_text = "Searches anywhere in titles and text;\nSearches if creator or texttype start with the query"

    actions = ('delete_exercise_with_children', make_published, 'make_published_with_dependent', 'make_unpublished_with_dependent', make_clone, 'make_assembly')

    save_as = True  # overwrites "save and add another" with "save as new" -> allows cloning of exercises

    fieldsets = [
        (None,               {'fields': ['title', 'text', 'text_type']}),
        ("Comment",               {'fields': ['comment'],
                              'classes': ['collapse']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseInline, AnswerInline, ExercisePictureInline, ExerciseCategoryInline, CourseInline]

    @admin.display(description="comment", ordering='comment')
    def short_comment(self, obj):
        s_comment = obj.comment
        if len(s_comment) > 150:
            s_comment = f"{s_comment[:150]}..."
        return format_html("<span title='{}'>{}</span>", obj.comment, s_comment)

    @admin.display(description="categories")
    def category_list(self, obj):
        category_list = obj.category.all().order_by('-name')
        return ", ".join(c.name for c in category_list)

    @admin.action(description="Put selected actions into assembly")
    def make_assembly(self, request, queryset):
        assembly = Assembly.objects.create(title=f"Autogenerated at {datetime.now()}",
                                           creator=request.user)
        abort_creation = False
        for i, obj in enumerate(queryset):
            if not obj.published:
                abort_creation = True
                self.message_user(request, f"The exercise {obj} is not published!", level=messages.ERROR)
            if not obj.is_root():
                abort_creation = True
                self.message_user(request, f"The exercise {obj} is no root exercise!", level=messages.ERROR)
            assembly.exercise.add(obj, through_defaults={'rank': i + 1})

        if abort_creation:
            assembly.delete()
            return
        else:
            assembly.save()
            return HttpResponseRedirect(f'/admin/exgen/assembly/{assembly.id}/change/')

    @admin.action(description="Mark selected exercises and their children as published")
    def make_published_with_dependent(self, request, queryset):
        for q in queryset:
            self._publish_recursively(q.get_all_child_dependencies(), True)

    @admin.action(description="Mark selected exercises and their children as unpublished")
    def make_unpublished_with_dependent(self, request, queryset):
        for q in queryset:
            self._publish_recursively(q.get_all_child_dependencies(), False)

    @admin.action(description="Delete exercise together with all children")
    def delete_exercise_with_children(self, request, queryset):
        for q in queryset:
            self._delete_children_recursively(q.get_all_child_dependencies())

    def _publish_recursively(self, exercises, publish: bool):
        if isinstance(exercises, tuple) or isinstance(exercises, list):
            for e in exercises:
                self._publish_recursively(e, publish)
        else:
            exercises.published = publish
            exercises.save()

    def _delete_children_recursively(self, exercises):
        if isinstance(exercises, tuple) or isinstance(exercises, list):
            for e in exercises:
                self._delete_children_recursively(e)
        else:
            exercises.delete()

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


class AssemblyAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category_list', 'date_modified', 'published')
    list_filter = ('creator', 'published', ('date_modified', admin.DateFieldListFilter), 'category')

    actions = (make_published, make_unpublished, make_clone)
    save_as = True  # overwrites "save and add another" with "save as new" -> allows cloning of exercises

    fieldsets = [
        (None, {'fields': ['title']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseAssemblyInline, AssemblyCategoryInline]

    @admin.display(description="categories")
    def category_list(self, obj):
        category_list = obj.category.all().order_by('-name')
        return ", ".join(c.name for c in category_list)

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Course, inlines=[CourseCategoryInline])
admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Category)
