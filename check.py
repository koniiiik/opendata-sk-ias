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
two_star = ['xls']

def translate(ext, mime_type=None):
  if ext == 'wsdl':
    return 'xml'
  return ext

all_formats = two_star + three_star + four_star

def get_file_ext(mime_type, url, cont_disp):
  ext = None
  if cont_disp != None:
    ext = cont_disp.split("filename=")[1].strip('\'"')
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

conn = sqlite3.connect('datasety.db')

conn.isolation_level = None

req = requests.get('http://data.gov.sk/api/1/rest/dataset')
assert req.status_code == requests.codes.ok

response_dict = req.json()

for ds_name in response_dict:
  req1 = requests.get('http://data.gov.sk/api/1/rest/dataset/' + ds_name)
  dataset = req1.json()
  ds_id = dataset['id']
  resources = dataset['resources'] 
  for ds_metadata in resources:
    url =  ds_metadata['url'] # id, name, 
    req2 = requests.get(url)
    headers = req2.headers
    content_type = headers['Content-Type']
    mime_type = content_type.split(';')[0]
    cont_disp = None
    if 'content-disposition' in headers:
      cont_disp = headers['content-disposition']
    #~ else:
      #~ print(req2.url.split('.')[-1])
    if (req2.status_code != requests.codes.ok):
      print (FAIL + "ERR (" + str(req2.status_code) + ")" + ENDC + " pre dataset:" + ds_name + ", url=" + url)
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
        print (FAIL + "NOT A DATASET" + ENDC + " pre dataset:" + ds_name + ", url=" + url)
        conn.execute("""
          INSERT into ckan_resource VALUES (?,?,?,?,?,?,?)
          """,(
           ds_id, 
           ds_name,
           "NOT A DATASET",
           url,
           0,
           None,
           mime_type
        ))
      else:
        ext = get_file_ext(mime_type, req2.url, cont_disp)
        stars = ohodnot(ext)
        print (OK + "OK" + ENDC + " pre dataset:" + ds_name + " ext:" + ext + " stars:"+ str(stars))
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
