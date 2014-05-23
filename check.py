#!/usr/bin/env python

import requests
import sqlite3
import mimetypes

# * - existuje
# ** - strojo-spracovatelne = xls
# *** - csv, xlsx, 
# **** - rdf 

four_star = ['rdf']
three_star = ['xml', 'xsd', 'csv']
two_star = ['xls', 'xlsx']
one_star = ['doc', 'pdf', 'zip', 'gz', 'txt', 'docx', 'rtf'] # to je nadmnozina toho, co realne je teraz v tych datasetoch

def translate(ext, mime_type=None):
  if ext == 'wsdl':
    return 'xml'
  return ext

all_formats = one_star + two_star + three_star + four_star

def get_file_ext(mime_type, url, cont_disp):
  ext = None
  if cont_disp != None:
    filename = cont_disp.split("filename=")[1].strip('\'"')
    ext = filename.split('.')[-1]
    if ext in all_formats:
      return ext
  ext = url.split('.')[-1]
  if ext in all_formats:
    return ext
  ext = mimetypes.guess_extension(mime_type)
  if ext != None:
    ext = ext.strip('.')
  else:
    ext = ''
  return translate(ext)
  
def ohodnot(ext):
  if ext in four_star:
    return 4
  if ext in three_star:
    return 3   
  if ext in two_star:
    return 2
  return 1
  

#some colors
OK = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

use_db= True
conn = None

if use_db:
  conn = sqlite3.connect('datasety.db')
  conn.isolation_level = None
  conn.execute("delete from ckan_resource;")

req = requests.get('http://data.gov.sk/api/1/rest/dataset')
assert req.status_code == requests.codes.ok

response_dict = req.json()

bad_datasets = ['register-obhospodarovatelov-lesa', # bad url - http:/g ...
'digitalna-mapa-skol', # Incomplete read
'naplnenost-skol-a-moznosti-studia' # Incomplete read
]

for ds_name in response_dict:
  if ds_name in bad_datasets:
    continue
  req1 = requests.get('http://data.gov.sk/api/1/rest/dataset/' + ds_name)
  dataset = req1.json()
  ds_id = dataset['id']
  resources = dataset['resources'] 
  for ds_metadata in resources:
    url =  ds_metadata['url'] # id, name, 
    #~ print(ds_name, url)
    req2 = requests.get(url)
    print(req2.is_redirect, req2.history)
    headers = req2.headers
    content_type = headers['Content-Type']
    mime_type = content_type.split(';')[0]
    cont_disp = None
    lower_headers = {k.lower():v for k,v in headers.items()}
    if 'content-disposition' in lower_headers:
      cont_disp = lower_headers['content-disposition']
    #~ print(req2.url)
    if (req2.status_code != requests.codes.ok):
      print (FAIL + "ERR (" + str(req2.status_code) + ")" + ENDC + " pre dataset:" + ds_name + ", url=" + url)
      if use_db:
        conn.execute("""
          INSERT into ckan_resource VALUES (?,?,?,?,?,?,?)
          """,(
           ds_id, 
           ds_name,
           "ERR (" + str(req2.status_code) + ")",
           url,
           0,
           None,
           mime_type
        ))
    else:
      if 'text/html' in content_type:
        if len(req2.history) > 0:
          err_c = "REDIRECT"
        else:
          err_c = "WEB FORM?"
        print (FAIL + err_c + ENDC + " pre dataset:" + ds_name + ", url=" + url)
        if use_db:
          conn.execute("""
            INSERT into ckan_resource VALUES (?,?,?,?,?,?,?)
            """,(
             ds_id, 
             ds_name,
             err_c,
             url,
             0,
             None,
             mime_type
          ))
      else:
        ext = get_file_ext(mime_type, req2.url, cont_disp)
        stars = ohodnot(ext)
        print (OK + "OK" + ENDC + " pre dataset:" + ds_name + " ext:" + ext + " stars:"+ str(stars))
        if use_db:
          conn.execute("""
            INSERT into ckan_resource VALUES (?,?,?,?,?,?,?)
            """,(
             ds_id, 
             ds_name,
             "OK",
             url,
             stars,
             ext,
             mime_type
          ))
