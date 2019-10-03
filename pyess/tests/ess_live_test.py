#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import pytest
import json
import re
import os

from uuid import UUID

from pyess.constants import GRAPH_DEVICES, GRAPH_TIMESPANS, GRAPH_TFORMATS, STATE_URLS

from pyess.ess import find_all_esses, get_ess_pw, autodetect_ess, ESS


def parses_as_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID("{" + uuid_to_test + "}", version=version)
    except ValueError:
        return False
    return True


@pytest.fixture()
def password():
    return json.load(open(os.path.dirname(__file__) + "/credentials.json"))["password"]


@pytest.fixture()
def test_ess(cache=[]):
    if not cache:
        ip, name = autodetect_ess()
        cache.append(ip)
        cache.append(name)
    return cache


@pytest.fixture()
def ess(test_ess, password):
    return ESS(test_ess[1], password)


@pytest.mark.vcr()
def test_init(password, test_ess):
    ess = ESS(test_ess[1], password)


@pytest.mark.vcr()
def test_get_password(test_ess):
    # assuming we are not on ess' wifi
    with pytest.raises(Exception):
        pw = get_ess_pw(test_ess[0])


# def test_get_state/

@pytest.mark.vcr()
@pytest.mark.parametrize('dev,timespan', [(d, t) for d in GRAPH_DEVICES for t in GRAPH_TIMESPANS])
def test_get_graph(ess, dev, timespan):
    res = ess.get_graph(dev, timespan, datetime.datetime.now())
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + dev + "_" + timespan + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict) and not key == "loginfo"]:
        for k in example[key].keys():
            assert k in res[key]


@pytest.mark.vcr()
@pytest.mark.parametrize("state", [(k) for k in STATE_URLS.keys()])
def test_get_state(ess, state):
    res = ess.get_state(state)
    example = json.load(open(os.path.dirname(__file__) + "/examples/" + state + ".json", "r"))
    for key in example.keys():
        assert key in res
    for key in [k for k in example.keys() if isinstance(example[k], dict)]:
        for k in example[key].keys():
            assert k in res[key]