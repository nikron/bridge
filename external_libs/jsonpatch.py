# -*- coding: utf-8 -*-
#
# python-json-patch - An implementation of the JSON Patch format
# https://github.com/stefankoegl/python-json-patch
#
# Copyright (c) 2011 Stefan Kögl <stefan@skoegl.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

""" Apply JSON-Patches (RFC 6902) """

from __future__ import unicode_literals

import collections
import copy
import functools
import inspect
import json
import sys

from external_libs.jsonpointer import JsonPointer, JsonPointerException

# Will be parsed by setup.py to determine package metadata
__author__ = 'Stefan Kögl <stefan@skoegl.net>'
__version__ = '1.3'
__website__ = 'https://github.com/stefankoegl/python-json-patch'
__license__ = 'Modified BSD License'


# pylint: disable=E0611,W0404
if sys.version_info >= (3, 0):
    basestring = (bytes, str)  # pylint: disable=C0103,W0622
    from itertools import zip_longest
else:
    from itertools import izip_longest as zip_longest


class JsonPatchException(Exception):
    """Base Json Patch exception"""


class JsonPatchConflict(JsonPatchException):
    """Raised if patch could not be applied due to conflict situation such as:
    - attempt to add object key then it already exists;
    - attempt to operate with nonexistence object key;
    - attempt to insert value to array at position beyond of it size;
    - etc.
    """


class JsonPatchTestFailed(JsonPatchException, AssertionError):
    """ A Test operation failed """


def multidict(ordered_pairs):
    """Convert duplicate keys values to lists."""
    # read all values into lists
    mdict = collections.defaultdict(list)
    for key, value in ordered_pairs:
        mdict[key].append(value)

    return dict(
        # unpack lists that have only 1 item
        (key, values[0] if len(values) == 1 else values)
        for key, values in mdict.items()
    )


def get_loadjson():
    """ adds the object_pairs_hook parameter to json.load when possible

    The "object_pairs_hook" parameter is used to handle duplicate keys when
    loading a JSON object. This parameter does not exist in Python 2.6. This
    methods returns an unmodified json.load for Python 2.6 and a partial
    function with object_pairs_hook set to multidict for Python versions that
    support the parameter. """

    argspec = inspect.getargspec(json.load)
    if 'object_pairs_hook' not in argspec.args:
        return json.load

    return functools.partial(json.load, object_pairs_hook=multidict)

json.load = get_loadjson()


def apply_patch(doc, patch, in_place=False):
    """Apply list of patches to specified json document.

    :param doc: Document object.
    :type doc: dict

    :param patch: JSON patch as list of dicts or raw JSON-encoded string.
    :type patch: list or str

    :param in_place: While :const:`True` patch will modify target document.
                     By default patch will be applied to document copy.
    :type in_place: bool

    :return: Patched document object.
    :rtype: dict

    >>> doc = {'foo': 'bar'}
    >>> patch = [{'op': 'add', 'path': '/baz', 'value': 'qux'}]
    >>> other = apply_patch(doc, patch)
    >>> doc is not other
    True
    >>> other == {'foo': 'bar', 'baz': 'qux'}
    True
    >>> patch = [{'op': 'add', 'path': '/baz', 'value': 'qux'}]
    >>> apply_patch(doc, patch, in_place=True) == {'foo': 'bar', 'baz': 'qux'}
    True
    >>> doc == other
    True
    """

    if isinstance(patch, basestring):
        patch = JsonPatch.from_string(patch)
    else:
        patch = JsonPatch(patch)
    return patch.apply(doc, in_place)


def make_patch(src, dst):
    """Generates patch by comparing of two document objects. Actually is
    a proxy to :meth:`JsonPatch.from_diff` method.

    :param src: Data source document object.
    :type src: dict

    :param dst: Data source document object.
    :type dst: dict

    >>> src = {'foo': 'bar', 'numbers': [1, 3, 4, 8]}
    >>> dst = {'baz': 'qux', 'numbers': [1, 4, 7]}
    >>> patch = make_patch(src, dst)
    >>> new = patch.apply(src)
    >>> new == dst
    True
    """
    return JsonPatch.from_diff(src, dst)


