# Generated by Django 4.0.5 on 2022-07-04 19:18

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('exgen', '0004_rename_assembly_assemblycategory_assembly'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='exercise',
            managers=[
                ('root', django.db.models.manager.Manager()),
            ],
        ),
    ]