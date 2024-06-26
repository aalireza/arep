arep
====

Warnings
-------
1. This code was written 7 years ago when the author knew next to nothing about
programming language theory, compilers, etc. The author still knows next to
nothing about those things but he does recommend using SemGrep and maybe ChatGPT.

2. The project is unmaintained. Python's AST has probably changed a bit since 7
years ago.


Description
-----------
`arep` is searching tool that enables one to scan a Python program and find
syntactical and/or semantical patterns within it.

Instead of a string-based method querying, a user declaratively describes the
search parameter in one or more constraint objects, then the search engine would
return all of the nodes of the programs AST that satisfy those constraints.

This way, results that are extremeley-difficult/nearly-impossible to be searched
via string or regex based methods, are trivially found e.g. searching for all
of the functions (be it function definitions or function calls or lambda
functions that are assigned to a variable).


All of the constraints have a `consideration` specification where by default
is set to `None`, which means the search engine is indifferent to them. However
if changes its value to `True`/`False` then the search engine would seek/avoid
all of the results that match the constraint. This method enables one build up
on the predefined constraints and search of arbitrary complex patterns within
the code.


License
-------
This project is licensed under the BSD license (3-clause) - see the `LICENSE <https://github.com/aalireza/arep/blob/master/LICENSE>`_
file for more details.
