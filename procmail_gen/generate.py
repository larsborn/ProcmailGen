#!/usr/bin/env python3
import argparse
import json
import logging
import os
import pathlib
import re


class ConsoleHandler(logging.Handler):
    def emit(self, record):
        print('[%s] %s' % (record.levelname, record.msg))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--maildir', default=os.path.join(str(pathlib.Path.home()), '.maildir'))
    parser.add_argument('config_file_names', nargs='+')
    args = parser.parse_args()

    logger = logging.getLogger('ToDoNameClient')
    logger.handlers.append(ConsoleHandler())
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    existing_folders = []
    maildir = os.path.realpath(args.maildir)
    logger.debug(f'Reading maildir "{maildir}"...')
    for folder in os.listdir(maildir):
        if not folder.startswith('.'):
            continue
        if not all(os.path.exists(os.path.join(maildir, folder, subdir)) for subdir in ['cur', 'new', 'tmp']):
            continue
        existing_folders.append('/'.join(folder[1:].split('.')))
    logger.debug(f'Found {len(existing_folders)} mail folders.')

    print("FROM=`formail -xFrom: | sed -e 's/ *(.*)//; s/>.*//; s/.*[:<] *//'`")
    print('MAILSERVER=$1')
    print('')
    for file_name in args.config_file_names:
        logger.debug(f'Reading "{file_name}"...')
        with open(file_name, 'r') as fp:
            data = json.load(fp)
        for row in data:
            assert row.get('action') == 'move'
            destination_folder = row.get('destination_folder')
            assert destination_folder in existing_folders, f'{destination_folder} does not exist in {existing_folders}'
            headers = ['From', 'To', 'Subject']
            assert all(k in headers + ['action', 'destination_folder'] for k in row.keys())
            for header_name in headers:
                rules = row.get(header_name, {})
                assert all(k in ['is', 'contains', 'startswith'] for k in rules.keys())
                for type_name, transform in [
                    ('is', lambda x: f'{header_name}: {re.escape(x)}$'),
                    ('contains', lambda x: f'{header_name}: .+{re.escape(x)}'),
                    ('startswith', lambda x: f'{header_name}: {re.escape(x)}'),
                ]:
                    for s in rules.get(type_name, []):
                        print(':0:')
                        print(f'* ^{transform(s)}')
                        print(f'.{destination_folder.replace("/", ".")}/')
                        print('')

    logger.debug('All done.')


if __name__ == '__main__':
    main()
