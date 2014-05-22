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
    SELECT id, nazov
    FROM dataset
    WHERE NOT EXISTS (
        SELECT *
        FROM ckan_dataset
        WHERE ckan_dataset.dataset_id = dataset.id
    )
    ORDER BY id
""")

for dataset_id, title in cursor:
    print("Searching for %s; id=%d" % (title, dataset_id))
    # TODO: try to search by notes as well to improve matches.
    res = ckan_call_api('search/dataset', q=title.replace(':', ''),
                        limit=20, all_fields=1)

    if res is None:
        print("Skipping, error on request.")
        continue

    found = False

    if res['count'] == 0:
        print("Nothing found.")

    candidates = []
    for candidate in res['results']:
        candidate_info = json.loads(candidate['data_dict'])
        if candidate_info['title'] == title:
            print("Found match: %s" % (candidate_info['name'],))
            found = (candidate_info['id'], candidate_info['name'], dataset_id)
            break
        else:
            candidates.append((candidate_info['title'],
                               candidate_info['id'],
                               candidate_info['name'], dataset_id))

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

    if not found:
        found = (None, None, dataset_id)

    conn.execute("""
        INSERT INTO ckan_dataset VALUES (?,?,?)
    """, found)
