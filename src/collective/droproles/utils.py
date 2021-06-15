import logging
import os


logger = logging.getLogger(__name__)
# Environment variable to determine if we drop roles.
DROP_ROLES_ENV = "DROP_ROLES"
# Environment variable to determine if we drop ALL roles.
DROP_ALL_ROLES_ENV = "DROP_ALL_ROLES"


def read_from_env(name=""):
    # By default, we do not drop roles.
    drop = os.getenv(name, False)
    if not drop:
        return False
    try:
        drop = int(drop)
    except (ValueError, TypeError, AttributeError):
        logger.warning("Ignored non-integer %s environment variable.", name)
        return False
    if drop == 0:
        return False
    return True


def read_drop_roles_from_env():
    drop = read_from_env(DROP_ROLES_ENV)
    if not drop:
        return False
    logger.info(
        "%s environment variable set. Will drop roles.",
        DROP_ROLES_ENV,
    )
    return True


def read_drop_all_roles_from_env():
    drop = read_from_env(DROP_ALL_ROLES_ENV)
    if not drop:
        return False
    logger.info(
        "%s environment variable set. Will drop ALL roles, regardless of %s setting.",
        DROP_ALL_ROLES_ENV,
        DROP_ROLES_ENV,
    )
    return True
