# -*- coding: utf-8 -*-
from collective.droproles import patches
from collective.droproles.testing import COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from zExceptions import Unauthorized

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
        # Store value of PATCHED.
        self._orig_patched = patches.PATCHED

    def tearDown(self):
        # Restore PATCHED value.  Might not matter, but seems cleaner.
        if self._orig_patched and not patches.PATCHED:
            # It was patched, but not anymore, so repatch.
            patches.patch_all()
        elif not self._orig_patched and patches.PATCHED:
            # It was not patched, but now it is, so unpatch.
            patches.unpatch_all()

    def test_drop_roles_false(self):
        patches.unpatch_all()
        self.browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        # open("/tmp/test.html", "w").write(self.browser.contents)
        self.assertFalse("Log in" in self.browser.contents)
        self.assertTrue("Site Setup" in self.browser.contents)

    def test_drop_roles_true(self):
        patches.patch_all()
        with self.assertRaises(Unauthorized):
            self.browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
