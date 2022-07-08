from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

User = get_user_model()

MARKDOWN = 'MARKDOWN'
LATEX = 'LATEX'
PLAIN = 'PLAIN'
TEXT_TYPE_CHOICES = [
    (MARKDOWN, 'Markdown'),
    (LATEX, 'Latex'),
    (PLAIN, 'Plain')
]


class ExerciseIsRootManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(children__isnull=True)


# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kursname")
    semester = models.CharField(max_length=10, verbose_name="Semester")
    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Dozent', null=True)
    exercise = models.ManyToManyField('Exercise', through='CourseExercise', blank=True,
                                      verbose_name="Benutzte Aufgaben")
    category = models.ManyToManyField('Category', through='CourseCategory', verbose_name="Kategorien")
    assembly = models.ManyToManyField('Assembly', through='AssemblyCourses', verbose_name="Assemblies")

    def __str__(self):
        return f"{self.semester}: {self.name}"


class Exercise(models.Model):
    objects = models.Manager()
    root = ExerciseIsRootManager()
    title = models.CharField(verbose_name="Title", max_length=50, blank=True, null=False)
    text = models.TextField(verbose_name="Aufgabentext")
    text_type = models.CharField(verbose_name="Texttype", max_length=15, choices=TEXT_TYPE_CHOICES, default=MARKDOWN)

    comment = models.TextField(verbose_name="Comment", blank=True)

    published = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(User, related_name='exercises', on_delete=models.SET_NULL, blank=True, null=True,
                                verbose_name="Ersteller")
    dependency = models.ManyToManyField('self', through='ExerciseDependency', through_fields=('child', 'parent'),
                                        symmetrical=False, blank=True, verbose_name="Abhängig von")
    category = models.ManyToManyField('Category', through='ExerciseCategory', verbose_name="Kategorien")

    def is_root(self):
        return not self.children.exists()

    def get_root(self):
        if self.is_root():
            return self
        else:
            # there can be only on root even if there are multiple depenencies (assuming the exercise is correctly configured)
            # get the first dependency where self is the child
            return self.children.all()[0].parent.get_root()

    def get_all_parent_dependencies(self):
        
        # list of all even dependencies
        even_dependencies = []
        # list of all higher dependencies
        higher_dependencies = []

        # get all dependencies where self is the child recursively
        for d in self.children.all():
            parent_dependencies = d.parent.get_all_parent_dependencies()

            if d.hierarchy == 'higher':
                higher_dependencies.extend(parent_dependencies)
            else:
                even_dependencies.extend(parent_dependencies)

        # list of all parent dependencies
        dependencies = []

        # append higher dependencies if there are any
        if higher_dependencies:
            dependencies.append(tuple(higher_dependencies))
        # keep even dependencies on same level as self
        dependencies.extend(even_dependencies)
        # add self
        dependencies.append(self)
        # ensure that no dependency doubling exists (as long as there is no weird exercise setup)
        return list(dict.fromkeys(tuple(dependencies)))

    def get_all_parent_dependencies_correctly_nested(self):
        def reverse_nesting(nested_list, nesting_level=0):
            new_list = []
            deep_list = []
            if not (isinstance(nested_list, list) or isinstance(nested_list, tuple)):
                return nesting_level + 1, nested_list

            for elem in nested_list:
                if isinstance(elem, list) or isinstance(elem, tuple):
                    nesting_level, result_list = reverse_nesting(elem, nesting_level)
                    new_list.extend(result_list)
                else:
                    deep_list.append(elem)

            # for _ in range(nesting_level):
            #    deep_list = [deep_list]
            temp = new_list
            for _ in range(nesting_level - 1):
                temp = temp[-1]

            if nesting_level == 0:
                temp.extend(deep_list)
            else:
                temp.append(deep_list)
            return nesting_level + 1, new_list

        parent_dependencies = self.get_all_parent_dependencies()
        _, reverse_nested_dependencies = reverse_nesting(parent_dependencies)

        return reverse_nested_dependencies

    def get_all_child_dependencies(self):
        # list of all even children
        even_children = []
        # list of all lower children
        lower_children = []

        # get all dependencies where self is the parent recursively
        for d in self.parents.all():
            child_dependencies = d.child.get_all_child_dependencies()

            if d.hierarchy == 'higher':
                lower_children.extend(child_dependencies)
            else:
                even_children.extend(child_dependencies)

        # list of all children
        children = [self]
        # keep even children on same level as self
        children.extend(even_children)
        # append lower children if there are any
        if lower_children:
            # ensure that no lower children doubling exists (as long as there is no weird exercise setup/dependencies only exist one layer up)
            children.append(tuple(dict.fromkeys(tuple(lower_children))))

        # ensure that no even children doubling exists (as long as there is no weird exercise setup)
        return list(dict.fromkeys(tuple(children)))

    def duplicate(self, creator):
        new_ex = Exercise.objects.create()
        new_ex.title = self.title
        new_ex.text = self.text
        new_ex.text_type = self.text_type
        new_ex.comment = self.comment
        new_ex.creator = creator

        for answer in self.answers.all():
            answer.duplicate(self)

        for pic in self.pictures.all():
            pic.duplicate(new_ex)

        for cat in self.category.all():
            new_ex.category.add(cat)

        for dependency in self.parents.all():
            new_child = dependency.child.duplicate(creator)
            new_child.dependency.add(new_ex, through_defaults={'hierarchy': dependency.hierarchy})
            new_child.save()

        new_ex.save()
        return new_ex

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('exgen:answer_bottom_up', kwargs={'pk': self.pk})

    def __str__(self):
        if self.title:
            return self.title
        else:
            text = f"{self.text[:41]}..." if len(self.text) > 43 else self.text
            return f"Text: {text}"


