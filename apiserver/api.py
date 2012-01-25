import inspect
import types

from django.conf import settings
from django.conf.urls.defaults import patterns, url, include

# original imports in tastypie.api
import warnings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from apiserver.exceptions import NotRegistered
from apiserver.serializers import Serializer
from apiserver.utils import is_valid_jsonp_callback_value
from apiserver.utils.mime import determine_format, build_content_type
from apiserver.resources import Resource
from apiserver import decorators


class API(object):
    def __init__(self, version=''):
        self.urlconf = []
        self.patterns = []
        self.version = '^' + version.rstrip('/')

    # canonical only for parity with tastypie, doesn't currently do anything
    def register(self, module, canonical=True):
        if isinstance(module, dict):
            resources = module.values()
        elif isinstance(module, list):
            resources = module
        elif isinstance(module, types.ModuleType):
            resources = [obj for name, obj in inspect.getmembers(module)
                if inspect.isclass(obj)
                and issubclass(obj, Resource)]
        elif issubclass(module, Resource):
            resources = [module]
        else:
            raise Exception("API can only register dictionaries, lists, modules or individual resources.")

        for resource in resources:
            instance = resource()

            # catch all errors that, thus far, haven't been caught
            if not getattr(settings, 'APISERVER_FULL_DEBUG', False):
                # TODO: log the full exception somewhere
                decorators.on_error(NotImplementedError, 501).decorate_cls(instance)
                decorators.on_error(BaseException, 500).decorate_cls(instance)

            # in special cases, specifically when somebody needs a detail view
            # but not a collection view, a resource can be routeless
            if instance._meta.parsed_route:
                self.patterns.append(url(instance._meta.parsed_route, instance.dispatch, name=instance.name))

        self.urlconf += patterns('', (self.version, include(self.patterns)))

    def unregister(self, resource_name):
        """
        If present, unregisters a resource from the API.
        """
        raise NotImplementedError()

    def canonical_resource_for(self, resource_name):
        """
        Returns the canonical resource for a given ``resource_name``.
        """
        raise NotImplementedError()

    # see sketch.py -- we might want to do this differently from tastypie,
    # relying more on decorators... not sure though
    def wrap_view(self, view):
        raise NotImplementedError()

    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all resources registers
        to the ``Api``. Useful for discovery.
        """
        raise NotImplementedError()
