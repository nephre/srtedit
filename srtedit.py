#!/usr/bin/python3

import argparse
import datetime
import re
import sys


def parse_args(args):
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-i', '--interval', type=float, metavar='duration',
                      help='Amount of seconds to add. Accepts negative numbers.')
    mode.add_argument('-m', '--minimum', type=float, metavar='duration',
                      help='Minimum subtitle display time. Shorter subtitles will be expanded to this value.')
    mode.add_argument('-s', '--slide', type=float, metavar='duration',
                      help='Display all subtitles later (positive) or earlier (negative value) by duration')
    parser.add_argument('-e', '--encoding', help='File encoding', default='cp1250', metavar='encoding')
    parser.add_argument('-f', '--file', help='SRT file to process', required=True, metavar='filename')
    parser.add_argument('-o', '--output', default=None, metavar='filename',
                        help='Output file name. If none, writes to input file.')

    out_args = parser.parse_args(args)

    if out_args.output is None:
        out_args.output = out_args.file

    return out_args


def main(args):
    with open(args.file, 'r', encoding=args.encoding) as srt_file:
        data = srt_file.read().splitlines()

    new_data = []
    pat_str = r'(?P<start_time>[\d]{2}:[\d]{2}:[\d]{2},[\d]{3}) --> (?P<end_time>[\d]{2}:[\d]{2}:[\d]{2},[\d]{3})'
    pattern = re.compile(pat_str)

    if args.minimum:
        delta = datetime.timedelta(seconds=args.minimum)
    elif args.interval:
        delta = datetime.timedelta(seconds=args.interval)
    else:
        delta = datetime.timedelta(seconds=args.slide)

    for line in data:
        result = pattern.search(line)

        if result:
            start_time = result.group('start_time')
            end_time = result.group('end_time')

            ts_start = datetime.datetime.strptime(f'{start_time}000', '%H:%M:%S,%f')
            ts_end = datetime.datetime.strptime(f'{end_time}000', '%H:%M:%S,%f')

            if args.minimum:
                diff = ts_end - ts_start
                if diff < delta:
                    new_end = ts_start + delta
                else:
                    new_end = ts_end
                new_start = ts_start
            elif args.interval:
                new_start = ts_start
                new_end = ts_end + delta
            else:
                new_start = ts_start + delta
                new_end = ts_end + delta

            new_start_time = new_start.strftime('%H:%M:%S,%f')[0:-3]
            new_end_time = new_end.strftime('%H:%M:%S,%f')[0:-3]

            line = f'{new_start_time} --> {new_end_time}'

        new_data.append(line)

    with open(args.output, 'w', encoding=args.encoding) as new_file:
        new_file.write('\n'.join(new_data))


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(args)
