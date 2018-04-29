import doctest
import cytoolz


def test_doctests():
    cytoolz.__test__ = {}
    for name, func in vars(cytoolz).items():
        if isinstance(func, cytoolz.curry):
            cytoolz.__test__[name] = func.func
    assert doctest.testmod(cytoolz).failed == 0
    del cytoolz.__test__
