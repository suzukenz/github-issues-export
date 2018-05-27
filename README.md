# Github Issues Exporter

simple command tool that outputs Github's issues as json or csv.

## Prerequisites
require `Python 3.x` and recommend `pipenv`

## Installing
```
pipenv install
```

## Usage

```
pipenv shell
./github_issues_export.py owner repo options...
```
or
```
pipenv run start owner repo options...
```

## options
```
usage: github_issues_export.py [-h] [--csv] [--count] [--token TOKEN]
                               [-s {open,closed,all}] [-l LABELS]
                               [-m MILESTONE] [-a ASSIGNEE]
                               owner repo

github issues export tool

positional arguments:
  owner                 owner of the github repository
  repo                  repository name

optional arguments:
  -h, --help            show this help message and exit
  --csv                 get issues as csv (default: false, return as json)
  --count               get only count (default: false)
  --token TOKEN         github auth token (for authentication required)
  -s {open,closed,all}, --state {open,closed,all}
                        the state of the issues (open||closed||all)
  -l LABELS, --labels LABELS
                        A list of comma separated label names
  -m MILESTONE, --milestone MILESTONE
                        specify milestone number (number is on web url). or
                        '*' specified, return issues that any milestone are
                        setted. If 'none' is specified, issues without
                        milestones are returned.
  -a ASSIGNEE, --assignee ASSIGNEE
                        Can be the name of a user. Pass in none for issues
                        with no assigned user, and * for issues assigned to
                        any user.
```

## License
Unlicense