class JsonPatch(object):
    """A JSON Patch is a list of Patch Operations.

    >>> patch = JsonPatch([
    ...     {'op': 'add', 'path': '/foo', 'value': 'bar'},
    ...     {'op': 'add', 'path': '/baz', 'value': [1, 2, 3]},
    ...     {'op': 'remove', 'path': '/baz/1'},
    ...     {'op': 'test', 'path': '/baz', 'value': [1, 3]},
    ...     {'op': 'replace', 'path': '/baz/0', 'value': 42},
    ...     {'op': 'remove', 'path': '/baz/1'},
    ... ])
    >>> doc = {}
    >>> result = patch.apply(doc)
    >>> expected = {'foo': 'bar', 'baz': [42]}
    >>> result == expected
    True

    JsonPatch object is iterable, so you could easily access to each patch
    statement in loop:

    >>> lpatch = list(patch)
    >>> expected = {'op': 'add', 'path': '/foo', 'value': 'bar'}
    >>> lpatch[0] == expected
    True
    >>> lpatch == patch.patch
    True

    Also JsonPatch could be converted directly to :class:`bool` if it contains
    any operation statements:

    >>> bool(patch)
    True
    >>> bool(JsonPatch([]))
    False

    This behavior is very handy with :func:`make_patch` to write more readable
    code:

    >>> old = {'foo': 'bar', 'numbers': [1, 3, 4, 8]}
    >>> new = {'baz': 'qux', 'numbers': [1, 4, 7]}
    >>> patch = make_patch(old, new)
    >>> if patch:
    ...     # document have changed, do something useful
    ...     patch.apply(old)    #doctest: +ELLIPSIS
    {...}
    """
    def __init__(self, patch):
        self.patch = patch

        self.operations = {
            'remove': RemoveOperation,
            'add': AddOperation,
            'replace': ReplaceOperation,
            'move': MoveOperation,
            'test': TestOperation,
            'copy': CopyOperation,
        }

    def __str__(self):
        """str(self) -> self.to_string()"""
        return self.to_string()

    def __bool__(self):
        return bool(self.patch)

    __nonzero__ = __bool__

    def __iter__(self):
        return iter(self.patch)

    def __hash__(self):
        return hash(tuple(self._ops))

    def __eq__(self, other):
        if not isinstance(other, JsonPatch):
            return False
        return self._ops == other._ops

    def __ne__(self, other):
        return not(self == other)

    @classmethod
    def from_string(cls, patch_str):
        """Creates JsonPatch instance from string source.

        :param patch_str: JSON patch as raw string.
        :type patch_str: str

        :return: :class:`JsonPatch` instance.
        """
        patch = json.loads(patch_str)
        return cls(patch)

    @classmethod
    def from_diff(cls, src, dst):
        """Creates JsonPatch instance based on comparing of two document
        objects. Json patch would be created for `src` argument against `dst`
        one.

        :param src: Data source document object.
        :type src: dict

        :param dst: Data source document object.
        :type dst: dict

        :return: :class:`JsonPatch` instance.

        >>> src = {'foo': 'bar', 'numbers': [1, 3, 4, 8]}
        >>> dst = {'baz': 'qux', 'numbers': [1, 4, 7]}
        >>> patch = JsonPatch.from_diff(src, dst)
        >>> new = patch.apply(src)
        >>> new == dst
        True
        """
        def compare_values(path, value, other):
            if value == other:
                return
            if isinstance(value, dict) and isinstance(other, dict):
                for operation in compare_dict(path, value, other):
                    yield operation
            elif isinstance(value, list) and isinstance(other, list):
                for operation in compare_list(path, value, other):
                    yield operation
            else:
                yield {'op': 'replace', 'path': '/'.join(path), 'value': other}

        def compare_dict(path, src, dst):
            for key in src:
                if key not in dst:
                    yield {'op': 'remove', 'path': '/'.join(path + [key])}
                    continue
                current = path + [key]
                for operation in compare_values(current, src[key], dst[key]):
                    yield operation
            for key in dst:
                if key not in src:
                    yield {'op': 'add',
                           'path': '/'.join(path + [key]),
                           'value': dst[key]}

        def compare_list(path, src, dst):
            lsrc, ldst = len(src), len(dst)
            for idx in range(min(lsrc, ldst)):
                current = path + [str(idx)]
                for operation in compare_values(current, src[idx], dst[idx]):
                    yield operation
            if lsrc < ldst:
                for idx in range(lsrc, ldst):
                    current = path + [str(idx)]
                    yield {'op': 'add',
                           'path': '/'.join(current),
                           'value': dst[idx]}
            elif lsrc > ldst:
                for idx in reversed(range(ldst, lsrc)):
                    yield {'op': 'remove', 'path': '/'.join(path + [str(idx)])}

        return cls(list(compare_dict([''], src, dst)))

    def to_string(self):
        """Returns patch set as JSON string."""
        return json.dumps(self.patch)

    @property
    def _ops(self):
        return tuple(map(self._get_operation, self.patch))

    def apply(self, obj, in_place=False):
        """Applies the patch to given object.

        :param obj: Document object.
        :type obj: dict

        :param in_place: Tweaks way how patch would be applied - directly to
                         specified `obj` or to his copy.
        :type in_place: bool

        :return: Modified `obj`.
        """

        if not in_place:
            obj = copy.deepcopy(obj)

        for operation in self._ops:
            obj = operation.apply(obj)

        return obj

    def _get_operation(self, operation):
        if 'op' not in operation:
            raise JsonPatchException("Operation does not contain 'op' member")

        op = operation['op']

        if not isinstance(op, basestring):
            raise JsonPatchException("Operation must be a string")

        if op not in self.operations:
            raise JsonPatchException("Unknown operation {0!r}".format(op))

        cls = self.operations[op]
        return cls(operation)


