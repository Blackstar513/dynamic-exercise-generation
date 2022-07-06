from traceback import print_exception

import pandoc
from .pandoc_exercise_composer import parse_exercise_tree


from ..models import Exercise, ExerciseDependency


def gather_assembly(configuration):
    exercise_ids = configuration.getlist("exercise_id")
    exercise = []
    for exid in exercise_ids:
        exercise += Exercise.objects.get(pk=exid).get_all_parent_dependencies_correctly_nested()
    return exercise


def generate_file(configuration):
    exercise = gather_assembly(configuration)
    pandoc_data = parse_exercise_tree(exercise,options=configuration)
    target_doc = pandoc.write(pandoc_data,format=configuration["doctype"])

    return target_doc

