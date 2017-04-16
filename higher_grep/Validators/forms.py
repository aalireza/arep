from inspect import getfullargspec as spec


def ValidatorForm(cls, **kwargs):
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


def ValidationForm(consideration, condition):
    if consideration is None:
        return True
    elif consideration:
        return condition
    return not condition
