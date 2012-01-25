from apiserver.api import API
from apiserver.explorer import Explorer
from apiserver.resources import TOC

from organization import resources


class TOCResource(TOC):
    class Meta:
        route = ''
        resources = [
            resources.OrganizationCollection,
            resources.PersonCollection,
        ]

v1 = API(version='v1')
v1.register(TOCResource)
v1.register(resources)
v1.register(Explorer)

urlpatterns = v1.urlconf
