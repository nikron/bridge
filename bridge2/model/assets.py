from __future__ import absolute_import, division, print_function, unicode_literals

class Asset(object):
    def __init__(self, locator, profile):
        self.locator = locator
        self.profile = profile
        self._device = profile.bind(locator)

    @property
    def attributes(self):
        return self._profile.attributes
