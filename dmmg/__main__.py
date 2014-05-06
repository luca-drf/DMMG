import dmmgclient as client
import dmmgserver as server
import argparse
from dmmgmain import similarity, filepath_gen, nltk_updater
import os
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='== DMMG ==')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--client", action="store_true",
                       help="Enable distributed mode. Client.")
    group.add_argument("-s", "--server", action="store_true",
                       help="Enable distributed mode. Server.")

    parser.add_argument("-d", "--delta", type=float,
                        help="Weight of syntax vs. semantic")
    parser.add_argument("query",
                        help="Path of the queries")
    parser.add_argument("rootpath",
                        help="Path to the database root")

    nltk_updater()

    args = parser.parse_args()
    if args.delta:
        delta = args.delta
    else:
        delta = None
    if args.client:
        client.start()
    elif args.server:
        server.start((delta, args.query, args.rootpath))
    else:
        if os.path.isfile(args.rootpath):
            similarity(delta, args.query, args.rootpath)
        elif os.path.isdir(args.rootpath) and os.path.isfile(args.query):
            for filepath in filepath_gen(args.rootpath):
                similarity(delta, args.query, filepath)
        elif os.path.isdir(args.rootpath) and os.path.isdir(args.query):
            queryset, testset = server.file_manager(args.query, args.rootpath)
            for query_filepath in queryset:
                try:
                    testset.remove(query_filepath)
                except KeyError:
                    pass
                for test_filepath in testset:
                    similarity(delta, query_filepath, test_filepath)
        else:
            sys.stderr.write('Provide a valid path.\n')
            exit(1)
