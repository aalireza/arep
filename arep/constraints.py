class ConstraintForm(type):
    """
    It acts as a template for all of the constraints. It receives a dictionary
    (may be nested) and makes an object that is a chain of connected classes,
    each with their own attributes and methods (where those attributes are the
    dictionary keys). The attributes and methods for each class is saved in
    `specs` dictionary.

    All capitalized names are those who have further specifications and all
    lower case names are properties of those classes. Capitalized names can't
    be assigned by a user while the lower case ones can.

    Assignment of a specification to `None` indicates indifference. Otherwise,
    it'll be considered in evaluation.

    In case of name collision for small case names, a trailing underline is
    used e.g. Action.Trying.Except.as_

    If the class has `consideration` specification, then assigning it to False
    would automatically ignore subclass specifications unless stated otherwise.


    Attributes
    ----------
    __name__ : str
        Works the same way as `quote` in Lisp.
    _class_vars : {str: any}
        Address of all of the attributes and methods of the class.
    _methods: {str: functions}

    Methods
    _______
    view_actives()
        View only the specs whose values have been changed.
    __itername__()
        Works the same is __iter__ except it iterates of __name__
    reset(replace_with)
    """

    def __new__(cls, name, parents, specs):

        non_representables = {
            *{
                '__repr__', '__delattr__', '__setattr__', '__dict__',
                '__name__', '__iter__', '__str__', '__getitem__',
            },
            '__itername__', 'view_actives', 'reset', '_class_vars', '_methods',
        }

        def set_attr_decorated(cls, name, value):
            if name == '_'.join([x.capitalize() for x in name.split('_')]):
                raise TypeError("Can't set a value for a constraint type")

            if not hasattr(cls, name):
                raise KeyError(
                    "Can't set an attribute that wasn't in the template"
                )

            if name != "consideration":
                object.__setattr__(cls, "consideration", True)

            object.__setattr__(cls, name, value)

        def del_attr_decorated(cls, name):
            raise Exception("Can't delete any part of the template")

        def get_item_decorated(cls, key):
            if key not in non_representables:
                return getattr(cls, key)
            raise KeyError(
                "{} doesn't have the requested specification".format(
                    cls.__name__
                )
            )

        def view_actives(cls):
            results = dict()
            for key_name, key in zip(cls.__itername__(), cls):
                if key_name in cls._class_vars:
                    if key is not None:
                        results[key_name] = key
                elif key_name in cls._methods:
                    key_if_active = view_actives(key)
                    if key_if_active:
                        results[key_name] = key_if_active
            return results

        def reset(cls, replace_with=None):
            for attr in cls.__itername__():
                if attr not in non_representables:
                    if type(getattr(cls, attr)).__name__ == constraint_type:
                        reset(getattr(cls, attr), replace_with)
                    else:
                        setattr(cls, attr, replace_with)

        def wrapped(name, specs, with_consideration, constraint_type):
            if type(specs) is not dict:
                return specs

            if any([type(specs[key]) is dict for key in specs]):
                for key in specs:
                    try:
                        specs[key] = wrapped(
                            key, specs[key], with_consideration,
                            constraint_type
                        )
                    except AttributeError:
                        print(key)

            specs['__name__'] = name

            if with_consideration:
                specs['consideration'] = None

            specs['__setattr__'] = set_attr_decorated

            specs['__delattr__'] = del_attr_decorated

            specs['__getitem__'] = get_item_decorated

            specs['__iter__'] = (
                lambda cls: (
                    getattr(cls, key)
                    for key in cls.__itername__()
                    if key not in non_representables
                )
            )

            specs['__itername__'] = (
                lambda cls: (
                    key
                    for key in specs
                    if key not in non_representables
                )
            )

            specs['__repr__'] = (
                lambda cls: (
                    {
                        str(key): getattr(cls, str(key))
                        for key in cls.__itername__()
                        if key not in non_representables
                    }.__repr__()
                ).replace("'", "")
            )

            specs['__str__'] = (lambda cls: cls.__name__)

            specs['reset'] = (
                lambda cls, resetting_value=None: reset(cls, resetting_value)
            )

            specs['view_actives'] = (
                lambda cls: view_actives(cls)
            )

            specs['_class_vars'] = {
                key: value
                for key, value in specs.items()
                if (key == key.lower()) and (key not in non_representables)
            }

            specs['_methods'] = {
                key: value
                for key, value in specs.items()
                if ((key not in specs['_class_vars']) and
                    (key not in non_representables))
            }

            return type(constraint_type, (object,), specs)()

        specs['__name__'] = name
        constraint_type = name
        # Currently, all constraint types would have the consideration toggle.
        with_consideration = True

        return wrapped(name, specs, with_consideration, constraint_type)


