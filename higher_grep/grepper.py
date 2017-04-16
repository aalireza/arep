from higher_grep.utils import establish_parent_link
from higher_grep.utils import Knowledge_template
from higher_grep.utils import update_knowledge_template
from higher_grep.utils import Result
from higher_grep import Validators
from functools import namedtuple, partial
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
                self.__knowledge_template = update_knowledge_template(
                    ast_tree_with_parent_pointers=self.__ast,
                    knowledge_template=Knowledge_template(),
                    results_name=self.__name
                )
                self.constraint_list = list()
            except TypeError as e:
                print(e)

    def get_source(self):
        return self.__source

    def get_knowledge(self):
        return self.__knowledge_template

    def add_constraint(self, constraint):
        self.constraint_list.append(constraint)

    def _validator_predicates_deriver(self):

        def per_constraint_deriver(constraint):

            def validator_tracker(cls):
                results = list()
                parents = [cls.__name__]

                def wrapped(cls, parents):
                    keywords = dict()
                    for key in cls.view_actives():
                        value = getattr(cls, key)
                        if type(value).__name__ not in {
                            "Action", "Kind", "Properties"
                        }:
                            keywords[key] = value
                        else:
                            wrapped(value, parents + [key])
                    if bool(keywords):
                        results.append(namedtuple(
                            "Validator_specification", "address kwargs")(
                                parents, keywords
                            ))

                wrapped(cls, parents)
                return results

            validator_specs = validator_tracker(constraint)

            validators = list()
            for specs in validator_specs:
                print(specs)
                result = getattr(Validators, specs.address[0])
                for address_index in range(1, len(specs.address)):
                    result = getattr(result, specs.address[address_index])
                validators.append(partial(result, **specs.kwargs))

            return validators

        return [
            per_constraint_deriver(constraint)
            for constraint in self.constraint_list
        ]

    def run(self):
        validator_predicates = {
            validator_predicate
            for constraint_block in self._validator_predicates_deriver()
            for validator_predicate in constraint_block
        }
        for node in ast.walk(self.__ast):
            if all([
                    validator_predicate(
                        node=node, knowledge=self.__knowledge_template
                    ) for validator_predicate in validator_predicates
            ]):
                try:
                    yield Result(
                        name=self.__name,
                        line=node.lineno, column=node.col_offset
                    )
                except AttributeError:
                    pass

    def get_all_results(self):
        return list(self.run())
