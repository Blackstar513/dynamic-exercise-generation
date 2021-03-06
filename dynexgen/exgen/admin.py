import nested_admin
from django.utils.html import format_html
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from .models import Exercise, Answer, Category, Course, ExercisePicture, AnswerPicture, ExerciseDependency, \
    CourseExercise, CourseCategory, ExerciseCategory, Assembly, ExerciseAssembly, AssemblyCategory, AssemblyCourses
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from datetime import datetime

User = get_user_model()
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


# Custom admin displays
@admin.display(description="creator", ordering='creator__last_name')
def creator_name(obj):
    if obj.creator.last_name == '':
        return f"Username: {obj.creator}"
    else:
        return f"{obj.creator.last_name}, {obj.creator.first_name}"


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


class CreatorFullNameFilter(admin.SimpleListFilter):
    title = _("By Creator")
    parameter_name = "creator_id"

    def lookups(self, request, model_admin):
        users = []
        for u in User.objects.all():
            if u.last_name:
                users.append((u.pk, f'{u.last_name}, {u.first_name}'))
            else:
                users.append((u.pk, f"Username: {u}"))

        return users

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            return queryset.filter(creator_id=value)
        return queryset


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


class ExerciseCourseInline(admin.TabularInline):
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


class AssemblyCourseInline(admin.TabularInline):
    model = AssemblyCourses
    extra = 0
    classes = ['collapse']


# Custom admin forms
class ExerciseAdmin(nested_admin.NestedModelAdmin):
    list_display = ('exercise_title', creator_name, 'category_list', 'text_type', 'short_comment', 'date_modified', 'published')
    #list_display_links = list_display
    list_filter = (CreatorFullNameFilter, 'published', 'text_type', ('date_modified', admin.DateFieldListFilter), ('children', IsRootFilter), 'category')

    search_fields = ('title', 'text', 'creator__last_name__startswith', 'text_type__startswith')
    search_help_text = "Searches anywhere in titles and text;\nSearches if creator or texttype start with the query"

    actions = ('delete_exercise_with_children', make_published, 'make_published_with_dependent', 'make_unpublished_with_dependent', make_clone, 'make_assembly')

    fieldsets = [
        (None,               {'fields': ['title', 'text', 'text_type']}),
        ("Comment",               {'fields': ['comment'],
                              'classes': ['collapse']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseInline, AnswerInline, ExercisePictureInline, ExerciseCategoryInline, ExerciseCourseInline]

    save_as = True

    @admin.display(description="exercise", ordering='title')
    def exercise_title(self, obj):
        return str(obj)

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

    @admin.action(description="Put selected exercises into assembly")
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

    def change_view(self, request, object_id, form_url="", extra_context=None):
        change_page = super().change_view(request, object_id, form_url, extra_context)
        # a bit hacky deepcopy on save as new solution
        # first the flat copy is made (happens in the step above)
        # then this flat copy is deepcopied
        # then the flat copy gets deleted and the redirect updated
        if '_saveasnew' in request.POST:
            splitted_url = change_page.url.split('/')
            # get the flat copy
            new_obj = Exercise.objects.get(pk=splitted_url[4])
            # duplicate the flat copy to ensure deepcopy
            dup_obj = new_obj.duplicate(request.user)
            # delete the flat copy
            new_obj.delete()
            # update the redirect url
            splitted_url[4] = str(dup_obj.id)
            change_page = HttpResponseRedirect('/'.join(splitted_url))

        return change_page


class AssemblyAdmin(admin.ModelAdmin):
    list_display = ('title', creator_name, 'category_list', 'date_modified', 'published')
    list_filter = (CreatorFullNameFilter, 'published', ('date_modified', admin.DateFieldListFilter), 'category')

    actions = (make_published, make_unpublished, make_clone)
    save_as = True  # overwrites "save and add another" with "save as new" -> allows cloning of exercises

    fieldsets = [
        (None, {'fields': ['title']}),
        ('Published?', {'fields': ['published']}),
    ]
    inlines = [ExerciseAssemblyInline, AssemblyCategoryInline, AssemblyCourseInline]

    @admin.display(description="categories")
    def category_list(self, obj):
        category_list = obj.category.all().order_by('-name')
        return ", ".join(c.name for c in category_list)

    def save_model(self, request, obj, form, change):
        if not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'lecturer_name', 'semester',)
    list_filter = ('category',)

    exclude = ('lecturer',)

    inlines = [CourseCategoryInline]

    @admin.display(description="lecturer", ordering='lecturer__last_name')
    def lecturer_name(self, obj):
        if obj.lecturer.last_name == '':
            return f"Username: {obj.lecturer}"
        else:
            return f"{obj.lecturer.last_name}, {obj.lecturer.first_name}"

    def save_model(self, request, obj, form, change):
        if not obj.lecturer:
            obj.lecturer = request.user
        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Category)