class PatchOperation(object):
    """A single operation inside a JSON Patch."""

    def __init__(self, operation):
        self.location = operation['path']
        self.pointer = JsonPointer(self.location)
        self.operation = operation

    def apply(self, obj):
        """Abstract method that applies patch operation to specified object."""
        raise NotImplementedError('should implement patch operation.')

    def __hash__(self):
        return hash(frozenset(self.operation.items()))

    def __eq__(self, other):
        if not isinstance(other, PatchOperation):
            return False
        return self.operation == other.operation

    def __ne__(self, other):
        return not(self == other)


class RemoveOperation(PatchOperation):
    """Removes an object property or an array element."""

    def apply(self, obj):
        subobj, part = self.pointer.to_last(obj)
        try:
            del subobj[part]
        except IndexError as ex:
            raise JsonPatchConflict(str(ex))

        return obj


class AddOperation(PatchOperation):
    """Adds an object property or an array element."""

    def apply(self, obj):
        value = self.operation["value"]
        subobj, part = self.pointer.to_last(obj)

        if isinstance(subobj, list):
            if part == '-':
                subobj.append(value)  # pylint: disable=E1103

            elif part > len(subobj) or part < 0:
                raise JsonPatchConflict("can't insert outside of list")

            else:
                subobj.insert(part, value)  # pylint: disable=E1103

        elif isinstance(subobj, dict):
            if part is None:
                obj = value  # we're replacing the root
            else:
                subobj[part] = value

        else:
            raise TypeError("invalid document type {0}".format(type(subobj)))

        return obj


class ReplaceOperation(PatchOperation):
    """Replaces an object property or an array element by new value."""

    def apply(self, obj):
        value = self.operation["value"]
        subobj, part = self.pointer.to_last(obj)

        if part is None:
            return value

        if isinstance(subobj, list):
            if part > len(subobj) or part < 0:
                raise JsonPatchConflict("can't replace outside of list")

        elif isinstance(subobj, dict):
            if not part in subobj:
                msg = "can't replace non-existent object '{0}'".format(part)
                raise JsonPatchConflict(msg)
        else:
            raise TypeError("invalid document type {0}".format(type(subobj)))

        subobj[part] = value
        return obj


class MoveOperation(PatchOperation):
    """Moves an object property or an array element to new location."""

    def apply(self, obj):
        from_ptr = JsonPointer(self.operation['from'])
        subobj, part = from_ptr.to_last(obj)
        value = subobj[part]

        if self.pointer.contains(from_ptr):
            raise JsonPatchException('Cannot move values into its own children')

        obj = RemoveOperation({
            'op': 'remove',
            'path': self.operation['from']
        }).apply(obj)

        obj = AddOperation({
            'op': 'add',
            'path': self.location,
            'value': value
        }).apply(obj)

        return obj


class TestOperation(PatchOperation):
    """Test value by specified location."""

    def apply(self, obj):
        try:
            subobj, part = self.pointer.to_last(obj)
            if part is None:
                val = subobj
            else:
                val = self.pointer.walk(subobj, part)
        except JsonPointerException as ex:
            raise JsonPatchTestFailed(str(ex))

        if 'value' in self.operation:
            value = self.operation['value']
            if val != value:
                msg = '{0} ({1}) is not equal to tested value {2} ({3})'
                raise JsonPatchTestFailed(msg.format(val, type(val),
                                                     value, type(value)))

        return obj


class CopyOperation(PatchOperation):
    """ Copies an object property or an array element to a new location """

    def apply(self, obj):
        from_ptr = JsonPointer(self.operation['from'])
        subobj, part = from_ptr.to_last(obj)
        value = copy.deepcopy(subobj[part])

        obj = AddOperation({
            'op': 'add',
            'path': self.location,
            'value': value
        }).apply(obj)

        return obj
