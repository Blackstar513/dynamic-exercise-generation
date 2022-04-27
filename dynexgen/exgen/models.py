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
    dependency = models.ManyToManyField('self', through='ExerciseDependency', through_fields=('parent', 'child'),
                                        symmetrical=False, blank=True, verbose_name="Abhängig von")
    category = models.ManyToManyField('Category', through='ExerciseCategory', verbose_name="Kategorien")

    def __str__(self):
        return f"{self.text[:20]}..."


class Answer(models.Model):
    text = models.TextField(verbose_name="Lösungstext")
    exercise = models.ForeignKey(Exercise, related_name='answers', on_delete=models.CASCADE, verbose_name='Lösung')

    def __str__(self):
        return f"{self.text[:20]}..."


class ExercisePicture(models.Model):
    location = models.CharField(verbose_name="Pfad", max_length=200)
    text = models.TextField(verbose_name="Bildbeschreibung")
    exercise = models.ForeignKey(Exercise, related_name='pictures', on_delete=models.CASCADE, verbose_name="Aufgabe")

    def __str__(self):
        return f"{self.location}"


class AnswerPicture(models.Model):
    location = models.CharField(verbose_name="Pfad", max_length=200)
    text = models.TextField(verbose_name="Bildbeschreibung")
    exercise = models.ForeignKey(Answer, related_name='pictures', on_delete=models.CASCADE, verbose_name="Lösung")

    def __str__(self):
        return f"{self.location}"


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
