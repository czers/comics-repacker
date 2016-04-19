#!/usr/bin/env python
import argparse
import magic
import tempfile
import zipfile
import rarfile
import os


class ComicsRepacker:
    def __init__(self, archives):
        self.archives = archives

    @staticmethod
    def decode_bytes(bytestring):
        try:
            decoded = bytestring.decode('utf-8')
        except UnicodeError:
            decoded = bytestring.decode('iso8859-1')
        return decoded

    def print_archive_info(self, archive):
        mime_type = self.get_archive_mime_type(archive)
        description = self.get_archive_type_description(archive)
        print('{0} {1} {2}'.format(archive.name, mime_type, description))

    def get_archive_mime_type(self, archive):
        last_pos = archive.tell()
        archive.seek(0)
        mime_type = self.decode_bytes(magic.from_buffer(archive.read(), mime=True))
        archive.seek(last_pos)
        return mime_type

    def get_archive_type_description(self, archive):
        last_pos = archive.tell()
        archive.seek(0)
        description = self.decode_bytes(magic.from_buffer(archive.read()))
        archive.seek(last_pos)
        return description

    def extract_archives(self, tmp):
        for i, archive in enumerate(self.archives):
            path = os.path.join(tmp, "{0:04}".format(i))
            self.extract_archive(archive, path)

    def extract_archive(self, archive, path):
        mime_type = self.get_archive_mime_type(archive)
        if mime_type == 'application/zip':
            with zipfile.ZipFile(archive) as zip:
                zip.extractall(path)
        elif mime_type == 'application/x-rar':
            with rarfile.RarFile(archive.name) as rar:
                rar.extractall(path)
        else:
            raise Exception('Unsupported input archive format: {0}'.format(mime_type))


def main():
    parser = argparse.ArgumentParser(description='Repack multiple comic archives as single archive')
    parser.add_argument('archives', nargs='+', type=argparse.FileType('rb', bufsize=4096))
    args = parser.parse_args()
    repacker = ComicsRepacker(args.archives)
    for archive in args.archives:
        repacker.print_archive_info(archive)
    with tempfile.TemporaryDirectory(prefix='comics-repacker-') as tmp:
        print('Using {0} as temporary working directory'.format(tmp))
        repacker.extract_archives(tmp)
        input('Press Enter to continue...')
    print('Done.')


if __name__ == '__main__':
    main()
