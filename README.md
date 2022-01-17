# sylte

![Testing and linting](https://github.com/danhje/sylte/workflows/Test%20And%20Lint/badge.svg)
[![codecov](https://codecov.io/gh/danhje/sylte/branch/master/graph/badge.svg)](https://codecov.io/gh/danhje/sylte)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/danhje/sylte?include_prereleases)
![PyPI](https://img.shields.io/pypi/v/sylte)

Sylte provides a decorator that stores function arguments as a pickle file in a central location,
and functions for retrieving those arguments later on, so that the function can be re-invoked
with the same args. Useful when writing or debugging a function that exists somewhere near the end
of a long-running pipeline.

## Installation

Using poetry:

```shell
poetry add sylte
```

Using pipenv:

```shell
pipenv install sylte
```

Using pip:

```shell
pip install sylte
```

## Usage

Let's say we have a function `transform` that we want to debug or modify. We will have to call it
several times to see how it behaves with real data. It's normally called as part of a long-running
pipeline, and we don't want to have to wait for this pipeline every time. We could write a unit-test,
but perhaps we aren't yet sure how the output will look, and perhaps the input-data is complex
and time-consuming to recreate in a test, and we'd prefer to do that when the function is finalized,
to avoid having to repeatedly modify the test as the function is modified.

Enter sylte. By applying the `@sylt` decorator to the function and running the pipeline once,
the args are recorded, and can be retrieved later.

```python
from sylte import sylt

@sylt
def transform(this_huge_df, this_other_huge_df, this_object_with_lots_of_attributes):
    ...
```

The arg set will be stored in a pickle file in the default cache location for the os.
The location can be seen by running `from sylte import CACHE_DIR; print(CACHE_DIR)`.
To use a different location than the default, specify the location with the environment variable `SYLTE_CACHE_DIR`.

The file name will have the format
`<file name>-<function name>-<timestamp>.pickle`.

The function `latest` will retrieve an unsylt the latest arg set, returning a tuple with args and kwargs.

```python
>>> from sylte import latest
...
>>> args, kwargs = latest()
>>> transform(*args, **kwargs)
```

`show` returns a list of all sylted arg sets:

```python
>>> from sylte import show
...
>>> show()
['demo-transform-2022-01-14-15-08-59',
 'demo-transform-2022-01-14-15-12-33',]
```

`unsylt` unsylts and returns the arg set with the specified name as output by `show`, i.e. the filename with the extension omitted:

```python
>>> from sylte import unsylt
...
>>> args, kwargs = unsylt('demo-add-2022-01-14-15-08-59')
>>> transform(*args, **kwargs)
```

`clear` deletes all previously sylted arg sets:

```python
>>> from sylte import clear, show
...
>>> clear()
>>> show()
[]
```
