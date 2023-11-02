#!/usr/bin/env python
'''
get_latest_release.py environment.yml

Requires 'mamba' and 'jq' to query conda-forge metadata
'''
import yaml
import sys
import asyncio
from datetime import datetime
import pandas as pd
import numpy as np
import json
from packaging.version import parse as parseVersion

#envfile = sys.argv[1]
envfile = 'pangeo-notebook/environment.yml'

loop = asyncio.get_event_loop()

async def run(cmd):
    # https://docs.python.org/3/library/asyncio-subprocess.html
    print(cmd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return json.loads(stdout)

async def main(coros):
    results = await asyncio.gather(*coros)
    return results

def get_release_date(metadata):
  ''' for list of json metadatas, return date of most recent conda-forge package version '''
  print(metadata)
  timestamps = np.array([x['timestamp'] for x in metadata])
  timestamps[::-1].sort()
  latest = datetime.utcfromtimestamp(timestamps[0]).strftime('%Y-%m-%d')
  return latest 

def get_version(metadata):
  ''' for list of json metadatas, return list of build strings for package version '''
  versions = [x['version'] for x in metadata]
  versions.sort(key=parseVersion, reverse=True)
  return versions[0]

def get_python_dependency(metadata, version='latest'):
  ''' for list of json metadatas, return list of build strings for package version '''
  if version == 'latest':
    verid = get_version(metadata)
  else:
    verid = version
  metadata = [x for x in metadata if x['version']==verid]
  builds = set([y for x in metadata for y in x['depends'] if y.startswith('python ')])
  #builds = set([x['build_string'] for x in metadata])
  return builds

coros = []
with open(envfile, 'r') as f:
  data = yaml.safe_load(f)
  packages = data['dependencies']
  print(f'Fetching latest release conda-forge metadata for {len(packages)} packages...')
  for i,package in enumerate(packages):
    # JQ sorting and groupby by strings is tricky, so just return top 'N' and do the rest in python
    #cmd = f"""mamba repoquery search -p linux-64 "{package}" --json | jq '.result["pkgs"][:10] | group_by(.version)[-1]'"""
    #Get most recent 10 builds of all releases
    cmd = f"""mamba repoquery search "{package}" --json | jq '.result["pkgs"][:10]'""" 
    coros.append(run(cmd))

# Async requests to retrieve metadata
results = loop.run_until_complete(main(coros))

# Serial computations on retrieved metadata
#latest_versions = [get_version(r) for r in results]
releases = [get_release_date(r) for r in results]
#python_builds = [get_python_dependency(r) for r in results]
#df = pd.DataFrame(dict(package=packages, version=latest_versions, release=releases, python=python_builds))
df = pd.DataFrame(dict(package=packages, release=releases))
print(df.sort_values('release').to_string(index=False)) 