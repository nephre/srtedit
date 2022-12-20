#!/usr/bin/python3

import argparse
import datetime
import re
import sys


def parse_args(args):
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-i', '--interval', type=float, default=1, metavar='duration',
                      help='Amount of seconds to add. Accepts negative numbers.')
    mode.add_argument('-m', '--minimum', type=float, default=1, metavar='duration',
                      help='Minimum subtitle display time. Shorter subtitles will be expanded to this value.')
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
    else:
        delta = datetime.timedelta(seconds=args.interval)

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
            else:
                new_end = ts_end + delta

            new_end_time = new_end.strftime('%H:%M:%S,%f')[0:-3]
            line = f'{start_time} --> {new_end_time}'

        new_data.append(line)

    with open(args.output, 'w', encoding=args.encoding) as new_file:
        new_file.write('\n'.join(new_data))


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(args)
