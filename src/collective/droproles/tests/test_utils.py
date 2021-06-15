# -*- coding: utf-8 -*-
from collective.droproles import config
from zope.publisher.browser import TestRequest

import os
import unittest


class UtilsTestCase(unittest.TestCase):
    def _make_request(self, do_check=False, dont_check=False):
        # Add zero, one or two headers to the request headers.
        environ = {}
        if do_check:
            environ[config.DO_CHECK_ROLES_HEADER] = 1
        if dont_check:
            environ[config.DONT_CHECK_ROLES_HEADER] = 1
        return TestRequest(environ=environ)

    def test_read_drop_roles_from_env(self):
        from collective.droproles import config

        # Default:
        if config.DROP_ROLES_ENV in os.environ:
            del os.environ[config.DROP_ROLES_ENV]
        config.read_drop_roles_from_env()
        self.assertIsNone(config.DROP_ROLES)

        # Never:
        os.environ[config.DROP_ROLES_ENV] = "0"
        config.read_drop_roles_from_env()
        self.assertFalse(config.DROP_ROLES)

        # Always:
        os.environ[config.DROP_ROLES_ENV] = "1"
        config.read_drop_roles_from_env()
        self.assertTrue(config.DROP_ROLES)
        os.environ[config.DROP_ROLES_ENV] = "42"
        config.read_drop_roles_from_env()
        self.assertTrue(config.DROP_ROLES)

        # Bad value:
        os.environ[config.DROP_ROLES_ENV] = "no integer"
        config.read_drop_roles_from_env()
        self.assertIsNone(config.DROP_ROLES)

    def test_must_check(self):
        from collective.droproles import config
        from collective.droproles.utils import must_check

        # Default:
        config.DROP_ROLES = None
        self.assertTrue(must_check())
        self.assertTrue(must_check(self._make_request()))
        self.assertTrue(must_check(self._make_request(do_check=True)))
        self.assertFalse(must_check(self._make_request(dont_check=True)))
        self.assertTrue(must_check(self._make_request(dont_check=True, do_check=True)))

        # Never:
        config.DROP_ROLES = False
        self.assertFalse(must_check(self._make_request()))
        self.assertFalse(must_check(self._make_request(do_check=True)))
        self.assertFalse(must_check(self._make_request(dont_check=True)))
        self.assertFalse(must_check(self._make_request(dont_check=True, do_check=True)))

        # Always:
        config.DROP_ROLES = True
        self.assertTrue(must_check(self._make_request()))
        self.assertTrue(must_check(self._make_request(do_check=True)))
        self.assertTrue(must_check(self._make_request(dont_check=True)))
        self.assertTrue(must_check(self._make_request(dont_check=True, do_check=True)))
