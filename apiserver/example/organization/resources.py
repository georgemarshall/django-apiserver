"""
Visit these URLs to see how it works:
- /organizations.json
- /organizations/acme/people.json
- /organizations/ACME/people/1.json
- /organizations/REX/people/2.json

Differences from Tastypie
- url routing is entirely manual, no magic
- show/create/update/destroy methods (stolen from Rails)
  that return a data structure (e.g. a dict)
- separate collection resources
- no ?format arg, but .<format> appended to routes
  (Although using Accepts should still be encouraged.)

Any other differences (e.g. no Meta, no hydrate/dehydrate)
purely for the sake of being able to quickly put together
a prototype.
"""
import apiserver as api
from django_filters import FilterSet

from .models import Person, Organization


# regular resource
class MessageResource(api.Resource):
    class Meta:
        route = '/messages/<name:s>'

    def show(self, request, filters, format):
        name, filters = api.utils.extract('name', filters)
        return {'message': 'hello there %s' % name}


# regular model resource
class PersonResource(api.ModelResource):
    class Meta:
        route = '/everybody/<pk:#>'
        queryset = Person.objects.all()


class PersonCollection(api.ModelCollection, PersonResource):
    class FilterSet(FilterSet):
        class Meta:
            model = Person

    class Meta(PersonResource.Meta):
        route = '/everybody'


# model resource
class OrganizationResource(api.ModelResource):
    people = api.fields.ToManyField('organization.resources.PersonResource', 'people')

    class Meta:
        route = '/organizations/<name:s>'
        queryset = Organization.objects.all()

    def show(self, request, filters, format):
        name, filters = api.utils.extract('name', filters)
        filters['name'] = name.upper()
        return super(OrganizationResource, self).show(request, filters, format)


# collection resource
class OrganizationCollection(api.ModelCollection, OrganizationResource):
    class FilterSet(FilterSet):
        class Meta:
            model = Organization
            fields = ['name']

    class Meta(OrganizationResource.Meta):
        route = '/organizations'

    def show(self, request, filters, format):
        # testing whether we couldn't decide full=True on the fly, rather than on a per-class level
        #
        # for field in self.base_fields.values():
        #     field.full = True
        return super(Organizations, self).show(request, filters, format)


# here solely to test OPTIONS
@api.only('show', 'destroy')
class OrganizationsOptions(OrganizationCollection):
    class Meta(OrganizationCollection.Meta):
        route = '/organization_options'

    def show(self, request, filters, format):
        return OrganizationCollection.options(self, request, filters, format)


# deep model resource
class PeopleResource(api.ModelResource):
    organization = api.fields.ToOneField(OrganizationResource, 'organization')

    class Meta:
        route = '/organizations/<organization__name:s>/people/<pk:#>'
        queryset = Person.objects.all()

    # shows how you could customize the args or do other wacky things
    #
    # this example transforms the filter args, and uppercases the org name
    # before handing it off
    def show(self, request, filters, format):
        organization, filters = api.utils.extract('organization__name', filters)
        filters['organization__name'] = organization.upper()
        return super(PeopleResource, self).show(request, filters, format)


# deep collection resource
class PeopleCollection(api.ModelCollection, PeopleResource):
    class Meta(PersonResource.Meta):
        route = '/organizations/<organization__name:s>/people'

    def show(self, request, filters, format):
        organization, filters = api.utils.extract('organization__name', filters)
        filters['organization__name'] = organization.upper()
        return super(PeopleCollection, self).show(request, filters, format)
