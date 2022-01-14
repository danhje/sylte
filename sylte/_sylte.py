import errno
import inspect
import os
import pickle
import re
from datetime import datetime
from functools import wraps
from pathlib import Path
from types import SimpleNamespace
from typing import List, Optional, Tuple, Union

CACHE_DIR = Path(os.getenv("SYLTE_CACHE_DIR", "~/.cache/sylte")).expanduser()
DT_FMT = "%Y-%m-%d-%H-%M-%S"


def _ensure_dir_exists(path: Union[str, Path]):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def _sylte_time(name: str) -> datetime:
    dt_string = re.search(r"(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})", name).group()
    return datetime.strptime(dt_string, DT_FMT)


def _latest(a: str, b: str) -> str:
    dt_a, dt_b = _sylte_time(a), _sylte_time(b)
    return a if dt_a > dt_b else b


class _Sylted(SimpleNamespace):
    def __init__(self, **kwargs):
        kwargs.update({k.stem: ... for k in Path(CACHE_DIR).glob("*.pickle")})
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> Tuple[tuple, dict]:
        value = super().__getattribute__(name)
        if value == Ellipsis:
            with open(CACHE_DIR / f"{name}.pickle", "rb") as f:
                return pickle.load(f)
        return value

    def __call__(self, name: str) -> Tuple[tuple, dict]:
        return self.__getattribute__(name)

    @staticmethod
    def list() -> List[str]:
        """Return a list of all previously sylted arg sets, with the most recent last."""
        return sorted(
            [p.stem for p in Path(CACHE_DIR).glob("*.pickle")], key=_sylte_time
        )

    def latest(self, substring: str = "") -> Optional[Tuple[tuple, dict]]:
        """Unsylt and return the most recent sylted arg set that contains the substring."""
        _matches = [s for s in self.list() if substring in s]
        if _matches:
            latest = _matches[-1]
            with open(CACHE_DIR / f"{latest}.pickle", "rb") as f:
                return pickle.load(f)
        return None

    def clear(self):
        f"""Delete all previously sylted arg sets, stored in {CACHE_DIR}."""
        for path in Path(CACHE_DIR).glob("*.pickle"):
            os.remove(path)
        [delattr(self, attr) for attr in self.list()]


sylted = _Sylted()


def _sylt(func, *args, **kwargs):
    time = datetime.now().strftime(DT_FMT)
    filename = os.path.splitext(os.path.basename(inspect.stack()[2].filename))[0]
    path = CACHE_DIR / f"{filename}-{func.__name__}-{time}.pickle"
    _ensure_dir_exists(CACHE_DIR)
    with open(path, "wb") as f:
        pickle.dump((args, kwargs), f)
    setattr(sylted, path.stem, ...)


def sylt(func):
    """Decorator that will sylt (cache) the arguments passed to the decorated function.

    The default location for these files is ~/.cache/sylte, but this can be overridden by
    setting the environment variable SYLTE_CACHE_DIR to a different directory.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        _sylt(func, *args, **kwargs)
        return func(*args, **kwargs)

    return wrapper
