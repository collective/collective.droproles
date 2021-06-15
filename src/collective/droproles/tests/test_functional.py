# -*- coding: utf-8 -*-
from collective.droproles import patches
from collective.droproles.testing import COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from zExceptions import Unauthorized

import transaction
import unittest


class TestIntegration(unittest.TestCase):
    """Test that the patch works in Plone."""

    layer = COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
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

    def get_admin_browser(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader(
            "Authorization", "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )
        return browser

    def get_member_browser(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader(
            "Authorization", "Basic {0}:{1}".format(TEST_USER_NAME, TEST_USER_PASSWORD)
        )
        return browser

    def get_anonymous_browser(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        return browser

    def test_drop_roles_false_admin(self):
        patches.unpatch_all()
        browser = self.get_admin_browser()
        browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        self.assertFalse("Log in" in browser.contents)
        self.assertTrue("Site Setup" in browser.contents)

    def test_drop_roles_true_admin(self):
        patches.patch_all()
        browser = self.get_anonymous_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

    def test_drop_roles_false_anonymous(self):
        patches.unpatch_all()
        browser = self.get_anonymous_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@personal-preferences")

    def test_drop_roles_true_anonymous(self):
        patches.patch_all()
        browser = self.get_anonymous_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@personal-preferences")

    def test_drop_roles_false_member(self):
        patches.unpatch_all()
        browser = self.get_member_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        # Member role is still available, so we can view this page:
        browser.open(self.portal.absolute_url() + "/@@personal-preferences")

    def test_drop_roles_true_member(self):
        patches.patch_all()
        browser = self.get_member_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        # Member role is still available, so we can view this page:
        browser.open(self.portal.absolute_url() + "/@@personal-preferences")
        self.assertIn(TEST_USER_NAME, browser.contents)

    def test_drop_roles_false_contributor(self):
        patches.unpatch_all()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        transaction.commit()
        browser = self.get_member_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        # Member role is still available, so we can view this page:
        browser.open(self.portal.absolute_url() + "/@@personal-preferences")
        # Contributor role is still available, so we have options here:
        browser.open(self.portal.absolute_url())
        self.assertIn("Add new", browser.contents)
        browser.getLink("Folder").click()

    def test_drop_roles_true_contributor(self):
        patches.patch_all()
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        transaction.commit()
        browser = self.get_member_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        # Member role is still available, so we can view this page:
        browser.open(self.portal.absolute_url() + "/@@personal-preferences")
        # Contributor role is no longer available, so we have no options here:
        browser.open(self.portal.absolute_url())
        self.assertNotIn("Add new", browser.contents)
