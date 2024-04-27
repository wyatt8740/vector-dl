#! /usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import re
import sys
import os

toplevel_path=os.getcwd()

def getPage(url):
  response = requests.get(url);
  # hardcoding... maybe there's a way to extract the encoding from the head?
  response.encoding='shift_jis'
  return response.text

#################################
# CLI ARGS
#################################

def add_flag(flag_dict, flag_name, flag_val):
  flag_dict.update({ str(flag_name).lower() : flag_val })

def parse_flag( arg, maybe_more_flags=True):
  if not(maybe_more_flags):
    return False
  elif arg == '--':
    return True
  elif arg.startswith("--"):
    flag = arg.rpartition('--')[2].rpartition('=')
    if flag[0] == '' and flag[1] == '':
      flag=(flag[2], '=', True)
    return flag
  return False

def get_flag(flag_dict, name, default_value=None):
  if type(flag_dict) is None:
    return default_value
  name=name.lower()
  value=flag_dict.get(name)
  if value is None:
    return default_value
  else:
    return value

#################################

# download a file from a given 'description' page. example:
# https://www.vector.co.jp/soft/dos/hardware/se000298.html
def dl_top(url, title=None):
  url=re.sub(r"www\.vector\.co\.jp/soft/", "www.vector.co.jp/soft/dl/", url)
  # software name (se* prefix) will become a subdirectory under toplevel_path
  soft_dir_name = toplevel_path + '/' + re.sub("\.html$","",re.sub(r"^.*/","",url))
  # create directory to dump our files in
  os.makedirs(soft_dir_name, exist_ok=True)

  # version specific download page links have to be extracted from this page
  # example link:
  # https://www.vector.co.jp/download/file/dos/hardware/fh000303.html
  document=getPage(url)
  soup=BeautifulSoup(document, 'html.parser')
  # a download page can have multiple available software versions
  version_links=soup.find_all('a', class_=["btn download"])

  i=0
  for dlpage_link in version_links:
    # 'CD-SD STD(8→8A 差分)'
    file_description_name=soup.select("tbody tr td strong.fn")[i].contents[0]
    # '8A'
    file_description_version=soup.select("tbody tr td strong.fn")[i].contents[1].text
    # i don't have a good way to know which file gets which "additional info"
    # field, since not all files have this field at all
    #file_description_additional_info=soup.select(".add")
    dl_version_page('https://www.vector.co.jp' + dlpage_link['href'],
                    soft_dir_name,
                    desc_name=file_description_name,
                    desc_ver=file_description_version)
    # on next run, we will use the next table row, which contains version info
    # for the next file
    i+=1
  return 0

# download page for an individual 'version' of a program
def dl_version_page(url, dlpage_dir="./", desc_name="", desc_ver=""):
  # currently desc_name and desc_ver are unused but they could be stored as metadata
  if desc_name is None:
    desc_name=""
  if desc_ver is None:
    desc_ver=""

  document=getPage(url)
  soup=BeautifulSoup(document, 'html.parser')
  dl_url=soup.select('#summary a')
  if dl_url:
    dl_url=dl_url[0]
    if dl_url['href']:
      dl_url=dl_url['href']
    dl_base_filename=re.sub(r"^.*/","",dl_url) # remove up to last forward slash in url
    filename = dlpage_dir + '/' + dl_base_filename
    file_request=requests.get(dl_url, allow_redirects=True)
    print(filename)
    with open(filename, 'wb') as file:
      file.write(file_request.content)
  else:
    print("ERROR: Could not extract a URL on a final download page.")
  

i=1
urls = [ ]
while i < len(sys.argv):
  if sys.argv[i].startswith("--") and sys.argv[i] != "--":
    i+=1
  elif sys.argv[i] == "--":
    i+=1
    break
  else:
    break

# i now contains index of first url

j=len(sys.argv) - 1
while i <= j:
  urls.append(sys.argv[i])
  i+=1

print("URLs: " + str(urls))
# urls now contains a list of all urls to work on
for url in urls:
  # do the download
  dl_top(url)
  