from traceback import print_exception

import pandoc
from .pandoc_exercise_composer import latex_from_fragments
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

    assembly = Assembly.objects.get(pk=assembly_ids[0])

    fragment_collection = FragmentCollection(configuration)
    fragment_collection.title = assembly.title

    for exercise in assembly.exercise.iterator():
        fragment_collection.add(exercise)
    return fragment_collection

def gather_exercises(exercise_ids, configuration):
    fragment_collection = FragmentCollection(configuration)
    fragment_collection.title = "Exercise Collection"
    for exid in exercise_ids:
        fragment_collection.add(Exercise.objects.get(pk=exid))
    return fragment_collection


def gather_fragments(configuration):
    exercise_ids = configuration.getlist("exercise")
    assembly_ids = configuration.getlist("assembly")
    if bool(exercise_ids) and bool(assembly_ids):
        raise TooManyFieldsSent(
                "exercises: "+str(exercise_ids)+
                " assemblies: "+str(assembly_ids))
    if not exercise_ids+assembly_ids:
        raise BadRequest("needs exercise or assmebly field")

    if exercise_ids:
        return gather_exercises(exercise_ids, configuration)
    if assembly_ids:
        return gather_assemblies(assembly_ids, configuration)

    raise Exception("How did we get here?")



def generate_file(configuration):
    fragment_collection = gather_fragments(configuration)
    pandoc_data = latex_from_fragments(fragment_collection)
    target_doc = pandoc.write(pandoc_data,format=configuration["doctype"])

    return target_doc

