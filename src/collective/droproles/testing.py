# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer

import collective.droproles


class CollectiveDropRolesLayer(PloneSandboxLayer):
    pass

    # def setUpZope(self, app, configurationContext):
    #     # Load any other ZCML that is required for your tests.
    #     # The z3c.autoinclude feature is disabled in the Plone fixture base
    #     # layer.
    #     self.loadZCML(package=collective.droproles)


COLLECTIVE_DROPROLES_FIXTURE = CollectiveDropRolesLayer()


COLLECTIVE_DROPROLES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_DROPROLES_FIXTURE,), name="CollectiveDropRolesLayer:IntegrationTesting"
)


COLLECTIVE_DROPROLES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_DROPROLES_FIXTURE,), name="CollectiveDropRolesLayer:FunctionalTesting"
)
