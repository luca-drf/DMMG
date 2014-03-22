import disdmmg as dis
import argparse
from maindmmg import dmmg, filepath_gen
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='== DMMG ==')
    parser.add_argument("-d", "--distributed",
                        choices=['c', 's'],
                        help="Enable distributed mode. {(c)lient, (s)erver}")
    parser.add_argument("delta",
                        help="Weight of syntax vs. semantic",
                        type=float)
    parser.add_argument("query",
                        help="Filepath of the query")
    parser.add_argument("rootpath",
                        help="Path to the database root")

    args = parser.parse_args()
    if args.distributed:
        if args.distributed == 'c':
            dis.client((args.delta, args.query, args.rootpath))
        elif args.distributed == 's':
            dis.server((args.delta, args.query, args.rootpath))
    else:
        if os.path.isfile(args.rootpath):
            dmmg(args.delta, args.query, args.rootpath)
        elif os.path.isdir(args.rootpath):
            for filepath in filepath_gen(args.rootpath):
                dmmg(args.delta, args.query, filepath)
        else:
            print 'Provide a valid root path.'
            exit(1)
