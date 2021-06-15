# -*- coding: utf-8 -*-
from collective.droproles import config
from collective.droproles.testing import COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

import unittest


class TestIntegration(unittest.TestCase):
    """Test that the patch works in Plone."""

    layer = COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )
        # Store DROP_ROLES setting.
        self._orig_drop_roles = config.DROP_ROLES

    def tearDown(self):
        # Restore DROP_ROLES setting.
        config.DROP_ROLES = self._orig_drop_roles

    def test_drop_roles_false(self):
        config.DROP_ROLES = False
        self.browser.open(self.portal.absolute_url())
        # open("/tmp/test.html", "w").write(self.browser.contents)
        self.assertFalse("Log in" in self.browser.contents)
        self.assertTrue("Site Setup" in self.browser.contents)

    def test_drop_roles_true(self):
        config.DROP_ROLES = True
        self.browser.open(self.portal.absolute_url())
        # open("/tmp/test.html", "w").write(self.browser.contents)
        self.assertTrue("Log in" in self.browser.contents)
        self.assertFalse("Site Setup" in self.browser.contents)
