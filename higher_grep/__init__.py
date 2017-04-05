from __future__ import absolute_import, division, print_function
from collections import namedtuple
from functools import partial
import ast
import os
import sys

if sys.version_info > (3, 0):
    long = int


_Constraints_template = {
    'Action': {
        'Call': {
            'should_consider': None,
        },
        'Initialization': {
            'should_consider': None,
        },
        'Import': {
            'should_consider': None,
            'id': None,
            'from': None,
            'from_id': None,
            'as': None,
        },
        'Definition': {
            'should_consider': None,
        },
        'Assignment': {
            'should_consider': None,
        },
        'Assertion': {
            'should_consider': None,
        },
        'Looping': {
            'should_consider': None,
            'for': None,
            'while': None,
            'for_else': None,
        },
        'Conditional': {
            'should_consider': None,
            'with_elif': None,
            'with_else': None,
            'is_ifexp': None,
        },
        'With': {
            'should_consider': None,
            'as': None,
        },
        'Deletion': {
            'should_consider': None,
        },
        'Indexing': {
            'should_consider': None,
        },
        'Trying': {
            'should_consider': None,
            'with_all_except_types': None,
            'without_any_except_types': None,
            'with_except_ases': None,
            'with_finally': None,
        },
        'Raising': {
            'should_consider': None,
            'error_type': None,
            'error_message': None,
        },
        'Yielding': {
            'should_consider': None,
            'in_comprehension': None,
            'yield_from': None,
        },
        'Making_Global': {
            'should_consider': None,
            'id': None,
        },
        'Making_Nonlocal': {
            'should_consider': None,
            'id': None,
        }
    },
    'Kind': {
        'Variables': {
            'should_consider': None,
            'id': None,
            'is_attribute': None,
            'in_global': None,
        },
        'STD_Types': {
            'should_consider': None,
            'type': None,
        },
        'Functions': {
            'should_consider': None,
            'id': None,
            'in_global': None,
            'is_lambda': None,
            'is_decorator': None,
        },
        'Decorators': {
            'should_consider': None,
            'id': None,
        },
        'Classes': {
            'should_consider': None,
            'id': None,
            'in_global': None,
            'superclass_type': None,
        },
        'Attributes': {
            'should_consider': None,
            'id': None,
            'class_id': None,
        },
        'Methods': {
            'should_consider': None,
            'id': None,
            'class_id': None,
        },
        'Generators': {
            'should_consider': None,
            'id': None,
        },
        'Comprehensions': {
            'should_consider': None,
            'of_list': None,
            'of_dict': None,
            'of_gen': None,
        },
        'Operations': {
            'should_consider': None,
            'operation_str': None,
            'is_unary': None,
            'is_binary': None,
        },
    },
    'Location_Limit': {
        'Line_Numbers': {
            'minimum': None,
            'maximum': None,
        },
        'Column_Numbers': {
            'minimum': None,
            'maximum': None,
        }
    }
}

def _establish_parent_link(tree):
    to_be_processed = [tree]
    while to_be_processed:
        try:
            current_parent = to_be_processed.pop(0)
            children = current_parent.body
            for child in children:
                child._parent = current_parent
            to_be_processed.extend(children)
        except AttributeError:
            if to_be_processed:
                to_be_processed.pop(0)
        except IndexError:
            continue
    if (not bool(to_be_processed)):
        return tree
    return False


def _constraint_template_modifier_func_maker(
        main, job, should_consider=None, args=None):
    def f(template):
        if should_consider is not None:
            template[main][job]['should_consider'] = should_consider
        if args is not None:
            for key, value in args:
                template[main][job][key] = value
    return f


