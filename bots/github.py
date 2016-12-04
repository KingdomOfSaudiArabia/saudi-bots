# this code by JeffPaine modified by kaluaim
import os
import inspect
import configparser
import json
import requests

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
configfile = os.path.join(path, 'bots.config')
config = configparser.SafeConfigParser()
config.read(configfile)

# Authentication for user filing issue (must have read/write access to
# repository to add issue to)
USERNAME = config.get('King', 'github_username')
PASSWORD = config.get('King', 'github_password')
REPO_OWNER = 'KingdomOfSaudiArabia'

def make_issue(repo, title, body=None, assignee=None, milestone=None, labels=[]):
    '''Create an issue on github.com using the given parameters.'''
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, repo)
    # Create an authenticated session to create the issue
    session = requests.session()
    session.auth = (USERNAME, PASSWORD)
    # Create our issue
    issue = {'title': title,
             'body': body,
             'assignee': assignee,
             'milestone': milestone,
             'labels': labels}
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print('Successfully created Issue "%s"' % title)
    else:
        print('Could not create Issue "%s"' % title)
        print('Response:', r.content)
