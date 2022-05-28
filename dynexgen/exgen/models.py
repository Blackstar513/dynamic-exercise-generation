from django.db import models


# Create your models here.
class Lecturer(models.Model):
    forename = models.CharField(max_length=50, verbose_name="Vorname")
    surname = models.CharField(max_length=50, verbose_name="Nachname")

    def __str__(self):
        return f"{self.forename} {self.surname}"


class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kursname")
    semester = models.CharField(max_length=10, verbose_name="Semester")
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, verbose_name='Dozent')
    exercise = models.ManyToManyField('Exercise', through='CourseExercise', blank=True,
                                       verbose_name="Benutzte Aufgaben")
    category = models.ManyToManyField('Category', through='CourseCategory', verbose_name="Kategorien")

    def __str__(self):
        return f"{self.semester}: {self.name}"


class Exercise(models.Model):
    text = models.TextField(verbose_name="Aufgabentext")
    creator = models.ForeignKey(Lecturer, related_name='exercises', on_delete=models.SET_NULL, blank=True, null=True,
                                verbose_name="Ersteller")
    dependency = models.ManyToManyField('self', through='ExerciseDependency', through_fields=('child', 'parent'),
                                        symmetrical=False, blank=True, verbose_name="Abhängig von")
    category = models.ManyToManyField('Category', through='ExerciseCategory', verbose_name="Kategorien")

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

    def __str__(self):
        return f"{self.text[:20]}..."


class Answer(models.Model):
    text = models.TextField(verbose_name="Lösungstext")
    exercise = models.ForeignKey(Exercise, related_name='answers', on_delete=models.CASCADE, verbose_name='Lösung')

    def __str__(self):
        return f"{self.text[:20]}..."


class ExercisePicture(models.Model):
    image = models.ImageField(upload_to='exercise_images/', verbose_name="Image", max_length=200)
    text = models.TextField(verbose_name="Bildbeschreibung")
    exercise = models.ForeignKey(Exercise, related_name='pictures', on_delete=models.CASCADE, verbose_name="Aufgabe")

    def __str__(self):
        return f"{self.image}"


class AnswerPicture(models.Model):
    image = models.ImageField(upload_to='answer_images/', verbose_name="Image", max_length=200)
    text = models.TextField(verbose_name="Bildbeschreibung")
    exercise = models.ForeignKey(Answer, related_name='pictures', on_delete=models.CASCADE, verbose_name="Lösung")

    def __str__(self):
        return f"{self.image}"


class Category(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100)

    def __str__(self):
        return self.name


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
