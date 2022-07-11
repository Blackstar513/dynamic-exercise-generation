# Generated by Django 4.0.5 on 2022-07-11 08:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('exgen', '0001_squashed_0009_alter_assembly_title'), ('exgen', '0002_alter_answer_date_created'), ('exgen', '0003_alter_assemblycategory_category'), ('exgen', '0004_rename_assembly_assemblycategory_assembly'), ('exgen', '0005_alter_exercise_managers'), ('exgen', '0006_alter_exercise_managers')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Kursname')),
                ('semester', models.CharField(max_length=10, verbose_name='Semester')),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Aufgabentext')),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseDependency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hierarchy', models.CharField(choices=[('even', 'Gleichgestellt'), ('higher', 'Höhergestellt')], max_length=10, verbose_name='Hierarchie')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='exgen.exercise')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='exgen.exercise')),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='excercise_categories', to='exgen.category', verbose_name='Kategorie')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='exgen.exercise', verbose_name='Aufgabe')),
            ],
        ),
        migrations.AddField(
            model_name='exercise',
            name='category',
            field=models.ManyToManyField(through='exgen.ExerciseCategory', to='exgen.category', verbose_name='Kategorien'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exercises', to=settings.AUTH_USER_MODEL, verbose_name='Ersteller'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='dependency',
            field=models.ManyToManyField(blank=True, through='exgen.ExerciseDependency', to='exgen.exercise', verbose_name='Abhängig von'),
        ),
        migrations.CreateModel(
            name='CourseExercise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_courses', to='exgen.course', verbose_name='Kurs')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_exercises', to='exgen.exercise', verbose_name='Aufgabe')),
            ],
        ),
        migrations.CreateModel(
            name='CourseCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_categories', to='exgen.category', verbose_name='Kategorie')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_courses', to='exgen.course', verbose_name='Kurs')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ManyToManyField(through='exgen.CourseCategory', to='exgen.category', verbose_name='Kategorien'),
        ),
        migrations.AddField(
            model_name='course',
            name='exercise',
            field=models.ManyToManyField(blank=True, through='exgen.CourseExercise', to='exgen.exercise', verbose_name='Benutzte Aufgaben'),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Lösungstext')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='exgen.exercise', verbose_name='Lösung')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('text_type', models.CharField(choices=[('MARKDOWN', 'Markdown'), ('LATEX', 'Latex'), ('PLAIN', 'Plain')], default='MARKDOWN', max_length=15, verbose_name='Texttype')),
            ],
        ),
        migrations.CreateModel(
            name='ExercisePicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Bildbeschreibung')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='exgen.exercise', verbose_name='Aufgabe')),
                ('image', models.ImageField(max_length=200, upload_to='exercise_images/', verbose_name='Image')),
            ],
        ),
        migrations.AddField(
            model_name='exercise',
            name='published',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exercise',
            name='text_type',
            field=models.CharField(choices=[('MARKDOWN', 'Markdown'), ('LATEX', 'Latex'), ('PLAIN', 'Plain')], default='MARKDOWN', max_length=15, verbose_name='Texttype'),
        ),
        migrations.AddField(
            model_name='course',
            name='lecturer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Dozent'),
        ),
        migrations.CreateModel(
            name='AnswerPicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Bildbeschreibung')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='exgen.answer', verbose_name='Lösung')),
                ('image', models.ImageField(max_length=200, upload_to='answer_images/', verbose_name='Image')),
            ],
        ),
        migrations.CreateModel(
            name='Assembly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, verbose_name='Title')),
                ('published', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='exercise',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Comment'),
        ),
        migrations.AddField(
            model_name='exercise',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exercise',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='exercise',
            name='title',
            field=models.CharField(blank=True, max_length=50, verbose_name='Title'),
        ),
        migrations.CreateModel(
            name='ExerciseAssembly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveSmallIntegerField(verbose_name='Ordering number')),
                ('assembly', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_assemblies', to='exgen.assembly', verbose_name='Assembly')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assembly_exercises', to='exgen.exercise', verbose_name='Exercise')),
            ],
        ),
        migrations.CreateModel(
            name='AssemblyCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assembly', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_assemblies', to='exgen.assembly', verbose_name='Assembly')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assembly_categories', to='exgen.category', verbose_name='Categorie')),
            ],
        ),
        migrations.AddField(
            model_name='assembly',
            name='category',
            field=models.ManyToManyField(through='exgen.AssemblyCategory', to='exgen.category', verbose_name='Categories'),
        ),
        migrations.AddField(
            model_name='assembly',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assemblys', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='assembly',
            name='exercise',
            field=models.ManyToManyField(through='exgen.ExerciseAssembly', to='exgen.exercise', verbose_name='Exercises'),
        ),
        migrations.CreateModel(
            name='AssemblyCourses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assembly', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_assemblies', to='exgen.assembly', verbose_name='Assembly')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='assembly',
            field=models.ManyToManyField(through='exgen.AssemblyCourses', to='exgen.assembly', verbose_name='Assemblies'),
        ),
        migrations.AddField(
            model_name='assemblycourses',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assembly_courses', to='exgen.course', verbose_name='Course'),
        ),
        migrations.AlterField(
            model_name='assembly',
            name='title',
            field=models.CharField(max_length=50, verbose_name='Title'),
        ),
        migrations.AlterModelManagers(
            name='exercise',
            managers=[
            ],
        ),
    ]
