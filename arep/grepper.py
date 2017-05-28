from arep.utils import (
    establish_parent_link, Knowledge_template, update_knowledge_template,
    Result
)
from arep import Validators
from functools import namedtuple, partial
import ast
import os


class Grepper(object):
    """
    Attributes
    ----------
    constraint_list
        The list of all the constraints that are being considered.
        It automatically "AND"s all the constraints. For now assign
        `consideration` to False for a constraint to `NOT` it and union
        greppers for "OR".
    __ast
        The modified AST of the program where each node with a parent has a
        pointer to it.
    __source
        str of the source code
    __name
        File name of the program
    __knowledge_template
        A dictionary of some of the knowledge that can be automatically gained
        by looking at the entire AST. For example, it helps to see whether
        `f()` is a class or a function or alike. It can't be known without it.

    Methods
    -------
    get_source()
    get_knowledge()
    run()
        A generator that yields nodes that satisfy all the constraints.
    all_results()
        Returns a list of all the results by exhusting the generator above.
    """
    def __init__(self, source_abs_path):
        """
        Parameters
        ----------
        source_abs_path : str
            Absolute path to the python source code that'll be parsed.
        """
        assert os.path.exists(source_abs_path), "Path doesn't exist"
        with open(source_abs_path, 'r') as f:
            self.__ast = establish_parent_link(ast.parse(f.read()))
            self.__source = f
            self.__name = os.path.basename(source_abs_path)
            self.__knowledge_template = update_knowledge_template(
                ast_tree_with_parent_pointers=self.__ast,
                knowledge_template=Knowledge_template(),
            )
            self.constraint_list = list()

    def get_source(self):
        """
        Returns
        -------
        str
        """
        return self.__source

    def get_knowledge(self):
        """
        Returns
        -------
        {str: type}
        """
        return self.__knowledge_template

    def _validator_predicates_deriver(self):
        """
        Collects all of the functions that need to be checked on each node
        for satisfaction.

        Returns
        -------
        [(*args, **kwargs) -> {True, False}]
        """

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
        """
        Yields
        ------
        Result
            An object with `name`, `line` and `column` attributes.
        """
        validator_predicates = {
            validator_predicate
            for constraint_block in self._validator_predicates_deriver()
            for validator_predicate in constraint_block
        }
        for node in ast.walk(self.__ast):
            if all([validator_predicate(
                    node=node, knowledge=self.__knowledge_template
            ) for validator_predicate in validator_predicates]):
                try:
                    yield Result(
                        name=self.__name,
                        line=node.lineno, column=node.col_offset
                    )
                except AttributeError:
                    pass

    def all_results(self):
        """
        Returns
        -------
        [Result]
        """
        return list(self.run())
