#!/usr/bin/env python3
import argparse
import os
import sys

from reptly.app import App
from reptly.aptly import Aptly
from reptly.ui import CronUI, PromptToolkitUi


def main():
    parser = argparse.ArgumentParser(
        prog="reply",
        description="""
    Aptly is a very powerful repository management tool. Managing
    mirrors, repositories, snapshots and publications requires multiple
    steps and many aptly calls.

    %(prog)s is a small helper script that implements a few common
    operations around repository management (primarily updating mirrors
    and repos, snapshotting them, merging them if needed and publish the
    snapshot to different destinations).

    Its name is a combination of aptly and reprepro as its ideological
    goal is providing aptlys features with a reprepro like easy to use
    interface.
    """,
    )
    parser.add_argument("--config")
    parser.add_argument(
        "--cron",
        action="store_const",
        const=CronUI,
        default=PromptToolkitUi,
        help="Produce only output on errors and changed packages",
    )

    actions = parser.add_subparsers(dest="action")
    update = actions.add_parser("update")
    update.add_argument(
        "target",
        metavar="MIRROR/REPO",
        nargs="*",
        help="name of mirror or repo to update",
    )

    publish = actions.add_parser("publish")
    publish.add_argument(
        "target", metavar="DEST", nargs="*", help="name of publish targets to update"
    )

    run = actions.add_parser("run")
    run.add_argument(
        "target",
        metavar="DEST",
        nargs="+",
        help="name of publish targets to update (with sources)",
    )

    args = parser.parse_args()

    aptly = Aptly()
    ui = args.cron()

    app = App(aptly, ui)

    if not args.config:
        for file in [
            "reptly.yaml",
            "reptly.yml",
            "conf.dpd",
            "config/reptly.yaml",
            "config/reptly.yml",
            "config/conf.dpd",
        ]:
            if os.path.exists(file) and os.path.isfile(file):
                args.config = file
                break
        else:
            print("ERROR: No default configuration file found", file=sys.stderr)

    file = str(args.config)
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as conf:
            app.load(conf)
    else:
        print(f"ERROR: Configuration file does not exist: {file}", file=sys.stderr)
        exit(1)

    if not args.action:
        parser.error("Action required")

    getattr(app, f"exec_{args.action}")(args)
