# DMOJ Submission Downloader

Downloads all the submissions of a DMOJ problem. Useful for when MOSS is needed to check for cheaters in a contest.

## Installation
First, install the prerequisites:
```sh
$ pip3 install -r requirements.txt
```

## Usage
```
$ python3 downloader.py --help
usage: downloader.py [-h] [--best-only] problem_code session_id

DMOJ Submission Downloader

positional arguments:
  problem_code     The DMOJ problem code.
  session_id       Your DMOJ session ID, which is needed to retrieve the
                   submission source.

optional arguments:
  -h, --help       show this help message and exit
  --best-only, -b  Only store the best submission per user, rather than all
                   submissions, where best submission is determined by
                   SubmissionDownloader.ORDER.
```
