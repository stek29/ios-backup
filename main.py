from __future__ import division, print_function
import argparse
import errno
import platform  # TODO: use sys instead
import sqlite3
from shutil import copyfile, move
import os
from os.path import expanduser, isdir, join, basename
from pprint import pprint


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise exc


def get_dirs(path):
    return list(map(basename, filter(isdir, map(lambda d: join(path, d), os.listdir(path)))))


def get_backup_paths():
    if platform.system().lower() == 'windows':
        if platform.release().lower() == 'xp':
            itunes_bak_path = expanduser('~/Application Data/Apple Computer/MobileSync/Backup/')
        else:
            itunes_bak_path = expanduser('~/AppData/Roaming/Apple Computer/MobileSync/Backup/')
    elif platform.system().lower() == 'darwin':
        itunes_bak_path = expanduser('~/Library/Application Support/MobileSync/Backup/')
    else:
        raise Exception("Can't detect system")

    if not isdir(itunes_bak_path):
        raise Exception("Can't find iTunes backup folder")

    return itunes_bak_path


def main(args=None):
    parser = argparse.ArgumentParser(description='iTunes backup normaliser')
    parser.add_argument('-u', '--udid', help='Backup UDID. Pass none to see list.')
    parser.add_argument('-p', '--path', help='Path to backups folder. Pass none to let'
                                             ' the script guess it.')
    parser.add_argument('-d', '--dest', help='Destination folder. "iBackup-UDID" by default.')
    parser.add_argument('-c', '--copy', action='store_true', default='False',
                        help='Copy all the files instead of moving. Not recommended, better'
                             ' make a copy of whole folder on your own.')

    args = parser.parse_args(args)

    if not args.path:
        args.path = get_backup_paths()
        print('Backup path guessed: {}'.format(args.path))

    udids = get_dirs(args.path)

    if not args.udid:
        print('UDIDs:')
        pprint(udids)
    elif args.udid not in udids:
        raise Exception("Can't find folder for UDID {}".format(args.udid))
    else:
        backup_path = join(args.path, args.udid)
        if not args.dest:
            args.dest = join(os.getcwd(), 'iBackup-{}'.format(args.udid))
        if os.path.exists(args.dest):
            raise Exception('Please move {} somewhere and try again'.format(args.dest))
        else:
            os.mkdir(args.dest)
            os.chdir(args.dest)

        conn = sqlite3.connect(join(backup_path, join(backup_path, 'Manifest.db')))
        c = conn.cursor()

        print('Counting directories: ', end='')
        count = next(c.execute('SELECT Count(*) FROM Files WHERE flags=2'))[0]
        print(count)

        print('Preparing directories')
        i = 0
        for dom, rpath in c.execute('SELECT domain,relativePath FROM Files WHERE flags=2'):
            print('{:.2%}'.format(i/count), end='\r')
            mkdir_p(join(dom, rpath))
            i += 1
        print('Done')

        print('Counting files: ', end='')
        count = next(c.execute('SELECT Count(*) FROM Files WHERE flags=1'))[0]
        print(count)

        print('Moving files:')
        fails = open('fails.txt', mode='w+')
        i = 0
        for file, dom, rpath in c.execute('SELECT fileID,domain,relativePath FROM Files WHERE flags=1'):
            file_to = join(dom, rpath)
            try:
                file_from = join(backup_path, file[:2], file)
                if not args.copy:
                    move(file_from, file_to)
                else:
                    copyfile(file_from, file_to)
            except Exception as e:
                print(file_from, 'caused an error!')
                print(e)
                print(file_from, file=fails)

            print('{:.2%} of {}, {}'.format(i/count, count, file_to), end='\r')
            i += 1
        print('Done')
        print('Be sure to check fails.txt')

        fails.close()
        c.close()
        conn.close()

if __name__ == '__main__':
    main()
