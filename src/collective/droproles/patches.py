from .utils import read_drop_all_roles_from_env
from .utils import read_drop_roles_from_env
from AccessControl.users import BasicUser
from AccessControl.users import SimpleUser
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PluggableAuthService.PropertiedUser import PropertiedUser

import logging


try:
    from ftw.upgrade.jsonapi.utils import validate_tempfile_authentication_header_value
except ImportError:
    validate_tempfile_authentication_header_value = None

logger = logging.getLogger(__name__)
# Drop these roles:
DROPPED_ROLES = set(
    ["Manager", "Site Administrator", "Editor", "Reviewer", "Contributor"]
)
# We patch these classes:
USER_CLASSES = [
    BasicUser,
    SimpleUser,
    PropertiedUser,
    PloneUser,
]
# Did we already patch?
# This is to avoid patching twice.  Also helps in tests, where we unpatch.
PATCHED = False


def _drop_roles(self, orig):
    if not orig:
        return orig
    # Do the cheapest test first: see if some roles would be dropped.
    new_result = set(orig).difference(DROPPED_ROLES)
    if len(new_result) == len(orig):
        # no change
        return orig
    # Drop some roles, unless this is a valid ftw.upgrade user.
    if self._is_upgrade_user():
        return orig
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
    request = getattr(self, "REQUEST", None)
    if request is None:
        return False
    auth = request.getHeader("x-ftw.upgrade-tempfile-auth")
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
    # Dropping roles here should have no effect, except a speedup:
    # it is useless to let this code check for a Manager role
    # when we know we have dropped the Manager role from the user.
    object_roles = self._drop_roles(object_roles)
    return self._orig_allowed(object, object_roles=object_roles)


def getRolesAnonymous(self):
    """Force Anonymous as only global role assigned to the user."""
    return ["Anonymous"]


def getRolesInContextAnonymous(self, object):
    """Force Anonymous as only global+local role assigned to the user."""
    return ["Anonymous"]


def allowedAnonymous(self, object, object_roles=None):
    """Check whether the user has access to object. The user must
    have one of the roles in object_roles to allow access.

    Force to only allow access if Anonymous is in the object roles.
    """
    if object_roles is None or "Anonymous" in object_roles:
        return 1
    return 0


def patch_class(klass, anonymous=False):
    if not anonymous:
        for method_name in ("_drop_roles", "_is_upgrade_user"):
            patched_method = globals()[method_name]
            setattr(klass, method_name, patched_method)
    for method_name in ("getRoles", "getRolesInContext", "allowed"):
        if method_name not in klass.__dict__:
            logger.debug("Class %s has no method %s.", klass, method_name)
            continue
        orig_method = getattr(klass, method_name)
        if anonymous:
            patched_method = globals()[method_name + "Anonymous"]
        else:
            patched_method = globals()[method_name]
        orig_name = "_orig_{}".format(method_name)
        setattr(klass, orig_name, orig_method)
        setattr(klass, method_name, patched_method)
        logger.debug("Patched class %s method %s.", klass, method_name)


def unpatch_class(klass):
    # Note: no anonymous variant needed.
    for method_name in ("_drop_roles", "_is_upgrade_user"):
        if method_name not in klass.__dict__:
            continue
        delattr(klass, method_name)
    for method_name in ("getRoles", "getRolesInContext", "allowed"):
        orig_name = "_orig_{}".format(method_name)
        if orig_name not in klass.__dict__:
            logger.info("Class %s has no method %s.", klass, orig_name)
            continue
        orig_method = getattr(klass, orig_name)
        setattr(klass, method_name, orig_method)
        delattr(klass, orig_name)
        logger.info("Unpatched class %s method %s.", klass, method_name)


def patch_all(anonymous=False):
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

    If anonymous is True: we patch the methods with versions that only grant
    anonymous access.
    """
    global PATCHED
    if PATCHED:
        logger.warning("Already patched.")
        return
    for klass in USER_CLASSES:
        patch_class(klass, anonymous=anonymous)
    PATCHED = True


def unpatch_all():
    """Unpatch getRolesInContext for various user implementations.

    Undo what we did in the patch method.
    """
    global PATCHED
    if not PATCHED:
        logger.warning("Not patched, so unpatch not needed.")
        return
    for klass in USER_CLASSES:
        unpatch_class(klass)
    PATCHED = False


# Do we want to drop roles?
if read_drop_all_roles_from_env():
    # Drop ALL roles, effectively making users anonymous,
    # although they can still login.
    patch_all(anonymous=True)
elif read_drop_roles_from_env():
    # Drop the standard roles.
    patch_all()
