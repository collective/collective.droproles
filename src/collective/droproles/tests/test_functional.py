# -*- coding: utf-8 -*-
from collective.droproles import patches
from collective.droproles.testing import COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser
from zExceptions import Unauthorized

import transaction
import unittest


def mock_ftw_validate_pass(auth):
    pass


def mock_ftw_validate_fail(auth):
    raise ValueError("mock fail for ftw.upgrade authentication")


def add_ftw_upgrade_header(browser):
    browser.addHeader("x-ftw.upgrade-tempfile-auth", "dummy")


class TestIntegration(unittest.TestCase):
    """Test that the patch works in Plone."""

    layer = COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        # Store value of PATCHED.
        self._orig_patched = patches.PATCHED
        # store original ftw.upgrade validation method
        self.orig_ftw = patches.validate_tempfile_authentication_header_value

    def tearDown(self):
        # Restore PATCHED value.  Might not matter, but seems cleaner.
        if self._orig_patched and not patches.PATCHED:
            # It was patched, but not anymore, so repatch.
            patches.patch_all()
        elif not self._orig_patched and patches.PATCHED:
            # It was not patched, but now it is, so unpatch.
            patches.unpatch_all()
        # restore ftw.upgrade validation method
        patches.validate_tempfile_authentication_header_value = self.orig_ftw

    def get_admin_browser(self):
        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
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
        browser = self.get_admin_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

    def test_drop_all_roles_admin(self):
        patches.unpatch_all()
        patches.patch_all(anonymous=True)
        browser = self.get_admin_browser()
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

    def test_drop_all_roles_anonymous(self):
        patches.unpatch_all()
        patches.patch_all(anonymous=True)
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
        self.assertIn(TEST_USER_ID, browser.contents)

    def test_drop_all_roles_member(self):
        patches.unpatch_all()
        patches.patch_all(anonymous=True)
        browser = self.get_member_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        # Member role is no longer available, so we can not view this page:
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@personal-preferences")
        # We can still view the homepage, and are somewhat authenticated.
        browser.open(self.portal.absolute_url())
        self.assertIn(TEST_USER_ID, browser.contents)

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

    def test_drop_all_roles_contributor(self):
        patches.unpatch_all()
        patches.patch_all(anonymous=True)
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        transaction.commit()
        browser = self.get_member_browser()
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@personal-preferences")
        # Contributor role is no longer available, so we have no options here:
        browser.open(self.portal.absolute_url())
        self.assertNotIn("Add new", browser.contents)

    def test_drop_roles_false_upgrade_admin(self):
        patches.unpatch_all()
        browser = self.get_admin_browser()
        add_ftw_upgrade_header(browser)
        browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

    def test_drop_roles_true_upgrade_admin(self):
        patches.patch_all()
        # We mock that we are the system-upgrade user from ftw.upgrade.
        # Login as Manager.
        browser = self.get_admin_browser()
        # Add a header that will convince ftw.upgrade (if installed)
        # that its special user is authenticated.
        # Normally it is not so easily convinced, but we will mock the function
        # that does the check.
        # Our patch should allow the Manager role then, even with DROP_ROLES=1.
        add_ftw_upgrade_header(browser)

        # At this point, the user is a standard Manager, and the role will be dropped.
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

        # Add a patch so our dummy ftw upgrade header will get checked
        # and let the check fail.
        patches.validate_tempfile_authentication_header_value = mock_ftw_validate_fail
        with self.assertRaises(ValueError):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

        # Add a patch so our dummy ftw upgrade header will get checked
        # and let the check pass.  We should retain the Manager role then.
        patches.validate_tempfile_authentication_header_value = mock_ftw_validate_pass
        browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

    def test_drop_all_roles_upgrade_admin(self):
        patches.unpatch_all()
        patches.patch_all(anonymous=True)
        browser = self.get_admin_browser()
        add_ftw_upgrade_header(browser)
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

        # The ftw upgrade validation code will never get called
        # when we drop all roles.  Try patching it anyway.
        patches.validate_tempfile_authentication_header_value = mock_ftw_validate_fail
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
        patches.validate_tempfile_authentication_header_value = mock_ftw_validate_pass
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")

    def test_drop_roles_true_upgrade_anonymous(self):
        patches.patch_all()
        # This is mostly to see if we can catch a corner case where the user has no REQUEST attribute.
        # Use an anonymous browser with the ftw upgrade header.
        # Well, it doesn't trigger the problem I want, but I guess the test is fine.
        browser = self.get_anonymous_browser()
        add_ftw_upgrade_header(browser)

        # Add a patch so our dummy ftw upgrade header will get checked
        # and let the check fail.
        patches.validate_tempfile_authentication_header_value = mock_ftw_validate_fail
        with self.assertRaises(ValueError):
            browser.open(self.portal.absolute_url())

        # Add a patch so our dummy ftw upgrade header will get checked
        # and let the check pass.
        patches.validate_tempfile_authentication_header_value = mock_ftw_validate_pass
        browser.open(self.portal.absolute_url())
        with self.assertRaises(Unauthorized):
            browser.open(self.portal.absolute_url() + "/@@overview-controlpanel")
