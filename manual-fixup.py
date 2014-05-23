#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

import json
import posixpath
import sqlite3
import sys
import traceback

try:
    import readline
except ImportError:
    pass

import requests


CKAN_API_BASE = 'http://data.gov.sk/api/1'


def prettyprint(data):
    print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))


def ckan_call_api(method, **kwargs):
    url = posixpath.join(CKAN_API_BASE, method)
    r = requests.get(url, params=kwargs)
    try:
        return r.json()
    except Exception as e:
        traceback.print_exc()
        print(r)
        print(r.headers)
        print(r.content)


conn = sqlite3.connect('datasety.db')

conn.isolation_level = None

cursor = conn.execute("""
    SELECT ckan_id, ckan_name, dataset_id, nazov
    FROM ckan_dataset
        INNER JOIN dataset ON (ckan_dataset.dataset_id = dataset.id)
    WHERE ckan_id IS NULL
       OR ckan_name IS NULL
    ORDER BY dataset_id
""")

for ckan_id, ckan_name, dataset_id, title in cursor:
    print("Searching for dataset %d: %s" % (dataset_id, title))
    identifier = ckan_id or ckan_name or raw_input("Dataset name: ")
    if not identifier:
        continue

    res = ckan_call_api('rest/dataset/%s' % (identifier,))

    if res is None:
        print("Skipping, error on request.")
        continue

    new_ckan_id = res['id']
    new_ckan_name = res['name']
    conn.execute("""
        UPDATE ckan_dataset
        SET ckan_id=?,
            ckan_name=?
        WHERE dataset_id=?
    """, (
        new_ckan_id,
        new_ckan_name,
        dataset_id,
    ))
