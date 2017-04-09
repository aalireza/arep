from functools import partial
from higher_grep import validators
from higher_grep.core import establish_parent_link
from higher_grep.core import Constraints_template
from higher_grep.core import Knowledge_template
from higher_grep.core import update_knowledge_template
from higher_grep.core import Result
import ast
import os


class Grepper(object):
    def __init__(self, source_abs_path):
        assert os.path.exists(source_abs_path), "Path doesn't exist"
        with open(source_abs_path, 'r') as f:
            try:
                self.__ast = establish_parent_link(ast.parse(f.read()))
                self.__source = f
                self.__name = os.path.basename(source_abs_path)
                self.__constraints_template = Constraints_template()
                self.__knowledge_template = update_knowledge_template(
                    ast_tree_with_parent_pointers=self.__ast,
                    knowledge_template=Knowledge_template(),
                    results_name=self.__name
                )
            except TypeError as e:
                print(e)

    def get_source(self):
        return self.__source[:]

    def get_knowledge(self):
        return self.__knowledge_template

    def get_constraints(self):
        unfiltered_constraints = {
            constraint_type: {
                job: {
                    arg: self.__constraints_template[constraint_type][job][arg]
                    for arg in self.__constraints_template[constraint_type][
                        job]
                    if (self.__constraints_template[constraint_type][job][arg]
                        is not None)
                }
                for job in self.__constraints_template[constraint_type]
            }
            for constraint_type in self.__constraints_template
        }
        constraints = {
            constraint_type: {
                job: {
                    arg: unfiltered_constraints[constraint_type][job][arg]
                    for arg in unfiltered_constraints[constraint_type][job]
                }
                for job in unfiltered_constraints[constraint_type]
                if len(unfiltered_constraints[constraint_type][job]) != 0
            }
            for constraint_type in unfiltered_constraints
        }
        return constraints

    def reset_constraints(self):
        self.__constraints_template = Constraints_template()

    def _validator_predicate_extracter(self):
        constraints = self.get_constraints()
        validator_predicates = {
            constraint_type: {
                job: (validators.__dict__[
                    "{}".format(constraint_type)].__dict__[
                        "{}".format(job)]
                ) for job in constraints[constraint_type]
            }
            for constraint_type in constraints
        }
        validator_partial_predicates = {
            partial(validator_predicates[constraint_type][job],
                    **{(lambda key: (
                        key if key == 'should_consider' else
                        "_{}".format(key)
                    ))(key): value
                       for key, value in (
                               self.__constraints_template[
                                   constraint_type][job].items()
                       )})
            for constraint_type in validator_predicates
            for job in validator_predicates[constraint_type]
        }
        return validator_partial_predicates

    def add_constraint(self, constraint):
        assert bool(constraint.__name__ == "constraint_template_modifier"), (
            "Invalid constraint"
        )
        constraint(self.__constraints_template)

    def run(self):
        validator_predicates = self._validator_predicate_extracter()
        for node in ast.walk(self.__ast):
            if all([
                    validator_predicate(
                        node=node, _knowledge=self.get_knowledge()
                    ) for validator_predicate in validator_predicates
            ]):
                yield Result(
                    name=self.__name, line=node.lineno, column=node.col_offset
                )

    def get_all_results(self):
        return list(self.run())
