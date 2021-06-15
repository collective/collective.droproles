import logging
import os


try:
    from ftw.upgrade.jsonapi.utils import validate_tempfile_authentication_header_value
except ImportError:
    validate_tempfile_authentication_header_value = None

logger = logging.getLogger(__name__)
# Environment variable to determine if we drop roles.
DROP_ROLES_ENV = "DROP_ROLES"
# Drop these roles:
DROPPED_ROLES = set(
    ["Manager", "Site Administrator", "Editor", "Reviewer", "Contributor"]
)


def read_drop_roles_from_env():
    # By default, we do not drop roles.
    drop = os.getenv(DROP_ROLES_ENV, False)
    if not drop:
        return False
    try:
        drop = int(drop)
    except (ValueError, TypeError, AttributeError):
        logger.warning("Ignored non-integer %s environment variable.", DROP_ROLES_ENV)
        return False
    if drop == 0:
        logger.info(
            "%s environment variable set to zero. Will NOT drop roles.",
            DROP_ROLES_ENV,
        )
        return False
    logger.info(
        "%s environment variable set to %d. Will drop roles.",
        DROP_ROLES_ENV,
        drop,
    )
    return True


def _drop_roles(self, orig):
    if not orig:
        return orig
    if self._is_upgrade_user():
        return orig
    # Drop some roles.
    new_result = set(orig).difference(DROPPED_ROLES)
    # Return the original type, usually a list.
    if isinstance(orig, tuple):
        return tuple(new_result)
    return list(new_result)


def _is_upgrade_user(self):
    """Is this the ftw system-upgrade user from the bin/upgrade script?

    The bin/upgrade script attaches itself to the first zeoclient it finds,
    which is likely the public zeoclient where roles are dropped.
    It cannot work then.
    So we check for a header.
    """
    if validate_tempfile_authentication_header_value is None:
        # The ftw.upgrade package is not available, so this cannot be the upgrade user.
        return False
    auth = self.REQUEST.getHeader("x-ftw.upgrade-tempfile-auth")
    if not auth:
        return False
    # Validate the header.  This will raise a ValueError if something is wrong.
    validate_tempfile_authentication_header_value(auth)
    # No ValueError raised, so this is the upgrade user.
    return True


def getRoles(self):
    """Get global roles assigned to the user."""
    result = self._orig_getRoles()
    # logger.info("%s.getRoles: %s" % (self.__class__.__name__, result))
    return self._drop_roles(result)


def getRolesInContext(self, object):
    result = self._orig_getRolesInContext(object)
    # logger.info("%s.getRolesInContext: %s" % (self.__class__.__name__, result))
    return self._drop_roles(result)


def allowed(self, object, object_roles=None):
    """Check whether the user has access to object. The user must
    have one of the roles in object_roles to allow access."""
    # logger.info("%s.allowed: %s" % (self.__class__.__name__, object_roles))
    object_roles = self._drop_roles(object_roles)
    return self._orig_allowed(object, object_roles=object_roles)


def patch():
    """Patch getRolesInContext for various user implementations.

    Luckily all methods of this name can be replaced by a single method
    that calls the original and filters out unwanted roles.

    Let's patch the getRoles and allowed methods as well.
    I think patching getRolesInContext may be sufficient,
    but patching the others can speed things up a bit.

    Not all classed have all three methods,
    but via inheritance they do have all of them.

    - SimpleUser inherits from BasicUser
    - PropertiedUser inherits from BasicUser
    - PloneUser inherits from PropertiedUser

    Remarks:

    - For Plone Groups, getRolesInContext is always empty.
    - This handles the standard users, not users from LDAP or some SSO thingie.
    - If this works in practice, we should put this into a separate package,
      to use in all KNMP Plone Sites.
    """
    from AccessControl.users import BasicUser
    from AccessControl.users import SimpleUser
    from Products.PluggableAuthService.PropertiedUser import PropertiedUser
    from Products.PlonePAS.plugins.ufactory import PloneUser

    klasses = (
        BasicUser,
        SimpleUser,
        PropertiedUser,
        PloneUser,
    )

    for klass in klasses:
        for method_name in ("_drop_roles", "_is_upgrade_user"):
            patched_method = globals()[method_name]
            setattr(klass, method_name, patched_method)
        for method_name in ("getRoles", "getRolesInContext", "allowed"):
            if method_name not in klass.__dict__:
                logger.info("Class %s has no method %s.", klass, method_name)
                continue
            orig_method = getattr(klass, method_name)
            patched_method = globals()[method_name]
            orig_name = "_orig_{}".format(method_name)
            setattr(klass, orig_name, orig_method)
            setattr(klass, method_name, patched_method)
            logger.info("Patched class %s method %s.", klass, method_name)


# Do we want to drop roles?
DROP_ROLES = read_drop_roles_from_env()
if DROP_ROLES:
    # Apply the patches.
    patch()
