#!/usr/bin/env python

"""
Replaces '{}' with a repository url in a command and runs the command for
each repo url in one or more JSON files.

The JSON files should have the format:

{
  "codeRepositories": [
    {"url": "https://github.com/$ORG/$REPO.git"},
    ...
  ]
}

Example usage:

$ ./map_repo_urls.py -c "echo {}" services/metadata/*.json
...
WARNING:__main__:No codeRepositories found for service Tiles
https://github.com/mozilla/tls-observatory.git
https://github.com/mozilla-services/shavar.git
https://github.com/mozilla-services/shavar-list-creation.git
https://github.com/mozilla-services/shavar-prod-lists.git
https://github.com/mozilla-services/shavar-server-list-config.git
https://github.com/mozilla/watchdog-proxy.git
https://github.com/mozilla/version-control-tools.git
https://github.com/mozilla/wpt-sync.git
$  ./map_repo_urls.py -q -c "echo {}" services/metadata/*.json
...
https://github.com/mozilla/tls-observatory.git
https://github.com/mozilla-services/shavar.git
https://github.com/mozilla-services/shavar-list-creation.git
https://github.com/mozilla-services/shavar-prod-lists.git
https://github.com/mozilla-services/shavar-server-list-config.git
https://github.com/mozilla/watchdog-proxy.git
https://github.com/mozilla/version-control-tools.git
https://github.com/mozilla/wpt-sync.git
"""

import argparse
import json
import logging
import subprocess


logging.basicConfig()
logger = logging.getLogger(__name__)


def iter_service_metadata(service_json_metadata_files):
    """Generator to read a list of service JSON files as dicts
    """
    for service_file in service_json_metadata_files:
        yield json.load(open(service_file, "r"))


def get_service_name(service_meta, fallback="unnamed"):
    """Returns a pretty printable name from a service metadata or the arg fallback name
    """
    return (
        service_meta.get("service", None)
        or service_meta.get("serviceKey", None)
        or fallback
    )


def iter_repo_urls(service_meta):
    """
    Generator to get repository URLs from an iterable of service metadata.

    Warns for missing codeRepositories key and missing URLs in a code
    repository.
    """
    repos = service_meta.get("codeRepositories", [])
    service_name = get_service_name(service_meta)
    if not repos:
        logger.warn("No codeRepositories found for service {}".format(service_name))
        raise StopIteration

    for i, repo in enumerate(service_meta.get("codeRepositories", [])):
        repo_url = repo.get("url", None)
        if not repo_url:
            logger.warn(
                "No url found for repo {} in service {}".format(service_name, i)
            )
            continue
        yield repo_url


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "-c",
        "--command",
        dest="cmd",
        type=str,
        help="Command to run on each repo. Defaults to printing the service name and repo url",
    )

    parser.add_argument(
        "-n",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Print the commands we'd run, but don't run them.",
    )

    parser.add_argument(
        "-q", "--quiet", dest="quiet", action="store_true", help="Suppress warnings."
    )

    parser.add_argument(
        "json_files",
        metavar="FILES",
        type=str,
        nargs="+",
        help="one or more JSON files",
    )

    return parser.parse_args()


def run_command_on_repo(cmd, dry_run):
    if dry_run:
        print("would run {!r}".format(cmd))
        return

    subprocess.run(cmd, universal_newlines=True, shell=True)


def main():
    args = parse_args()

    if args.quiet:
        logger.setLevel(logging.getLevelName("ERROR"))

    for service_meta in iter_service_metadata(args.json_files):
        for repo_url in iter_repo_urls(service_meta):
            service_name = get_service_name(service_meta)  # NB: unused
            run_command_on_repo(args.cmd.replace("{}", repo_url), args.dry_run)


if __name__ == "__main__":
    main()
