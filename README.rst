Introduction
============

Example code for setting LDAP with ``pas.plugins.ldap``.


Usage
-----

- Copy ``ldapsettings.xml``, ``registry.xml`` and ``metadata.xml`` files from ``profiles/default`` to your own profile.
- Adapt for your site, mostly the password and the LDAP/AD names and user account.
- Check the ``install_requires`` in ``setup.py`` as well.

Tested on Plone 4.3 and 5.1.


Optional: script to activate ldap
---------------------------------

In the root of this package is a ``setup_ldap.py`` script.
Call this with::

    bin/instance run setup_ldap.py

You can enable or disable ``pas.plugins.ldap`` with this, see the options.
This includes disabling an old ``plone.app.ldap`` setup.
Also useful after copying a production database to your laptop and disabling ldap.


Optional: memcache from environment
-----------------------------------

You can set an OS environment to override the memcache::

    export PAS_PLUGINS_LDAP_MEMCACHE=127.0.0.1:12345

Then changing the setting in http://localhost:8080/Plone/plone_ldapcontrolpanel has no effect.
You need the ``componentregistry.xml`` from the profile for this.

This is useful when you have a customer with multiple sites on a single server,
and you put the LDAP/AD settings in one shared package,
but you only have that one memcache setting that you would need to change for each site.
Instead, you can now use an environment setting for that.
