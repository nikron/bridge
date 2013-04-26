#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

class ESafeLoader(yaml.SafeLoader):

    def compose_node(self, parent, index):
        anchor = None
        if self.check_event(yaml.AliasEvent):
            anchor = self.peek_event().anchor

        node = super(ESafeLoader, self).compose_node(parent, index)

        if anchor is not None:
            node.anchor = anchor

        return node

    def construct_object(self, node, deep=False):
        data = super(ESafeLoader, self).construct_object(node, deep)
        if hasattr(node, 'anchor') and hasattr(data, '__dict__'):
            data.anchor = node.anchor
        return data

class ESafeDumper(yaml.SafeDumper):

    ANCHOR_TEMPLATE = u'%s%03d'

    def __init__(self, *args, **kargs):
        super(ESafeDumper, self).__init__(*args, **kargs)
        self.last_anchor_id_by_tag = {}

    def serialize(self, node):
        super(ESafeDumper, self).serialize(node)
        self.last_anchor_id_by_tag = {}

    def generate_anchor(self, node):
        if hasattr(node, 'anchor'):
            # TODO: rename `anchor` to `_id`?
            return node.anchor
        elif hasattr(node, 'tag'):
            last_anchor_id = self.last_anchor_id_by_tag[node.tag] = self.last_anchor_id_by_tag.setdefault(node.tag, 0) + 1
            return self.ANCHOR_TEMPLATE % (node.tag[1:].lower(), last_anchor_id)
        else:
            self.last_anchor_id = self.last_anchor_id + 1
            return self.ANCHOR_TEMPLATE % ('id', last_anchor_id)

    def represent_yaml_object(self, tag, data, cls, flow_style=None):
        anchor = None
        if hasattr(data, 'anchor'):
            anchor = data.anchor
            del data.anchor

        node = super(ESafeDumper, self).represent_yaml_object(tag, data, cls, flow_style)

        if anchor is not None:
            node.anchor = anchor

        return node
