"""Functions relating to zipping or unzipping iterables.

"""
import itertools
import operator

from typing import (
    Any,
    Iterator,
    Iterable,
    Optional,
    Tuple,
)

import litecore.irecipes.common as _common

from litecore.sentinels import NO_VALUE as _NO_VALUE


def zip_strict(*iterables) -> Iterator[Tuple[Any, ...]]:
    """Same as built-in zip, but requires all iterables to be same length.

    Arguments:
        arbitrary number of iterable positional arguments

    Yields:
        iterator of zipped tuples of the arguments

    Raises:
        ValueError: if the iterables are not equal-length

    Credit to:
        https://treyhunner.com/2019/03/unique-and-sentinel-values-in-python/

    Examples:

    >>> list(zip_strict('abcd', range(4)))
    [('a', 0), ('b', 1), ('c', 2), ('d', 3)]
    >>> list(zip_strict('abcd', range(5)))
    Traceback (most recent call last):
     ...
    ValueError: all iterables must have the same length
    >>> list(zip_strict('', []))
    []

    """
    for values in itertools.zip_longest(*iterables, fillvalue=_NO_VALUE):
        if any(value is _NO_VALUE for value in values):
            msg = f'all iterables must have the same length'
            raise ValueError(msg)
        yield values


def unzip(iterable: Iterable[Tuple[Any, ...]]) -> Tuple[Iterator[Any], ...]:
    """Inverse of built-in zip(), returns iterators of each tuple item.

    Returns tuple of iterators based upon an iterable, each item of which
    is assumed to be a tuple of the same number of items (i.e., of the
    sort created by zip() built-in).

    Assumes that all items of the iterable are a tuple with same length
    as the initial item.

    The iterable can be infinite (i.e., a zip() of infinite iterators).
    In that case, each returned iterator will also be infinite.

    Uses itertools.tee(), see the standard library docs for cautions:
        https://docs.python.org/3/library/itertools.html#itertools.tee

    In particular, this may require significant auxiliary storage and/or
    suffer from reduced performance in certain cases. For finite
    iterables, see the unzip_finite() and unzip_longest_finite()
    functions for simpler and faster alternatives.

    Arguments:
        iterable: iterator or collection of tuples to be unzipped

    Returns:
        tuple of iterators, each item corresponding to an item of the
            original zipped iterable

    >>> letters, numbers = unzip(zip('abcd', range(8)))
    >>> tuple(letters)
    ('a', 'b', 'c', 'd')
    >>> tuple(numbers)
    (0, 1, 2, 3)
    >>> import itertools
    >>> inf_letters = itertools.cycle('abcd')
    >>> inf_numbers = itertools.count()
    >>> letters, numbers = unzip(zip(inf_letters, inf_numbers))
    >>> from litecore.irecipes.common import take
    >>> take(6, letters)
    ['a', 'b', 'c', 'd', 'a', 'b']
    >>> take(8, numbers)
    [0, 1, 2, 3, 4, 5, 6, 7]
    >>> list(unzip(zip('abcd', [])))
    []
    >>> new_letters, new_numbers = unzip(zip('abcd', range(3)))
    >>> list(new_letters)
    ['a', 'b', 'c']
    >>> list(new_numbers)
    [0, 1, 2]

    """
    first, iterator = _common.peek(iter(iterable))
    if first is None:
        return ()
    tees = itertools.tee(iterator, len(first))
    return (map(operator.itemgetter(i), tee) for i, tee in enumerate(tees))


def unzip_finite(
        iterable: Iterable[Tuple[Any, ...]],
) -> Tuple[Iterator[Any], ...]:
    """Similar to unzip(), but limited to finite iterables.

    This function does not distinguish sentinel values of the sort used
    by itertools.zip_longest(). Such sentinels will be included in the
    returned item iterators. See unzip_longest_finite() in this module
    to efficiently unzip an iterable created using itertools.zip_longest().

    Arguments:
        iterable: iterator or collection of tuples to be unzipped

    Returns:
        tuple of iterators, each item corresponding to an item of the
            original zipped iterable

    >>> letters, numbers = unzip_finite(zip('abcd', range(8)))
    >>> letters
    ('a', 'b', 'c', 'd')
    >>> numbers
    (0, 1, 2, 3)
    >>> list(unzip_finite(zip('abcd', [])))
    []
    >>> new_letters, new_numbers = unzip(zip('abcd', range(3)))
    >>> list(new_letters)
    ['a', 'b', 'c']
    >>> list(new_numbers)
    [0, 1, 2]

    """
    for zipped in zip(*iterable):
        yield zipped


def unzip_longest_finite(
        iterable: Iterable[Tuple[Any, ...]],
        *,
        fillvalue: Optional[Any] = None,
) -> Tuple[Iterator[Any], ...]:
    """Similar to unzip(), but limited to finite iterables.

    This function distinguishes sentinel values of the sort used by
    itertools.zip_longest(). Such sentinels will be stripped from the
    returned item iterators. Use unzip_finite() in this module to
    efficiently unzip iterables created using built-in zip().

    Arguments:
        iterable: iterator or collection of tuples to be unzipped

    Keyword Arguments:
        fillvalue: sentinel value (similar to itertools.zip_longest())
            to be stripped from the returned item iterators

    Returns:
        tuple of iterators, each item corresponding to an item of the
            original zipped iterable

    >>> import itertools
    >>> zipped = itertools.zip_longest('abcd', range(6), fillvalue=-1)
    >>> letters, numbers = unzip_longest_finite(zipped, fillvalue=-1)
    >>> letters
    ('a', 'b', 'c', 'd')
    >>> numbers
    (0, 1, 2, 3, 4, 5)
    >>> list(unzip_longest_finite(zip('abcd', [0])))
    [('a',), (0,)]

    """
    for zipped in zip(*iterable):
        yield tuple(item for item in zipped if item != fillvalue)
