import logging
import os


logger = logging.getLogger(__name__)
# Environment variable to determine if we drop roles.
DROP_ROLES_ENV = "DROP_ROLES"


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
