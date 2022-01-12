from sylte import sylt


def test_sylt_function_unmodified():
    @sylt
    def add(a, b):
        return a + b

    assert add(3, 7) == 10
