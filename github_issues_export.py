#!/usr/bin/env python
import argparse
import json
import csv
from io import StringIO

import requests
from requests.exceptions import RequestException


# issue fields
NUMBER = 'number'
TITLE = 'title'
STATE = 'state'
ASSIGNEES = 'assignees'
MILESTONE = 'milestone'
LABELS = 'labels'
CREATED_AT = 'created_at'
UPDATED_AT = 'updated_at'
URL = 'html_url'

# In the github api spec, default: 30, max: 100
REQ_PER_PAGE = 100


class Issues:
    def __init__(self, raw_issues):
        # todo: enable filter keys
        self.disp_fields = [
            NUMBER,
            TITLE,
            STATE,
            ASSIGNEES,
            MILESTONE,
            LABELS,
            CREATED_AT,
            UPDATED_AT,
            URL,
        ]
        self.data = [
            {
                # filter dict fields
                k: v for k, v in raw_issue.items() if k in self.disp_fields
            } for raw_issue in raw_issues if 'pull_request' not in raw_issue
        ]

    def count(self):
        return len(self.data)

    def print_as_json(self):
        print(json.dumps(self.data, indent=2))

    def print_as_csv(self):
        s = StringIO()
        writer = csv.writer(
            s, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        # header row
        writer.writerow(self.disp_fields)
        for issue in self.data:
            row = [self.parse_value(k, issue.get(k)) for k in self.disp_fields]
            writer.writerow(row)
        print(s.getvalue(), end='')
        s.close()

    @staticmethod
    def parse_value(field_name, value):
        if not value:
            return ''
        if field_name == ASSIGNEES:
            assignees = [assignee.get('login') for assignee in value]
            return ', '.join(assignees)
        elif field_name == MILESTONE:
            return value.get('title', '')
        elif field_name == LABELS:
            label_names = [label.get('name') for label in value]
            return ', '.join(label_names)
        else:
            return value


def request_issues_api(owner, repo, options={}):
    # ref: https://developer.github.com/v3/issues/#list-issues-for-a-repository
    req_url = 'https://api.github.com/repos/{}/{}/issues'.format(
        owner, repo
    )
    headers = {
        'Authorization': 'token ' + options['token']
    } if options.get('token', False) else {}

    filters = {
        'state': options.get('state', False),
        'labels': options.get('labels', False),
        'milestone': options.get('milestone', False),
        'assignee': options.get('assignee', False)
    }
    params = {k: v for k, v in filters.items() if v}
    params['per_page'] = REQ_PER_PAGE

    res_issues = []
    page = 1
    while True:
        res = requests.get(req_url, headers=headers, params=params)

        # handle response statuses
        code = res.status_code
        if code != 200:
            if code == 404:
                print('error: 404 not found.')
            else:
                print(res.json().get('message'))
            res.raise_for_status()

        res_issues.extend(res.json())
        # pagination
        link = res.headers.get('Link', False)
        if link and 'rel="next"' in link:
            page = page + 1
            params['page'] = page
        else:
            break

    return res_issues


def setup_arg_parser():
    parser = argparse.ArgumentParser(description='github issues export tool')
    parser.add_argument('owner', help='owner of the github repository')
    parser.add_argument('repo', help='repository name')
    parser.add_argument(
        '--csv', action='store_true', default=False,
        help='get issues as csv (default: false, return as json)'
    )
    parser.add_argument(
        '--count', action='store_true', default=False,
        help='get only count (default: false)'
    )
    parser.add_argument(
        '--token',
        help='github auth token (for authentication required)'
    )
    parser.add_argument(
        '-s', '--state', choices=['open', 'closed', 'all'], default='open',
        help='the state of the issues (open||closed||all)'
    )
    parser.add_argument(
        '-l', '--labels', help='A list of comma separated label names'
    )
    parser.add_argument(
        '-m', '--milestone',
        help='''
            specify milestone number (number is on web url).
            or '*' specified, return issues that any milestone are setted.
            If 'none' is specified, issues without milestones are returned.
        '''
    )
    parser.add_argument(
        '-a', '--assignee',
        help='''
            Can be the name of a user.
            Pass in none for issues with no assigned user,
            and * for issues assigned to any user.
        '''
    )
    return parser


def main():
    arg_parser = setup_arg_parser()
    args = arg_parser.parse_args()

    options = {
        'token': args.token,
        'state': args.state,
        'labels': args.labels,
        'milestone': args.milestone,
        'assignee': args.assignee
    }

    res_issues = {}
    try:
        res_issues = request_issues_api(args.owner, args.repo, options)
    except RequestException as _:
        print('failed to request github api')
        return

    issues = Issues(res_issues)

    if args.count:
        print(issues.count())
        return
    if issues.count() == 0:
        print('nothing result.')
        return

    # out issues
    if args.csv:
        issues.print_as_csv()
    else:
        issues.print_as_json()


if __name__ == '__main__':
    main()
