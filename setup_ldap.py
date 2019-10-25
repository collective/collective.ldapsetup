# - Uninstall old plone.app.ldap.
# - Install new pas.plugins.ldap.
# - Optionally deactivate it for local development.
# Run this with:
# bin/instance run scripts/setup_ldap.py
# or with extra options: --dry-run --site=plone
from node.ext.ldap.interfaces import ILDAPProps
from plone import api
from Products.GenericSetup.tool import UNKNOWN
from zope.component.hooks import setSite

import argparse
import sys
import transaction

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dry-run",
    action="store_true",
    default=False,
    dest="dry_run",
    help="Dry run. No changes will be saved.",
)
parser.add_argument(
    "--verbose",
    action="store_true",
    default=False,
    dest="verbose",
    help="Print details. Otherwise the script is silent when no action is needed.",
)
parser.add_argument(
    "--disable",
    action="store_true",
    default=False,
    dest="disable",
    help="Disable the LDAP plugin in acl_users.",
)
parser.add_argument(
    "--enable",
    action="store_true",
    default=False,
    dest="enable",
    help="Explicitly enable the LDAP plugin in acl_users.",
)
parser.add_argument(
    "--uri",
    default="",
    dest="uri",
    help="Set uri for LDAP server. Can be a port or server:port. "
    "For example, --uri=29636 will set it to localhost:29636, presumably a local port forward from ssh to the real LDAP. "
    "'ldaps://' will be prepended, unless uri starts with 'ldap'.",
)
parser.add_argument(
    "--site",
    default="",
    dest="site",
    help="Single site id to work on. Default is to work on all.",
)
# sys.argv will be something like:
# ['.../parts/instance/bin/interpreter', '-c',
#  'scripts/script_name.py', '--dry-run', '--site=plone']
# Or apparently:
# ['scripts/script_name.py', '--dry-run', '--site=plone']
# Ignore any that do not start with a dash.
cleaned_args = [arg for arg in sys.argv if arg.startswith("-") and arg != "-c"]
options = parser.parse_args(args=cleaned_args)

if options.enable and options.disable:
    print("ERROR: Enable and disable selected. Make up your mind.")
    sys.exit(1)
if options.dry_run and options.verbose:
    print("Dry run selected, will not commit changes.")

# 'app' is the Zope root.
# Get Plone Sites to work on.
if options.site:
    # Get single Plone Site.
    plones = [getattr(app, options.site)]
else:
    # Get all Plone Sites.
    plones = [
        obj
        for obj in app.objectValues()  # noqa
        if getattr(obj, "portal_type", "") == "Plone Site"
    ]


def commit(note):
    print(note)
    if options.dry_run:
        print("Dry run selected, not committing.")
        transaction.abort()
        return
    # Commit transaction and add note.
    tr = transaction.get()
    tr.note(note)
    transaction.commit()


old_ldap_plugin_id = "ldap-plugin"
new_ldap_plugin_id = "pasldap"
for site in plones:
    if options.verbose:
        print("")
        print("Handling Plone Site %s." % site.id)
    setSite(site)
    pas = api.portal.get_tool("acl_users")
    if old_ldap_plugin_id in pas:
        qi = api.portal.get_tool("portal_quickinstaller")
        qi.uninstallProducts(["plone.app.ldap"])
        commit("Uninstalled old plone.app.ldap.")
    setup = api.portal.get_tool("portal_setup")
    profile_id = "profile-collective.ldapsetup:default"
    installed_version = setup.getLastVersionForProfile(profile_id)
    if installed_version == UNKNOWN:
        setup.runAllImportStepsFromProfile(profile_id)
        commit("Installed new pas.plugins.ldap.")
    elif setup.hasPendingUpgrades(profile_id):
        setup.upgradeProfile(profile_id)
        commit("Upgraded pas.plugins.ldap.")
    if new_ldap_plugin_id not in pas:
        setup.runAllImportStepsFromProfile(profile_id)
        commit("Created new pas.plugins.ldap plugin.")
    if options.uri:
        uri = options.uri
        if ":" not in uri:
            uri = "localhost:{0}".format(uri)
        if not uri.startswith("ldap"):
            uri = "ldaps://{0}".format(uri)
        plugin = pas[new_ldap_plugin_id]
        props = ILDAPProps(plugin)
        if props.uri != uri:
            props.uri = uri
            commit("Set server.uri to {0}".format(uri))

    if options.enable or options.disable:
        # Activate or deactive the plugin for all available plugin types.
        changed = False
        plugin = pas[new_ldap_plugin_id]
        for info in pas.plugins.listPluginTypeInfo():
            interface = info["interface"]
            if not interface.providedBy(plugin):
                continue
            active = plugin.is_plugin_active(interface)
            if options.enable and active:
                # It is already enabled, nothing to do.
                continue
            if options.disable and not active:
                # It is already disabled, nothing to do.
                continue
            changed = True
            if options.enable:
                pas.plugins.activatePlugin(interface, new_ldap_plugin_id)
                pas.plugins.movePluginsDown(
                    interface, [x[0] for x in pas.plugins.listPlugins(interface)[:-1]]
                )
            if options.disable:
                pas.plugins.deactivatePlugin(interface, new_ldap_plugin_id)
        if changed:
            if options.enable:
                commit(
                    "Enabled the LDAP plugin and moved it to the top of all plugin types."
                )
            elif options.disable:
                commit("Disabled the LDAP plugin for all plugin types.")
        elif options.verbose:
            if options.enable:
                commit("LDAP was already enabled.")
            elif options.disable:
                commit("LDAP was already disabled.")

    if options.verbose:
        print("Done.")
