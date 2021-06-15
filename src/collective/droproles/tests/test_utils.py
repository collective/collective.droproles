# -*- coding: utf-8 -*-
from collective.droproles import utils

import os
import unittest


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.orig_drop_roles_env = None
        if utils.DROP_ROLES_ENV in os.environ:
            self.orig_drop_roles_env = os.environ[utils.DROP_ROLES_ENV]
            del os.environ[utils.DROP_ROLES_ENV]
        self.orig_drop_all_roles_env = None
        if utils.DROP_ALL_ROLES_ENV in os.environ:
            self.orig_drop_all_roles_env = os.environ[utils.DROP_ALL_ROLES_ENV]
            del os.environ[utils.DROP_ALL_ROLES_ENV]

    def tearDown(self):
        if self.orig_drop_roles_env is not None:
            os.environ[utils.DROP_ROLES_ENV] = self.orig_drop_roles_env
        if self.orig_drop_all_roles_env is not None:
            os.environ[utils.DROP_ALL_ROLES_ENV] = self.orig_drop_all_roles_env

    def test_read_drop_roles_from_env(self):
        # Default:
        self.assertFalse(utils.read_drop_roles_from_env())

        # Never:
        os.environ[utils.DROP_ROLES_ENV] = "0"
        self.assertFalse(utils.read_drop_roles_from_env())

        # Always:
        os.environ[utils.DROP_ROLES_ENV] = "1"
        self.assertTrue(utils.read_drop_roles_from_env())
        os.environ[utils.DROP_ROLES_ENV] = "42"
        self.assertTrue(utils.read_drop_roles_from_env())

        # Bad value:
        os.environ[utils.DROP_ROLES_ENV] = "no integer"
        self.assertFalse(utils.read_drop_roles_from_env())

    def test_read_drop_all_roles_from_env(self):
        # Default:
        self.assertFalse(utils.read_drop_all_roles_from_env())

        # Never:
        os.environ[utils.DROP_ALL_ROLES_ENV] = "0"
        self.assertFalse(utils.read_drop_all_roles_from_env())

        # Always:
        os.environ[utils.DROP_ALL_ROLES_ENV] = "1"
        self.assertTrue(utils.read_drop_all_roles_from_env())
        os.environ[utils.DROP_ALL_ROLES_ENV] = "42"
        self.assertTrue(utils.read_drop_all_roles_from_env())

        # Bad value:
        os.environ[utils.DROP_ALL_ROLES_ENV] = "no integer"
        self.assertFalse(utils.read_drop_all_roles_from_env())
