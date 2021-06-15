.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi. It is a comment.

collective.droproles
====================

This is a monkey patch for PAS (``PluggableAuthService``).
It drops roles like Manager or Editor on Plone Sites.
An Editor can still login, but only has the Member and Authenticated roles.


Features
--------

- A patch for methods ``getRoles``, ``getRolesInContext``, and ``allowed`` on various user classes,
  returning the original list, but with the following roles removed:
  Manager, Site Administrator, Editor, Reviewer, Contributor.
  This is temporary: no database changes are made.

- Configuration via environment variable ``DROP_ROLES``.
  By default we do not drop roles, but with ``DROP_ROLES=1``, we do drop them.


Use case
--------

You have a Plone Site on two domains:

- edit.example.local is for editing.
  Users with the Editor or Manager role login here to edit and manage the site.
  This is a local domain that can only be reached within your local network or a VPN.

- www.example.org is for anonymous users and maybe also for standard Members without extra roles.
  This domain is protected by a special firewall to prevent common web attacks like
  dubious form submissions, request flooding, spammers, cross site scripting attacks, etcetera.

Problems:

- Editors sometimes login to the public domain,
  and get errors during editing because the firewall is too protective.

- The system administrator complains that he has setup a special domain for editing and managing,
  so that no changes can come in from the public site,
  and yet unexpectedly the editors can login and make changes via the public site anyway.

This package gives you the option to treat all users as having at most the Member or Authenticated roles.
A Manager can login, but cannot go to the Plone overview controlpanel.


Installation
------------

Install collective.droproles by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.droproles

    [instance]
    recipe = plone.recipe.zope2instance
    environment-vars =
        DROP_ROLES 1

and then running ``bin/buildout``.

Without the environment variable, it does nothing.


Configuration
-------------

You can set an environment variable to drop the roles::

    export DROP_ROLES=1

Set this to 1 (or another positive integer) for yes, and 0 for no.
Any other values will be ignored.

Note that the OS environment can be different when you manually start your Plone instance or start it in a cronjob.
So it is better to set this in your Plone ``buildout.cfg``::

    [instance]
    recipe = plone.recipe.zope2instance
    environment-vars =
        DROP_ROLES 1

Run the buildout and it will be set in the Plone config,
in this case in ``parts/instance/etc/zope.conf``.

If you have a ZEO setup with two zeoclients, where one zeoclient gets all traffic from editors, and another gets the anonymous visitors, you can do this:

- zeoclient for editors: ``DROP_ROLES 0``
- zeoclient for anonymous: ``DROP_ROLES 1``

Now editors can edit normally in their edit environment.
And when they accidentally login on the anonymous environment, they will be treated as simple Members without extra roles.

Technically, ``DROP_ROLES 0`` does nothing, because it is the default.
But it may be good to be specific.


Suggested buildout usage
------------------------

This is a suggestion on how to properly add this in a buildout.
Note that this focuses on configuring collective.droproles, and ignores lots of other useful settings::

    [zeoclient]
    # Configuration for public zeoclient.
    recipe = plone.recipe.zope2instance
    http-address = 8080
    zeo-client = on
    eggs =
        Plone
        collective.droproles
    # Environment variables shared by all zeoclients:
    base-environment-vars =
        zope_i18n_compile_mo_files true
    environment-vars =
        ${:base-environment-vars}
    # In the public zeoclient, we drop roles:
        DROP_ROLES 1

    [zeoclient-cms]
    # Second Plone zeoclient, only used for CMS, so for editors.
    # The next weird line means: inherit all settings from the [zeoclient] section:
    <= zeoclient
    # Use a different port:
    http-address = 8090
    environment-vars =
        ${:base-environment-vars}
    # In the CMS zeoclient, we do not want to drop roles:
        DROP_ROLES 0

    [instance]
    # Standalone Plone instance without ZEO setup, for local development.
    <= zeoclient
    zeo-client = off
    environment-vars =
        ${:base-environment-vars}
    # With single instance, we do not want to drop roles:
        DROP_ROLES 0


ftw.upgrade
~~~~~~~~~~~

If you use the ``bin/upgrade`` script from ``ftw.upgrade``,
you are automatically authenticated and have the Manager role.
But if this script attaches itself to the public zeoclient above,
the Manager role would be dropped, making the script useless.
We have a patch for this that is active when our other patches are active.
So: ``bin/upgrade`` should work just fine.


Support
-------

If you are having issues, please let us know.
Contact Maurits van Rees at Zest Software, m.van.rees@zestsoftware.nl.
Or open an issue in `GitHub <https://github.com/collective/collective.droproles/issues/>`_.


License
-------

The project is licensed under the GPLv2.
