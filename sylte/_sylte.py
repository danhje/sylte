import errno
import inspect
import os
import pickle
import re
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import List, Optional, Tuple, Union, Callable
from appdirs import user_cache_dir

_DEFAULT_DIR = user_cache_dir("sylte")
CACHE_DIR = Path(os.getenv("SYLTE_CACHE_DIR", _DEFAULT_DIR)).expanduser()
DT_FMT = "%Y-%m-%d-%H-%M-%S"


def _ensure_dir_exists(path: Union[str, Path]) -> None:
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Guard against race condition. # pragma: no cover
            if exc.errno != errno.EEXIST:
                raise


def _sylte_time(name: str) -> datetime:
    dt_string = re.search(r"(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})", name).group()
    return datetime.strptime(dt_string, DT_FMT)


def _sylt(func: Callable, *args, **kwargs) -> None:
    time = datetime.now().strftime(DT_FMT)
    filename = os.path.splitext(os.path.basename(inspect.getfile(func)))[0]
    path = CACHE_DIR / f"{filename}-{func.__name__}-{time}.pickle"
    _ensure_dir_exists(CACHE_DIR)
    with open(path, "wb") as f:
        pickle.dump((args, kwargs), f)


def sylt(func: Callable) -> Callable:
    """Decorator that will sylt (cache) the arguments passed to the decorated function.

    The default location for these files is ~/.cache/sylte, but this can be overridden by
    setting the environment variable SYLTE_CACHE_DIR to a different directory.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        _sylt(func, *args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def unsylt(name: str) -> Optional[Tuple[tuple, dict]]:
    """Unsylt the arg set with the given name.

    Arguments:
        name: The name of the arg set to unsylt.

    Returns:
        A tuple of the args and kwargs of the arg set, or None if no arg set is found.

    """
    try:
        with open(CACHE_DIR / f"{name}.pickle", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


def show(substring: str = "") -> List[str]:
    """Return a list of all previously sylted arg sets, with the most recent last.

    Arguments:
        substring: Optional substring to search for.
    """
    return sorted(
        [p.stem for p in Path(CACHE_DIR).glob("*.pickle") if substring in p.stem],
        key=_sylte_time,
    )


def latest(substring: str = "") -> Optional[Tuple[tuple, dict]]:
    """Unsylt and return the most recent sylted arg set.

    Arguments:
        substring: Optional substring to search for. If multiple matches are found, the
            most recent is returned.

    Returns:
        A tuple of the args and kwargs of the arg set, or None if no arg set is found.

    """
    try:
        with open(CACHE_DIR / f"{show(substring)[-1]}.pickle", "rb") as f:
            return pickle.load(f)
    except IndexError:
        return None


def clear():
    f"""Delete all previously sylted arg sets stored in {CACHE_DIR}."""
    for path in Path(CACHE_DIR).glob("*.pickle"):
        os.remove(path)