def _Action_Template():
    return {
        'Import': {
            'name': None,
            'From': {
                'name': None,
            },
            'As': {
                'name': None,
            }
        },
        'Assignment': {
            'Operational_Augmentation': {
                'operation_symbol': None
            }
        },
        'Unpacking': {
            'one_dimensional': None,
            'two_dimensional': None,
        },
        'Assertion': {
            'Error': {
                'content': None
            }
        },
        'Looping': {spec: None for spec in {
            'for_', 'while_', 'for_else', 'with_break',
            'with_simple_non_terminating_test'
        }},
        'Conditional': {spec: None for spec in {
            'elif_', 'else_', 'ifexp'
        }},
        'With': {
            'As': {
                'name': None
            }
        },
        'Trying': {
            'Except': {
                'type_': None,
                'as_': None
            },
            'finally_': None,
        },
        'Raising': {
            'Error': {
                'type_': None,
                'message': None
            },
            'Cause': {
                'name': None
            },
        },
        'Yielding': {
            'from_': None,
            'in_expression': None,
        },
        **{
            spec: {'name': None}
            for spec in {'Making_Global', 'Making_Nonlocal'}
        },
        **{spec: dict()
           for spec in {
                   'Call', 'Instantiation', 'Definition', 'Deletion',
                   'Indexing', 'Passing', 'Returning', 'Breaking', 'Continuing'
           }
        }
    }


class Action(object):
    """
    Uses the ConstraintForm to create a series of nested classes representing
    all of the constraints in `Action` category.
    """
    def __new__(self):
        return ConstraintForm("Action", (object,), _Action_Template())


def _Kind_Template():
    return {
        'Variables': {
            spec: None
            for spec in {
                    'name', 'is_attribute', 'is_argument'
            }
        },
        'STD_Types': {
            'type_': None
        },
        'Functions': {
            'name': None,
            'is_builtin': None,
            'Lambda': {
                'immediately_called': None,
            },
            'Decorators': {
                'name': None
            },
            'Parameters': {
                'Arguments': {
                    'is_variadic': None,
                },
                'Keywords': {
                    'is_variadic': None,
                },
                'with_default_values': None,
            },
        },
        'Classes': {
            'name': None,
        },
        'Comprehensions': {
            spec: None for spec in {
                'of_list', 'of_set', 'of_dict', 'of_gen'
            }
        },
        'Operations': {
            'symbol': None,
            'augments_an_assignment': None,
            'is_boolean': None,
            'is_comparative': None,
            'is_unary': None,
            'is_binary': None,
        }
    }


class Kind(object):
    """
    Uses the ConstraintForm to create a series of nested classes representing
    all of the constraints in `Kind` category.
    """
    def __new__(self):
        return ConstraintForm("Kind", (object,), _Kind_Template())


def _Properties_Template():
    return {
        'Positional': {
            'Line_Numbers': {
                'minimum': None,
                'maximum': None,
            },
            'Column_Numbers': {
                'minimum': None,
                'maximum': None,
            },
        },
    }



class Properties(object):
    """
    Uses the ConstraintForm to create a series of nested classes representing
    all of the constraints in `Kind` category.
    """
    def __new__(self):
        return ConstraintForm("Properties", (object,), _Properties_Template())