class Action(object):
    _constraint_modifier_localized = partial(
        _constraint_template_modifier_func_maker, main='Action')

    def Call(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Call', should_consider=should_consider)

    def Initialization(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Initialization', should_consider=should_consider)

    def Import(_id=None, _from=None, _from_id= None, _as=None,
               should_consider=True):
        return Action._constraint_modifier_localized(
            job='Import', should_consider=should_consider, args=[
                ('id', _id),
                ('from', _from),
                ('as', _as)])

    def Definition(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Definition', should_consider=should_consider)

    def Assignment(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Assignment', should_consider=should_consider)

    def Assertion(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Assertion', should_consider=should_consider)

    def Looping(_for=None, _while=None, _for_else=None,
                should_consider=True):
        return Action._constraint_modifier_localized(
            job='Looping', should_consider=should_consider, args=[
                ('for', _for),
                ('while', _while),
                ('for_else', _for_else)])

    def Conditional(_with_elif=None, _with_else=None,
                    should_consider=True):
        return Action._constraint_modifier_localized(
            job='Conditional', should_consider=should_consider, args=[
                ('with_elif', _with_elif),
                ('with_else', _with_else)])

    def With(_as=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job="With", should_consider=should_consider, args=[('as', _as)])

    def Deletion(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Deletion', should_consider=should_consider)

    def Indexing(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Indexing', should_consider=should_consider)

    def Trying(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Trying', should_consider=should_consider, args=[
                ('with_except_types', _with_except_types),
                ('without_except_types', _without_except_types),
                ('with_except_ases', _with_except_ases),
                ('with_finally', _with_finally)])

    def Raising(should_consider=True):
        return Action._constraint_modifier_localized(
            job='Raising', should_consider=should_consider, args=[
                ('error_type', _error_type),
                ('error_message', _error_message)])

    def Yielding(_yield_from, _in_comprehension, should_consider=True):
        return Action._constraint_modifier_localized(
            job='Yielding', should_consider=should_consider, args=[
                ('in_comprehension', _in_comprehension),
                ('yield_from', _yield_from)])

    def Making_Global(_id=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job='Making_Global', should_consider=should_consider, args=[
                ('id',_id)])

    def Making_Nonlocal(_id=None, should_consider=True):
        return Action._constraint_modifier_localized(
            job='Making_Nonlocal', should_consider=should_consider, args=[
                ('id',_id)])


class Kind(object):
    _constraint_modifier_localized = partial(
        _constraint_template_modifier_func_maker, main='Kind')

    def Variables(_id=None, _is_attribute=None, _in_global=None,
                  should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Variables', should_consider=should_consider, args=[
                ('id', _id),
                ('is_attribute', _is_attribute),
                ('in_global', _in_global)])

    def STD_Types(_type=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='STD_Types', should_consider=should_consider, args=[
                ('type', _type)])

    def Functions(_id=None, _in_global=None, _is_lambda=None, _is_decorator=None,
                  should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Functions', should_consider=should_consider, args=[
                ('id', _id),
                ('in_global', _in_global),
                ('is_lambda', _is_lambda),
                ('is_decorator', _is_decorator)])

    def Decorators(_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Decorators', should_consider=should_consider, args=[
                ('id', _id)])

    def Classes(_id=None, _in_global=None, _superclass_type=None,
                should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Classes', should_consider=should_consider, args=[
                ('id', _id),
                ('in_global', _in_global),
                ('superclass_type', _superclass_type)])

    def Attributes(_id=None, _class_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Generators', should_consider=should_consider, args=[
                ('id', _id),
                ('class_id', _class_id)])

    def Methods(_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Methods', should_consider=should_consider, args=[
                ('id', _id),
                ('class_id', _class_id)])

    def Generators(_id=None, should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Generators', should_consider=should_consider, args=[
                ('id', _id)])

    def Comprehensions(_of_list=None, _of_dict=None, _of_gen=None,
                       should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Comprehensions', should_consider=should_consider, args=[
                ('of_list', _of_list),
                ('of_dict', _of_dict),
                ('of_gen', _of_gen)])

    def Operations(_operation_str=None, _is_unary=None, _is_binary=None,
                   should_consider=True):
        return Kind._constraint_modifier_localized(
            job='Operations', should_consider=should_consider, args=[
                ('operation_str', _operation_str),
                ('is_unary', _is_unary),
                ('is_binary', _is_binary)])

class Location_Limit(object):
    _constraint_modifier_localized = partial(
        _constraint_template_modifier_func_maker, main='Location_Limit')

    def Line_Numbers(starting_line=None, ending_line=None):
        return Location_Limit._constraint_modifier_localized(
            job='Line_Numbers', args=[
                ('minimum', starting_line),
                ('maximum', ending_line)])

    def Column_Numbers(starting_column=None, ending_column=None):
        return Location_Limit._constraint_modifier_localized(
            job='Column_Numbers', args=[
                ('minimum', starting_column),
                ('maximum', ending_column)])


