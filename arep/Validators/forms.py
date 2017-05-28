from inspect import getfullargspec as spec


def ValidatorForm(cls, **kwargs):
    """
    The basic structure of all the validators.
    """
    def func_call_from_kwargs(f, keyword_dict):
        return f(**{
            key: (keyword_dict[key] if key in keyword_dict else None)
            for key in spec(f).args
        })

    try:
        validators = set([func_call_from_kwargs(cls.basic, kwargs)])
        for kwarg in kwargs:
            if kwarg not in {
                    'node', 'consideration', 'knowledge'
            }:
                validators.add(func_call_from_kwargs(
                    getattr(cls, kwarg), kwargs
                ))
        return all(validators)
    except AttributeError:
        return ValidationForm(
            (kwargs['consideration'] if 'consideration' in kwargs else None),
            condition=False
        )


def ValidationForm(consideration, condition, consideration_types={}):
    """
    The basic structure of all the validator methods.
    """
    if consideration is None:
        return True
    elif (
            consideration and
            (bool(type(consideration) in consideration_types)
             if consideration_types else True)
    ):
        return condition
    return not condition


def PositionalBasicForm(consideration, minimum, maximum):
    """
    The basic structure of all the positional validations. It's mainly to
    check whether the provided limits are consistent or not.
    """
    def _range_checker(minimum, maximum):
        return (
            True
            if not (type(minimum) is type(maximum) is int)
            else bool(minimum <= maximum)
        )

    return ValidationForm(
        consideration,
        condition=bool(_range_checker(minimum, maximum))
    )
