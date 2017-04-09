from higher_grep.core import Result


def results_formatter(coordinates, name):
    results = set([])
    for result in coordinates:
        if type(result) is Result:
            results.add(result)
        else:
            results.add(Result(
                # Removing `test_` from `test_something.py`
                '_'.join(name.split('_')[1:]), result[0], result[1]
            ))
    return results