class _Validators(object):
    def Action_Call(node, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) == ast.Call))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Initialization(node, should_consider):
        raise NotImplementedError

    def Action_Import(node, _id, _from, _from_id, _as, should_consider):
        if not should_consider:
            False
        try:
            partial_validators = set()
            if _from is False:
                partial_validators.add(bool(type(node) == ast.Import))
            else:
                partial_validators.add(bool(type(node) in {
                    ast.Import, ast.ImportFrom}))
            if _id is not None:
                partial_validators.add(bool(_id in {node.name
                                                    for node in node.names}))
            if _from_id is not None:
                partial_validators.add(bool(_from_id == node.module))
            if _as is not None:
                partial_validators.add(bool(
                    _as in [name.asname for name in node.names]))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Definition(node, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) in {ast.FunctionDef,
                                                       ast.ClassDef}))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Assignment(node, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) == ast.Assign))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Assertion(node, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) == ast.Assert))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Looping(node, _for, _while, _for_else, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) in {ast.For, ast.While}))
            if _for is not None:
                partial_validators.add(bool(_for) and
                                       bool(type(node) == ast.For))
            if _while is not None:
                partial_validators.add(bool(_while) and
                                       bool(type(node) == ast.While))
            if _for_else is not None:
                partial_validators.add(bool(_for_else) and
                                       bool(type(node) == ast.For) and
                                       bool(len(node.orelse) != 0))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Conditional(node, _with_elif, _with_else, _is_ifexp,
                           should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) in {ast.If, ast.IfExp}))
            if _with_elif is not None:
                partial_validators.add(bool(_with_elif) and (
                    any([(type(possibly_orelse) == ast.If)
                         for possibly_orelse in node.orelse])))
            if _with_else is not None:
                partial_validators.add(bool(_with_else) and
                                       bool(len(node.orelse) != 0))
            if _is_ifexp is not None:
                partial_validators.add(bool(_is_ifexp) and
                                       bool(type(node) == ast.IfExp))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_With(node, _as, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) == ast.With))
            if _as is not None:
                partial_validators.add(bool(_as) and
                                       bool(any([
                                           _as == with_item.optional_vars.id
                                           for with_item in node.items])))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Deletion(node, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) is ast.Delete))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Indexing(node, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) is ast.Subscript))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Trying(node, _with_all_except_types, _without_any_except_types,
                      _with_except_ases, _with_finally, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) == ast.Try))
            if _with_all_except_types is not None:
                partial_validator.add(
                    bool(_with_all_except_types) and
                    bool(all([(except_type.__name__ in {
                        handler.type.id
                        for handler in node.handlers
                        if type(handler) is ast.ExceptHandler})
                             for except_type in _with_all_except_types])))
            if _without_any_except_types is not None:
                partial_validator.add(
                    bool(_without_any_except_types) and
                    bool(not any([(except_type.__name__ in {
                        handler.type.id
                        for handler in node.handlers
                        if type(handler) is ast.ExceptHandler})
                                  for except_type in _with_all_except_types])))
            if _with_except_ases is not None:
                partial_validators.add(
                    bool(_with_except_ases) and
                    bool(all([except_as in {
                        handler.name
                        for handler in node.handlers
                        if type(handler) is ast.ExceptHandler
                    } for except_as in _with_except_ases])))
            if _with_finally is not None:
                partial_validators.add(
                    bool(_with_finally) and
                    bool(len(node.finalbody) != 0))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Raising(node, _error_type, _error_message, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) is ast.Raise))
            if _error_type is not None:
                partial_validators.add(
                    bool(_error_type) and
                    bool(_error_type.__name__ == node.exc.id))
            if _error_message is not None:
                partial_validators.add(
                    bool(_error_message) and
                    bool(_error_message in {str(messages)
                                            for messages in node.exc.args}))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Yielding(node, _in_comprehension, _yield_from, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            if _incomprehension is not None:
                if _in_comprehension:
                    partial_validators.add(bool(type(node) in {
                        ast.Yield, ast.YieldFrom, ast.GeneratorExp}))
                else:
                    partial_validators.add(bool(type(node) in {
                        ast.Yield, ast.YieldFrom}))
            if _yield_from is not None:
                partial_validators.add(bool(_yield_from) and
                                       bool(type(node) is ast.YieldFrom))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Making_Global(node, _id, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) is ast.Global))
            if _id is not None:
                partial_validators.add(bool(_id) and
                                       bool(_id in [str(name)
                                                    for name in node.names]))
            return all(partial_validators)
        except AttributeError:
            return False

    def Action_Making_Nonlocal(node, _id, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) is ast.Nonlocal))
            if _id is not None:
                partial_validators.add(bool(_id) and
                                       bool(_id in [str(name)
                                                    for name in node.names]))
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Variables(node, _id, _is_attribute, _in_global, should_consider):
        builtin_datatypes = {type, int, float, long, bool, dict, set, frozenset,
                            list, dict, bytes, bytearray, memoryview}
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(
                bool(type(node) is ast.Name) or
                bool(node != node._parent.func))
            partial_validators.add(bool(node.id not in
                                        list(map(lambda x: x.__name__,
                                                 builtin_datatypes))))
            if _id is not None:
                partial_validators.add(bool(_id) and bool(_id == node.id))
            if _is_attribute in {False, True}:
                partial_validators.add(bool(_is_attribute) and bool(
                    type(node._parent) is ast.Attribute))
            if _in_global is not None:
                if type(node) is ast.Name:
                    current_node = node
                    while (type(current_node) not in {
                            ast.ClassDef, ast.FunctionDef, ast.Lambda}):
                        if type(current_node) is ast.Module:
                            partial_validators.add(bool(_in_global))
                            break
                        current_node = current_node._parent
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_STD_Types(node, _type, should_consider):
        builtin_datatypes = {type, int, float, long, bool, dict, set, frozenset,
                            list, dict, bytes, bytearray, memoryview}
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(type(node) is ast.Name) and
                                   bool(node.id in
                                        list(map(lambda x: x.__name__,
                                                 builtin_datatypes))))
            if _type is not None:
                if _type:
                    partial_validators.add(node.id == _type.__name__)
                else:
                    partial_validators.add(True)
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Functions(node, _id, _in_global, _is_lambda, _is_decorator,
                       should_consider):
        # Remove class stuff
        if not should_consider:
            return False
        try:
            lambda_check = (bool(type(node) is ast.Lambda))
                            # bool((type(node) is ast.Call) and bool(node.func)))
            # function_check = bool(lambda_check or
            #                       type(node) is ast.FunctionDef)
            partial_validators = set()
            partial_validators.add(
                (type(node) in {ast.FunctionDef, ast.Lambda}) or
                (type(node) is ast.Call and bool(node.func)))
            if _id is not None:
                if type(node) is ast.Call:
                    partial_validators.add(bool(_id) and
                                           (node.func.id == _id))
                else:
                    partial_validators.add(bool(_id) and (node.name == _id))
            # if _in_global is not None:
            #     if function_check:
            #         current_node = node._parent
            #         while (type(current_node) not in {
            #                 ast.ClassDef, ast.FunctionDef, ast.Lambda}):
            #             if type(current_node) is ast.Module:
            #                 partial_validators.add(bool(_in_global))
            #                 break
            #             current_node = current_node._parent
            if _is_lambda is not None:
                partial_validators.add(bool(_is_lambda) and lambda_check)
            # if _is_decorator is not None:
            #     partial_validators.add(
            #         _is_decorator and bool(len(node.decorator_list) != 0))
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Decorators(node, _id, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
            partial_validators.add(bool(len(node.decorator_list) != 0))
            if _id is not None:
                partial_validators.add(bool(node.decorator_list[0].id == _id))
            return all(partial_validators)
        except AttributeError:
            return False

    def Kind_Classes(node, _id, _in_global, _superclass_type, should_consider):
        # if not should_consider:
        #     return False
        # try:
        #     partial_validators = set()

        #     current_node = node
        #     module_node = None
        #     while type(current_node) is not ast.Module:
        #         if type(current_node) is ast.Module:
        #             module_node = current_node
        #         else:
        #             current_node = current_node._parent

        #     all_class_names = [class_definition.name
        #                        for class_definition in ast.walk(module_node)
        #                        if type(class_definition) is ast.ClassDef]
        #     class(bool(type(node) is ast.Name) and
        #                             bool(node.id in all_class_names)) or
        #                            bool(type(node) is ast.ClassDef))
        #     partial_validators.add((bool(type(node) is ast.Name) and
        #                             bool(node.id in all_class_names)) or
        #                            bool(type(node) is ast.ClassDef))
        #     if _in_global is not None:
        #         if type(node) is ast.ClassDef:
        #             current_node = node
        #             while (type(current_node) not in {
        #                     ast.ClassDef, ast.FunctionDef, ast.Lambda}):
        #                 if type(current_node) is ast.Module:
        #                     partial_validators.add(_in_global)
        #                     break
        #                 current_node = current_node._parent
        #         elif type(node) is ast.Name
        # except AttributeError:
        #     return False
        raise NotImplementedError

    def Kind_Attributes(node, _id, _class_id, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Methods(node, _id, _class_id, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Generators(_id, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Comprehensions(_of_list, _of_dict, _of_gen, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Kind_Operations(_operation_str,
                        _is_unary, _is_binary, should_consider):
        if not should_consider:
            return False
        try:
            partial_validators = set()
        except AttributeError:
            return False
        raise NotImplementedError

    def Location_Limit_Line_Numbers(node, _minimum, _maximum):
        try:
            partial_validators = set()
            if _minimum is not None:
                partial_validators.add(bool(
                    isinstance(_minimum, (int, float, long)) and
                    (int(_minimum) <= node.lineno)))
            if _maximum is not None:
                partial_validators.add(bool(
                    isinstance(_maximum, (int, float, long)) and
                    (int(_maximum) >= node.lineno)))
            return all(partial_validators)
        except AttributeError:
            return False

    def Location_Limit_Column_Numbers(node, _minimum, _maximum):
        try:
            partial_validators = set()
            if _minimum is not None:
                partial_validators.add(bool(
                    isinstance(_minimum, (int, float, long)) and
                    (int(_minimum) <= node.col_offset)))
            if _maximum is not None:
                partial_validators.add(bool(
                    isinstance(_maximum, (int, float, long)) and
                    (int(_maximum) >= node.col_offset)))
            return all(partial_validators)
        except AttributeError:
            return False


class Grepper(object):

    def __init__(self, source_abs_path):
        assert os.path.exists(source_abs_path), "Path doesn't exist"
        with open(source_abs_path, 'r') as f:
            try:
                self.__ast = _establish_parent_link(ast.parse(f.read()))
                self.__source = f
                self.__constraints_template = _Constraints_template.copy()
                self.__result_template = namedtuple(
                    '_'.join(
                        os.path.basename(source_abs_path).split('.')[:-1]),
                    'Line Column')
            except TypeError as e:
                print(e)

    def get_source(self):
        return self.__source[:]

    def get_constraints(self):
        unfiltered_constraints = {
            constraint_type: {
                job: {
                    arg: self.__constraints_template[
                            constraint_type][job][arg]
                        for arg in self.__constraints_template[
                                constraint_type][job]
                        if (self.__constraints_template[
                                constraint_type][job][arg]is not None)
                } for job in self.__constraints_template[constraint_type]
            } for constraint_type in self.__constraints_template
        }
        constraints = {
            constraint_type: {
                job: {
                    arg: unfiltered_constraints[constraint_type][job][arg]
                    for arg in unfiltered_constraints[constraint_type][job]
                } for job in unfiltered_constraints[constraint_type]
                if len(unfiltered_constraints[constraint_type][job]) != 0
            } for constraint_type in unfiltered_constraints
        }
        return constraints

    def _validator_predicate_extracter(self):
        constraints = self.get_constraints()
        validator_predicates = {constraint_type: {
            job: _Validators.__dict__["{}_{}".format(constraint_type, job)]
            for job in constraints[constraint_type]
            } for constraint_type in constraints
        }
        validator_partial_predicates = {
            partial(validator_predicates[constraint_type][job],
                    **{
                        (lambda key: (key if key == 'should_consider'
                                      else "_{}".format(key))
                        )(key): value
                        for key, value in (
                                self.__constraints_template[
                                    constraint_type][job].items())
                    })
            for constraint_type in validator_predicates
            for job in validator_predicates[constraint_type]
        }
        return validator_partial_predicates

    def add_constraints(self, action=None, kind=None, limit=None):
        for local_variable in {'action', 'kind', 'limit'}:
            current_variable = locals()[local_variable]
            if (current_variable is not None):
                if type(current_variable) is not list:
                    current_variable = [current_variable]
                for template_modifier in current_variable:
                    template_modifier(self.__constraints_template)

    def run(self):
        validator_predicates = self._validator_predicate_extracter()
        for node in ast.walk(self.__ast):
            if all(
                    [validator_predicate(node=node)
                     for validator_predicate in validator_predicates]
            ):
                yield self.__result_template(node.lineno, node.col_offset)

    def get_all_results(self):
        return list(self.run())


if __name__ == '__main__':
    a = Grepper('/home/raf/Projects/Workspace/higher_grep/data.py')
    # a.add_constraints(Kind.Functions())
    # a.add_constraints(Kind.Functions(_is_lambda=True))
    a.add_constraints(Action.Call(should_consider=True))
    # a.add_constraints(Action.Import())
    # a.add_constraints(Action.Import(_id = 'deque'))
    # a.add_constraints(Action.Import(_from=False))
    # a.add_constraints(Action.Definition())
    # a.add_constraints(Action.Assertion())
    # a.add_constraints(Action.Looping())
    # a.add_constraints(Action.Conditional())
    # a.add_constraints(Action.Making_Global())
    # a.add_constraints(Action.Deletion())
    
    print(a.get_all_results())
