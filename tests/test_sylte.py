import pickle
from datetime import datetime

from sylte import sylt, unsylt, show, clear, latest
from sylte._sylte import _ensure_dir_exists, _sylte_time


def test_ensure_dir_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("SYLTE_CACHE_DIR", str(tmp_path))
    _ensure_dir_exists(tmp_path / "test" / "dir")
    assert (tmp_path / "test" / "dir").exists()


def test_sylte_time():
    assert _sylte_time("test_sylte-func-2022-01-14-15-16-37") == datetime(
        2022, 1, 14, 15, 16, 37
    )


def test_show(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    assert show() == [
        "test_sylte-func-2022-01-14-15-16-00",
        "test_sylte-func-2022-01-14-15-16-01",
    ]


def test_show_with_substring(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-other_func-2022-01-14-15-16-01.pickle", "a").close()

    assert show("other") == [
        "test_sylte-other_func-2022-01-14-15-16-01",
    ]


def test_latest(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        "pickle.load",
        lambda x: "success"
        if "test_sylte-func-2022-01-14-15-16-01" in str(x)
        else "fail",
    )
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    assert latest("test_sylte-func-2022-01-14-15-16-01") == "success"


def test_clear(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    clear()
    assert list(tmp_path.iterdir()) == []


def test_sylt_decorated_function_works(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)

    @sylt
    def add(a, b):
        return a + b

    assert add(3, 7) == 10


def test_unsylt(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    argset = (1, 2.0), {3: ...}
    with open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "wb") as f:
        pickle.dump(argset, f)

    assert unsylt("test_sylte-func-2022-01-14-15-16-00") == argset


def test_latest_reverses_sylt(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)

    @sylt
    def func(a, b, c):
        pass

    func(1, [2], c={3: ...})

    assert latest() == ((1, [2]), {"c": {3: ...}})
