import dmmgclient as client
import dmmgserver as server
import argparse
from dmmgmain import dmmg, filepath_gen, nltk_updater
import os
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='== DMMG ==')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--client", action="store_true",
                       help="Enable distributed mode. Client.")
    group.add_argument("-s", "--server", action="store_true",
                       help="Enable distributed mode. Server.")

    parser.add_argument("delta",
                        help="Weight of syntax vs. semantic",
                        type=float)
    parser.add_argument("query",
                        help="Path of the queries")
    parser.add_argument("rootpath",
                        help="Path to the database root")

    nltk_updater()

    args = parser.parse_args()
    if args.client:
        client.start()
    elif args.server:
        server.start((args.delta, args.query, args.rootpath))
    else:
        if os.path.isfile(args.rootpath):
            dmmg(args.delta, args.query, args.rootpath)
        elif os.path.isdir(args.rootpath) and os.path.isfile(args.query):
            for filepath in filepath_gen(args.rootpath):
                dmmg(args.delta, args.query, filepath)
        else:
            sys.stderr.write('Provide a valid path.')
            exit(1)
