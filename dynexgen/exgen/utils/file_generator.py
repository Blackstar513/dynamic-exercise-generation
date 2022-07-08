from traceback import print_exception

import pandoc
from .pandoc_exercise_composer import parse_exercise_tree
from django.core.exceptions import TooManyFieldsSent, BadRequest


from ..models import Exercise, Assembly


class FragmentCollection:
    def __init__(self, configuration):
        self.title = ""
        self.tree = []
        self.configuration = {
                "nest_down":False,
                "answers":False,
                }
        for key, default_value in self.configuration.items():
            self.configuration[key] = configuration.get(key,default_value)
    def add(self, exercise):
        self.tree += exercise.get_all_parent_dependencies_correctly_nested()


def gather_assemblies(assembly_ids, configuration):
    if len(assembly_ids) != 1:
        raise BadRequest("Only one assembly ay be requested")
    assembly_id = assembly_ids[0]
    assembly = Assembly.objects.get(pk=assembly_id)
    fragment_collection = FragmentCollection(configuration)
    for exercise in assembly.exercise.iterator():
        fragment_collection.add(exercise)
    return fragment_collection.tree

def gather_exercises(exercise_ids, configuration):
    fragment_collection = FragmentCollection(configuration)
    for exid in exercise_ids:
        fragment_collection.add(Exercise.objects.get(pk=exid))
    return fragment_collection.tree


def gather_fragments(configuration):
    exercise_ids = configuration.getlist("exercise")
    assembly_ids = configuration.getlist("assembly")
    if bool(exercise_ids) and bool(assembly_ids):
        raise TooManyFieldsSent("exercises: "+str(exercise_ids)+" assemblies: "+str(assembly_ids))
    if not exercise_ids+assembly_ids:
        raise BadRequest("needs exercise or assmebly field")

    if exercise_ids:
        return gather_exercises(exercise_ids, configuration)
    if assembly_ids:
        return gather_assemblies(assembly_ids, configuration)

    raise Exception("How did we get here?")



def generate_file(configuration):
    exercise = gather_fragments(configuration)
    pandoc_data = parse_exercise_tree(exercise,options=configuration)
    target_doc = pandoc.write(pandoc_data,format=configuration["doctype"])

    return target_doc

