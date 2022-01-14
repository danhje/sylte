from datetime import datetime

from sylte import sylt
from sylte._sylte import _ensure_dir_exists, _latest, _sylte_time, _Sylted, sylted


def test_ensure_dir_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("SYLTE_CACHE_DIR", str(tmp_path))
    _ensure_dir_exists(tmp_path / "test" / "dir")
    assert (tmp_path / "test" / "dir").exists()


def test_sylte_time():
    assert _sylte_time("test_sylte-func-2022-01-14-15-16-37") == datetime(
        2022, 1, 14, 15, 16, 37
    )


def test_latest():
    sylte_names = [
        "test_sylte-func-2022-01-14-15-16-39",
        "test_sylte-func-2022-01-14-15-16-40",
    ]
    assert _latest(*sylte_names) == "test_sylte-func-2022-01-14-15-16-40"
    assert _latest(*reversed(sylte_names)) == "test_sylte-func-2022-01-14-15-16-40"


def test_sylted_init(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    sylted = _Sylted()
    assert "test_sylte-func-2022-01-14-15-16-00" in sylted.__dict__
    assert "test_sylte-func-2022-01-14-15-16-01" in sylted.__dict__


def test_sylted_call(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        "pickle.load",
        lambda x: "success"
        if "test_sylte-func-2022-01-14-15-16-00" in str(x)
        else "fail",
    )
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    sylted = _Sylted()
    assert sylted("test_sylte-func-2022-01-14-15-16-00") == "success"


def test_sylted_list(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    sylted = _Sylted()
    assert sylted.list() == [
        "test_sylte-func-2022-01-14-15-16-00",
        "test_sylte-func-2022-01-14-15-16-01",
    ]


def test_sylted_latest(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        "pickle.load",
        lambda x: "success"
        if "test_sylte-func-2022-01-14-15-16-01" in str(x)
        else "fail",
    )
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    sylted = _Sylted()
    assert sylted("test_sylte-func-2022-01-14-15-16-01") == "success"


def test_sylted_clear(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        "pickle.load",
        lambda x: "success"
        if "test_sylte-func-2022-01-14-15-16-01" in str(x)
        else "fail",
    )
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    sylted = _Sylted()
    sylted.clear()
    assert sylted.list() == []
    assert list(tmp_path.iterdir()) == []


def test_sylt_decorated_function_works(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)

    @sylt
    def add(a, b):
        return a + b

    assert add(3, 7) == 10


def test_sylt_unsylts_to_args(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)

    @sylt
    def func(a, b, c):
        pass

    func(1, [2], c={3: ...})

    assert sylted.latest() == ((1, [2]), {"c": {3: ...}})
