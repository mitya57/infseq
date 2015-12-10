The ``infseq`` module implements cached lazy infinite sequences for Python 3.

Here, the word “lazy” means that values of the sequence will never be calculated
unless they are really used, and the word “cached” means that every value will
be calculated no more than once.

Sequences can contain items of any type — such as numbers, strings or even
other sequences.

Using this module is pretty straightforward — everything just works. Here are
some usage examples:

Creating sequences
------------------

.. code:: python

  >>> from infseq import InfSequence
  >>> InfSequence(5)
  <InfSequence: 5 5 5 5 5 5 ...>
  >>> InfSequence(5, 6, ...)
  <InfSequence: 5 6 7 8 9 10 ...>
  >>> InfSequence.geometric_progression(3)
  <InfSequence: 1 3 9 27 81 243 ...>
  >>> InfSequence.cycle('a', 'b', 'c')
  <InfSequence: 'a' 'b' 'c' 'a' 'b' 'c' ...>
  >>> InfSequence.fibonacci()
  <InfSequence: 0 1 1 2 3 5 ...>

.. note::
   For the ease of debugging the first six values are calculated when
   ``repr()`` is called on the sequence. If you just create the sequence
   without printing it, the values are not calculated. The number of items can
   be adjusted by modifying the ``infseq.REPR_VALUES`` number (it is set to
   6 by default).

Retrieving the values
---------------------

.. code:: python

  >>> a = InfSequence.geometric_progression(2)
  >>> a
  <InfSequence: 1 2 4 8 16 32 ...>
  >>> a[10]
  1024
  >>> a.partial_sum(10)  # a[0] + ... + a[9]
  1023
  >>> a.partial_sum(4, 10)  # sum(a[i] for i in range(4, 10))
  1008
  >>> a.partial_product(5)  # a[0] * ... * a[4]
  1024

Slicing and prepending elements
-------------------------------

.. code:: python

  >>> a[5:]
  <InfSequence: 32 64 128 256 512 1024 ...>
  >>> a[::2]
  <InfSequence: 1 4 16 64 256 1024 ...>
  >>> list(a[5:10])  # a[5:10] returns a map object, because of laziness
  [32, 64, 128, 256, 512]
  >>> (5, 7) + a
  <InfSequence: 5 7 1 2 4 8 ...>

Arithmetic operations
---------------------

.. code:: python

  >>> b = InfSequence(1, 2, ...)
  >>> b
  <InfSequence: 1 2 3 4 5 6 ...>
  >>> b * 2
  <InfSequence: 2 4 6 8 10 12 ...>
  >>> b ** 2
  <InfSequence: 1 4 9 16 25 36 ...>
  >>> a + b
  <InfSequence: 2 4 7 12 21 38 ...>
  >>> b.accumulate()  # a[0],  a[0] + a[1],  a[0] + a[1] + a[2], ...
  <InfSequence: 1 3 6 10 15 21 ...>

Applying any functions
----------------------

.. code:: python

  >>> c = InfSequence.geometric_progression(9)
  >>> c
  <InfSequence: 1 9 81 729 6561 59049 ...>
  >>> import math
  >>> c.apply_function(math.sqrt)
  <InfSequence: 1.0 3.0 9.0 27.0 81.0 243.0 ...>

Using the matrix multiplication operator
----------------------------------------

If you are using Python 3.5+, you can use the new “matrix multiplication”
operator that was introduced in that version.

The expression ``a @ b`` will produce the following result::

  result[0] = a[0] * b[0]
  result[1] = a[0] * b[1] + a[1] * b[0]
  result[2] = a[0] * b[2] + a[1] * b[1] + a[2] * b[0]
  ...

Example:

.. code:: python

  >>> InfSequence(0, 2, ...) @ InfSequence(1)
  <InfSequence: 1 4 9 16 25 36 ...>

Installing the module and running the tests
-------------------------------------------

The module is available on PyPI_. To install the module, simply use::

  pip3 install infseq

The source code is hosted on GitHub_.

To run the doctests in this module, use::

  python3 -m doctest ./README.rst

.. _PyPI: https://pypi.python.org/pypi/infseq
.. _GitHub: https://github.com/mitya57/infseq
