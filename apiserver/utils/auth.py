# encoding: utf-8

import base64


def create_auth_string(username, password):
    credentials = base64.encodestring("%s:%s" % (username, password)).rstrip()
    auth_string = 'Basic %s' % credentials
    return auth_string