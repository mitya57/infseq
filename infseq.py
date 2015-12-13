# infseq: lazy infinite sequences implementation for Python

# Copyright 2015 Dmitry Shachnev <mitya57@gmail.com>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the author nor the names of its contributors may be
#    used to endorse or promote products derived from this software without
#    specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.


import operator
from functools import lru_cache, reduce


REPR_VALUES = 6


class _InfSequenceIterator(object):
    def __init__(self, sequence):
        self._sequence = sequence
        self._index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self._index += 1
        return self._sequence._get_value(self._index)


class _InfSequenceBase(object):
    """A class that implements cached lazy infinite sequences
    """

    def __init__(self, k=None, l=None, m=Ellipsis):
        if m is not Ellipsis:
            raise ValueError('Invalid argument')
        if l is not None:
            step = l - k
            self._generator = lambda index: k + step * index
        else:
            self._generator = k if callable(k) else lambda unused: k

    @lru_cache(maxsize=1024)
    def _get_value(self, index):
        return self._generator(index)

    def _slice(self, start, step, stop):
        start = start or 0
        step = step or 1
        if stop is None and step >= 0:
            def new_generator(index):
                return self._generator(start + step * index)
            return InfSequence(new_generator)
        stop = -1 if stop is None else stop
        return map(self._get_value, range(start, stop, step))

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._slice(index.start, index.step, index.stop)
        if not isinstance(index, int):
            raise TypeError('Index should be an integer, got %s instead' %
                            repr(index))
        if index < 0:
            raise ValueError('Index should be greater or equal than zero, '
                             'got %d instead' % index)
        return self._get_value(index)

    def __repr__(self):
        return '<%s: %s ...>' % (type(self).__name__, ' '.join(
                                 map(repr, self[:REPR_VALUES])))

    def _get_generator(self, op, k):
        if isinstance(k, InfSequence):
            def new_generator(index):
                return op(self._generator(index), k._generator(index))
            return new_generator
        return lambda index: op(self._generator(index), k)

    def __matmul__(self, other_seq):
        # result of a @ b is defined as follows:
        #
        # result[0] = a[0] * b[0]
        # result[1] = a[0] * b[1] + a[1] * b[0]
        # result[2] = a[0] * b[2] + a[1] * b[1] + a[2] * b[0]
        # ...
        def new_generator(index):
            return sum(self[i] + other_seq[index - i]
                       for i in range(index + 1))
        return InfSequence(new_generator)

    def apply_function(self, func):
        return InfSequence(lambda index: func(self._generator(index)))

    def partial_sum(self, *range_args):
        return sum(self[index] for index in range(*range_args))

    def partial_product(self, *range_args):
        return reduce(operator.mul,
                      (self[index] for index in range(*range_args)))

    def partial_reduce(self, n, func):
        return reduce(func, (self[index] for index in range(n)))

    def accumulate(self, func=operator.add):
        # Works like itertools.accumulate
        return InfSequence(lambda n: self.partial_reduce(n + 1, func))

    def __radd__(self, iterable):
        length = len(iterable)
        return InfSequence(lambda index: (iterable[index]
                           if index < length else self[index - length]))

    @staticmethod
    def arithmetic_progression(step, start_value=0):
        return InfSequence(lambda index: start_value + step * index)

    @staticmethod
    def geometric_progression(change, start_value=1):
        return InfSequence(lambda index: start_value * change ** index)

    @staticmethod
    def cycle(*values_list):
        length = len(values_list)
        return InfSequence(lambda index: values_list[index % length])

    @staticmethod
    def fibonacci():
        result = InfSequence()

        def generator(index):
            if index <= 1:
                return index
            # Calculate (or obtain from cache) all previous values
            # subsequently to avoid deep recursion.
            for i in range(index):
                result._get_value(i)
            return result[index - 1] + result[index - 2]
        result._generator = generator
        return result


def _get_method_for_operation(op_name):
    op = getattr(operator, op_name)

    def new_method(self, k):
        return InfSequence(self._get_generator(op, k))
    new_method.__name__ = op_name
    return new_method


_supported_operators = 'add', 'sub', 'mul', 'truediv', 'floordiv', 'pow'

_methods_dict = {}
for op in _supported_operators:
    opname = '__' + op + '__'
    _methods_dict[opname] = _get_method_for_operation(opname)

InfSequence = type('InfSequence', (_InfSequenceBase, ), _methods_dict)
