from traceback import print_exception

import pandoc
from .pandoc_exercise_composer import parse_exercise_tree


def gather_assembly(configuration):
    exercise_id = configuration["exercise_id"]
    exercise = Exercise.objects.get(pk=exercise_id).get_all_parent_dependencies_correctly_nested()
    return exercise


def generate_file(configuration):
    exercise = gather_assembly(configuration)
    pandoc_data = parse_exercise_tree(exercise,options=configuration)
    target_doc = pandoc.write(pandoc_data,format=configuration["doctype"])

    return target_doc