class Answer(models.Model):
    text = models.TextField(verbose_name="Lösungstext")
    text_type = models.CharField(verbose_name="Texttype", max_length=15, choices=TEXT_TYPE_CHOICES, default=MARKDOWN)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    exercise = models.ForeignKey(Exercise, related_name='answers', on_delete=models.CASCADE, verbose_name='Lösung')

    def duplicate(self, exercise):
        new_answer = Answer()
        new_answer.text = self.text
        new_answer.text_type = self.text_type

        for pic in self.pictures.all():
            pic.duplicate(new_answer)

        new_answer.exercise = exercise

        exercise.save()
        new_answer.save()

        return new_answer

    def __str__(self):
        return f"{self.text[:20]}..."


class ExercisePicture(models.Model):
    image = models.ImageField(upload_to='exercise_images/', verbose_name="Image", max_length=200)
    text = models.TextField(verbose_name="Bildbeschreibung")
    exercise = models.ForeignKey(Exercise, related_name='pictures', on_delete=models.CASCADE, verbose_name="Aufgabe")

    def duplicate(self, exercise):
        new_ex_pic = ExercisePicture()
        # TODO: only take real picture name not folder
        new_ex_pic.image = ContentFile(self.image.read(), self.image.name)
        new_ex_pic.text = self.text
        new_ex_pic.exercise = exercise

        exercise.save()
        new_ex_pic.save()

        return new_ex_pic

    def __str__(self):
        return f"{self.image}"


class AnswerPicture(models.Model):
    image = models.ImageField(upload_to='answer_images/', verbose_name="Image", max_length=200)
    text = models.TextField(verbose_name="Bildbeschreibung")
    answer = models.ForeignKey(Answer, related_name='pictures', on_delete=models.CASCADE, verbose_name="Lösung")

    def duplicate(self, answer):
        new_ans_pic = AnswerPicture()
        # TODO: only take real picture name not folder
        new_ans_pic.image = ContentFile(self.image.read(), self.image.name)
        new_ans_pic.text = self.text
        new_ans_pic.answer = answer

        answer.save()
        new_ans_pic.save()

        return new_ans_pic

    def __str__(self):
        return f"{self.image}"


class Category(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100)

    def __str__(self):
        return self.name


class Assembly(models.Model):
    title = models.CharField(verbose_name="Title", max_length=50, blank=False)

    published = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(User, related_name='assemblys', on_delete=models.SET_NULL, blank=True, null=True,
                                verbose_name="Creator")
    exercise = models.ManyToManyField('Exercise', through='ExerciseAssembly', verbose_name="Exercises")
    category = models.ManyToManyField('Category', through='AssemblyCategory', verbose_name="Categories")

    def duplicate(self, creator):
        new_assembly = Assembly.objects.create()
        new_assembly.creator = creator
        new_assembly.title = self.title

        for ex in self.exercise_assemblies.all():
            new_assembly.exercise.add(ex.exercise, through_defaults={'rank': ex.rank})

        for cat in self.category.all():
            new_assembly.category.add(cat)

        new_assembly.save()

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('exgen:index')


class ExerciseDependency(models.Model):
    HIERARCHY_CHOICES = [
        ('even', "Gleichgestellt"),
        ('higher', "Höhergestellt")
    ]

    parent = models.ForeignKey(Exercise, related_name='parents', on_delete=models.CASCADE)
    child = models.ForeignKey(Exercise, related_name='children', on_delete=models.CASCADE)
    hierarchy = models.CharField(max_length=10, choices=HIERARCHY_CHOICES, verbose_name="Hierarchie")


class ExerciseCategory(models.Model):
    category = models.ForeignKey(Category, related_name='excercise_categories', on_delete=models.CASCADE,
                                 verbose_name="Kategorie")
    exercise = models.ForeignKey(Exercise,  related_name='exercises', on_delete=models.CASCADE,
                                 verbose_name="Aufgabe")


class CourseExercise(models.Model):
    course = models.ForeignKey(Course, related_name='exercise_courses', on_delete=models.CASCADE, verbose_name="Kurs")
    exercise = models.ForeignKey(Exercise, related_name='course_exercises', on_delete=models.CASCADE,
                                 verbose_name="Aufgabe")


class CourseCategory(models.Model):
    course = models.ForeignKey(Course, related_name='category_courses', on_delete=models.CASCADE, verbose_name="Kurs")
    category = models.ForeignKey(Category, related_name='course_categories', on_delete=models.CASCADE,
                                 verbose_name="Kategorie")


class ExerciseAssembly(models.Model):
    exercise = models.ForeignKey(Exercise, related_name='assembly_exercises', on_delete=models.CASCADE, verbose_name="Exercise")
    assembly = models.ForeignKey(Assembly, related_name='exercise_assemblies', on_delete=models.CASCADE, verbose_name="Assembly")

    rank = models.PositiveSmallIntegerField(verbose_name="Ordering number")


class AssemblyCategory(models.Model):
    assembly = models.ForeignKey(Assembly, related_name='category_assemblies', on_delete=models.CASCADE, verbose_name="Assembly")
    category = models.ForeignKey(Category, related_name='assembly_categories', on_delete=models.CASCADE,
                                 verbose_name="Categorie")


class AssemblyCourses(models.Model):
    course = models.ForeignKey(Course, related_name='assembly_courses', on_delete=models.CASCADE, verbose_name="Course")
    assembly = models.ForeignKey(Assembly, related_name='course_assemblies', on_delete=models.CASCADE,
                                 verbose_name="Assembly")
