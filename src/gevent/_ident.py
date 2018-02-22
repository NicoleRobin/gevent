# -*- coding: utf-8 -*-
# Copyright 2018 gevent contributors. See LICENSE for details.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from weakref import WeakKeyDictionary
from weakref import ref

from heapq import heappop
from heapq import heappush

__all__ = [
    'IdentRegistry',
]

class ValuedWeakRef(ref):
    """
    A weak ref with an associated value.
    """
    __slots__ = ('value',)


class IdentRegistry(object):
    """
    Maintains a unique mapping of (small) positive integer identifiers
    to objects that can be weakly referenced.

    It is guaranteed that no two objects will have the the same
    identifier at the same time, as long as those objects are
    also uniquely hashable.
    """

    def __init__(self):
        # {obj -> (ident, wref(obj))}
        self._registry = WeakKeyDictionary()

        # A heap of numbers that have been used and returned
        self._available_idents = []

    def get_ident(self, obj):
        """
        Retrieve the identifier for *obj*, creating one
        if necessary.
        """

        try:
            return self._registry[obj][0]
        except KeyError:
            pass

        if self._available_idents:
            # Take the smallest free number
            ident = heappop(self._available_idents)
        else:
            # Allocate a bigger one
            ident = len(self._registry)

        vref = ValuedWeakRef(obj, self._return_ident)
        vref.value = ident # pylint:disable=assigning-non-slot,attribute-defined-outside-init
        self._registry[obj] = (ident, vref)
        return ident

    def _return_ident(self, vref):
        # By the time this is called, self._registry has been
        # updated
        heappush(self._available_idents, vref.value)

    def __len__(self):
        return len(self._registry)
