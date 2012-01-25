import re
import urllib2
import functools
from copy import copy
from pygments import lexers, formatters, highlight

from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.test.client import Client
from django.utils import simplejson

import apiserver as api
from apiserver.explorer.forms import RequestForm


def get_base_uris(base):
    content = web.get(base).content
    data = simplejson.loads(content)
    return data


class APIRequest(object):
    HEADERS = {
        "HTTP_CONTENT_TYPE": "application/json",
        "HTTP_ACCEPT": "application/json",
        }

    web = Client()
    web.put = functools.partial(web.post, REQUEST_METHOD='PUT')

    def __init__(self, endpoint, user=None):
        self.headers = copy(self.HEADERS)

        if user:
            self.headers["HTTP_AUTHORIZATION"] = api.utils.create_auth_string(*user)

    def do(self, method, endpoint, data='', content_type='application/json', headers={}):
        response = getattr(self.web, method)(endpoint, data=data, content_type=content_type, **headers)
        return response, response.status_code

    # TODO
    def as_curl(self):
        return """curl http://{path}{endpoint} \
            --request {method|upper} \
            --header 'Content-Type: application/json' \{% if data %}
            --data '{data}' \{% endif %}
            --user {username}:{password}""".format(self.__dict__)


class Explorer(api.Resource):
    class Meta:
        route = '/explorer'

    def get_users(self):
        """
        If you provide some dummy users from which users may select, you can specify
        those by overriding this method and returning a list of usernames.
        (They'll still have to fill out the password field.)
        """
        return []

    def post(self, request, filters, format):
        return self.show(request, filters, format)

    def show(self, request, filters, format):
        if request.POST:
            form = RequestForm(request.POST)
            if form.is_valid():
                method = form.cleaned_data['method']
            else:
                method = "get"
        else:
            form = RequestForm()
            method = "get"

        post_endpoint = request.POST.get("endpoint", False)
        querystring_endpoint = request.GET.get("endpoint", "/v1")
        endpoint = post_endpoint or querystring_endpoint
        form.fields.get('endpoint').initial = endpoint

        headers = copy(HEADERS)

        default_user = False
        if default_user:
            user = form.data.get("user", default_user[0])
            pwd = test_users[user]
            headers["HTTP_AUTHORIZATION"] = create_auth_string(user, pwd)
        else:
            user = "anonymous user"

        print "Relaying {method} request for {user} to {endpoint}".format(user=user, endpoint=endpoint, method=method.upper())

        response = getattr(web, method)(endpoint, data=form.data.get('data', ''), content_type='application/json', **headers)
        status_code = response.status_code
        try:
            response = prettify(response.content)
        except simplejson.JSONDecodeError:
            response = response.content

        return direct_to_template(request, "explorer.html", {
            "starting_points": get_base_uris('/v1'),
            "path": request.META["HTTP_HOST"],
            "endpoint": endpoint,
            "form": form,
            "headers": headers,
            "status": status_code,
            "response": response,
            "method": method,
            "username": user,
            #"password": get_password(user),
            "data": form.data.get("data", ""),
            "curl": request.as_curl(),
            })
