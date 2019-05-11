import argparse
import os
import re
import requests
import sys
import time

from operator import itemgetter


class SubmissionDownloader:
    BASE_URL = 'https://dmoj.ca/src/{sub_id}/raw'
    SUBMISSION_URL = 'https://dmoj.ca/problem/{problem_code}/submissions/{page_num}'
    # delay between requests
    REQUEST_DELAY = 1
    # when self.best_only = True, store the best submission based on this order
    ORDER = ['AC', '_AC', 'WA', 'TLE', 'MLE', 'OLE', 'IR', 'RTE', 'CE', 'IE', 'AB']
    reid = re.compile(r'<tr id="(\d*)">\n<td class="sub-result (\w*)">.*?<a href="/user/(\w*)">', re.DOTALL)

    def __init__(self, problem_code, cookies, best_only, echo=print):
        self.code = problem_code
        self.cookies = cookies
        self.best_only = best_only
        self.ids = []
        self.echo = echo

    def request(self, url):
        ret = requests.get(url, cookies=self.cookies)
        time.sleep(self.REQUEST_DELAY)
        return ret

    def get_submission_ids(self):
        # keep going until 404
        page_num = 1
        while True:
            request = self.request(self.SUBMISSION_URL.format(problem_code=self.code, page_num=page_num))
            if request.status_code != 200:
                break
            self.echo('Downloaded page {}'.format(page_num))
            self.ids.extend(self.reid.findall(request.text))
            page_num += 1
        self.echo('Downloaded {} page(s) of {} submission(s).'.format(page_num - 1, len(self.ids)))

        self.ids = [(sub[0], self.ORDER.index(sub[1]), sub[2]) for sub in self.ids]

        if self.best_only:
            self.echo('Parsing submissions and only storing best...')
            user_mp = {}
            for sub in self.ids:
                try:
                    user_mp[sub[2]] = min(user_mp[sub[2]], (sub[1], sub[0]))
                except KeyError:
                    user_mp[sub[2]] = (sub[1], sub[0])
            self.ids = list(map(itemgetter(1), user_mp.values()))
        else:
            self.ids = list(map(itemgetter(0), self.ids))

    def get_submission_sources(self):
        try:
            os.mkdir(self.code)
        except FileExistsError:
            self.echo('Warning: folder named "{}" already exists, assuming '
                      'any files inside are downloaded submissions.'.format(self.code))
        downloaded_subs = os.listdir(self.code)
        for id in self.ids:
            if id in downloaded_subs:
                self.echo('Submission {} already downloaded. Continuing...'.format(id))
                continue
            self.echo('Downloading submission {}'.format(id))
            with open('{}/{}'.format(self.code, id), 'w') as f:
                f.write(self.request(self.BASE_URL.format(sub_id=id)).text)

    def run(self):
        self.get_submission_ids()
        self.get_submission_sources()


def main():
    parser = argparse.ArgumentParser(description='DMOJ Submission Downloader')
    parser.add_argument('problem_code', help='The DMOJ problem code.')
    parser.add_argument('session_id', help='Your DMOJ session ID, which is needed to retrieve the submission source.')
    parser.add_argument('--best-only', '-b', default=0, const=1, action='store_const',
                        help='Only store the best submission per user, rather than all submissions, '
                             'where best submission is determined by SubmissionDownloader.ORDER.')
    args = parser.parse_args()

    problem_code = args.problem_code
    cookies = {
        'sessionid': args.session_id,
    }
    best_only = args.best_only
    SubmissionDownloader(problem_code, cookies, best_only).run()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
