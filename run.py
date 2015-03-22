import requests
import json
import os
import time

from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
app.debug = True

pulp_user = 'admin'
pulp_pass = 'admin'

pulp_api_url = "https://pulpapi"
if "PULPURL" in os.environ:
    pulp_api_url = os.environ['PULPURL']


print "Using Pulp API on " + str(pulp_api_url)  + "/pulp/api"

def _get_repos(base_url):
    global pulp_user
    global pulp_pass
    url = "%s/pulp/api/v2/repositories/?details=true" % (base_url)
    res = requests.get(url, verify=False, auth=(pulp_user, pulp_pass))
    return json.loads(res.text)

def _get_repo(base_url, repo):
    global pulp_user
    global pulp_pass
    options = "limit=1&sort=descending"
    url = "%s/pulp/api/v2/repositories/%s/history/sync/?%s" % (base_url, repo, options)
    res = requests.get(url, verify=False, auth=(pulp_user, pulp_pass))
    return json.loads(res.text)

def _get_packages(base_url, repo_id):
    global pulp_user
    global pulp_pass
    url = "%s/pulp/api/v2/repositories/%s/search/units/" % (base_url, repo_id)
    payload = {
        "criteria": {
            "fields": {
                "unit": [
                    'name',
                    'summary',
                    'version',
                    'release',
                    'epoch',
                    'arch',
                    'filename'
                ]
            },
            "type_ids": [],
        }
    }
    res = requests.post(url, data=json.dumps(payload), verify=False, auth=(pulp_user, pulp_pass))
    return json.loads(res.text) 

def _get_package(base_url, package_id, package_type):
    global pulp_user
    global pulp_pass
    url = "%s/pulp/api/v2/content/units/%s/%s/" % (base_url, package_type, package_id)
    res = requests.get(url, verify=False, auth=(pulp_user, pulp_pass))
    return json.loads(res.text)

def _get_sync(base_url, repo, time_start, time_stop):
    global pulp_user
    global pulp_pass
    url = "%s/pulp/api/v2/repositories/%s/history/sync/?start_date=%s&end_date=%s" % (base_url, repo, time_start, time_stop)
    res = requests.get(url, verify=False, auth=(pulp_user, pulp_pass))
    return json.loads(res.text)

def _get_sync_packages(base_url, repo, time_start, time_stop):
    global pulp_user
    global pulp_pass
    url = "%s/pulp/api/v2/repositories/%s/search/units/" % (base_url, repo)
    payload = {
        "criteria": {
            "type_ids": ["rpm"],
            "fields": {},
            "filters": {
                "unit": {},
                "association": {
                    "created": {
                        "$gte": time_start,
                        "$lte": time_stop
                        }
                    }
                }
            }
        }
    res = requests.post(url, data=json.dumps(payload), verify=False, auth=(pulp_user, pulp_pass))
    return json.loads(res.text) 

@app.route("/")
def index():
    repos = _get_repos(pulp_api_url)
    return render_template('index.html', repos=repos)

@app.route("/repos/<repo_id>")
def repo(repo_id):
    groups = []
    packages = []
    sync_history = _get_repo(pulp_api_url, repo_id)
    units = _get_packages(pulp_api_url, repo_id) 
    for item in units:
        if item['unit_type_id'] == 'package_group':
            groups.append(item)
        else:
            packages.append(item)
    return render_template('repo.html', data={ 'repo': repo_id }, syncs=sync_history, packages=packages, groups=groups)

@app.route("/repos/<repo_id>/sync/")
def sync(repo_id):
    started = request.args.get('started')
    completed = request.args.get('completed')
    sync = _get_sync(pulp_api_url, repo_id, started, completed)
    packages = _get_sync_packages(pulp_api_url, repo_id, started, completed) 
    return render_template('sync.html', details=sync[0], packages=packages)

@app.route("/packages/<package_id>/")
def package(package_id):
    package_type = request.args.get('type')
    if not package_type:
        package_type = 'rpm'
    package = _get_package(pulp_api_url, package_id, package_type)
    return render_template('package.html', package=package)

def nl2br(value): 
    return value.replace('\n','<br>\n')

def epoch2date(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['epoch2date'] = epoch2date

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)
