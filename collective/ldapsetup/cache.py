# -*- coding: utf-8 -*-
from pas.plugins.ldap.interfaces import ICacheSettingsRecordProvider
from pas.plugins.ldap.plonecontrolpanel.cache import CacheSettingsRecordProvider
from plone.registry import Record
from zope.interface import implementer

import logging
import os


logger = logging.getLogger(__name__)
CACHE_ENV_VAR = "PAS_PLUGINS_LDAP_MEMCACHE"
MEMCACHE_SERVERS = os.getenv(CACHE_ENV_VAR, "").strip()


class EnvRecord(object):
    # servers, delimited by space
    value = MEMCACHE_SERVERS


if MEMCACHE_SERVERS:
    logger.info("Using memcache servers from %s variable: %s", CACHE_ENV_VAR, MEMCACHE_SERVERS)
    CACHE_RECORD = EnvRecord()
else:
    CACHE_RECORD = None


@implementer(ICacheSettingsRecordProvider)
class CollectiveCacheSettingsRecordProvider(CacheSettingsRecordProvider):
    def __call__(self):
        if CACHE_RECORD is not None:
            return CACHE_RECORD
        # Return value from registry as usual.
        return super(CollectiveCacheSettingsRecordProvider, self).__call__()
