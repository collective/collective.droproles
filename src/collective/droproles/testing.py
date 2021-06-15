# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer

import collective.droproles


class CollectiveDropRolesLayer(PloneSandboxLayer):
    pass


COLLECTIVE_DROPROLES_FIXTURE = CollectiveDropRolesLayer()


COLLECTIVE_DROPROLES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_DROPROLES_FIXTURE,),
    name="CollectiveDropRolesLayer:IntegrationTesting",
)


COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_DROPROLES_FIXTURE,),
    name="CollectiveDropRolesLayer:FunctionalTesting",
)
