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

conn.execute("""
    DELETE FROM ckan_dataset
""")

cursor = conn.execute("""
    SELECT id, nazov
    FROM dataset
    ORDER BY id
""")

for dataset_id, title in cursor:
    print("Searching for %s" % (title,))
    # TODO: try to search by notes as well to improve matches.
    res = ckan_call_api('search/dataset', q=title.replace(':', ''),
                        limit=20)

    if res is None:
        print("Skipping, error on request.")
        continue
    if res['count'] == 0:
        print("Nothing found.")
        continue

    found = False
    candidates = []
    for candidate in res['results']:
        candidate_info = ckan_call_api('rest/dataset/%s' % (candidate,),
                                       limit=20)
        if candidate_info['title'] == title:
            print("Found match: %s" % (candidate,))
            found = (candidate_info['id'], candidate, dataset_id)
            break
        else:
            candidates.append((candidate_info['title'],
                               candidate_info['id'],
                               candidate, dataset_id))

    if (not found and candidates):
        for i, c in enumerate(candidates):
            print("% 13d %s" % (i, c[0]))
        answer = raw_input("Any candidate correct? ")
        try:
            i = int(answer)
            found = candidates[i][1:]
            print("Accepting %s" % (candidates[i][0],))
        except (ValueError, IndexError):
            print("Skipping.")

    if found:
        conn.execute("""
            INSERT INTO ckan_dataset VALUES (?,?,?)
        """, (
            candidate_info['id'],
            candidate,
            dataset_id,
        ))
    else:
        # TODO: mark those without a match
        pass
