from datetime import datetime

from sylte import sylt
from sylte._sylte import _ensure_dir_exists, _latest, _sylte_time, _Sylted


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
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-00.pickle", "a").close()
    open(tmp_path / "test_sylte-func-2022-01-14-15-16-01.pickle", "a").close()

    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)
    sylted = _Sylted()
    assert "test_sylte-func-2022-01-14-15-16-00" in sylted.__dict__
    assert "test_sylte-func-2022-01-14-15-16-01" in sylted.__dict__


def test_sylt_decorated_function_works(tmp_path, monkeypatch):
    monkeypatch.setattr("sylte._sylte.CACHE_DIR", tmp_path)

    @sylt
    def add(a, b):
        return a + b

    assert add(3, 7) == 10
