"""
Author: Rex Valkering (rexvalkering@gmail.com)

Extracts and zips all files of users in docker.

Usage: python2 docker.py [--force] [-s students.txt] [--test] archive
Example: python2 docker.py assignment1 -f -s students.txt

"""

import subprocess
import re
import os
import tarfile
import shutil

def main(args):
    folder = args.archive
    students = []

    # Rename <archivename>.tar.gz to <archivename>
    if folder[-7:] == ".tar.gz":
        folder = folder[:-7]

    # Check if the folder does not currently exist.
    if not args.force and os.path.exists(folder):
        print "Folder '%s' already exists. Please rename or remove the folder, \
               choose another name for your archive, or run with --force." % folder
        exit(1)

    # Create folder if necessary.
    if not os.path.exists(folder) and not args.test:
        os.makedirs(folder)

    # Index students if needed.
    if args.students:
        if not os.path.exists(args.students):
            print "Could not find students file called %s, aborting." % \
                args.students
            exit(1)

        print "Reading %s..." % args.students
        with open(args.students) as f:
            out = f.read()
            lines = out.split('\n')
            for line in lines:
                if line.strip() == "":
                    continue

                students.append(line.strip())
                print "- Found student: %s" % line.strip()

    if args.students and not students:
        print "No students in file called %s, aborting." % args.students
        exit(1)

    dockerfolder = "/home/jovyan/work"

    # Call the docker ps command to get all currently active accounts.
    process = subprocess.Popen(['docker', 'ps'], stdout=subprocess.PIPE)
    out, err = process.communicate()

    lines = out.split('\n')
    for line in lines[1:]:

        # Extract name
        line = re.sub(r'[ \t]+', ' ', line)
        parts = line.split(' ')
        name = parts[-1]

        # Check if we want the contents of this users folder.
        if not name or (args.students is not None and name not in students):
            continue

        # Find all files of this user.
        source = name + ':' + dockerfolder
        print source

        # Copy files, except in test-case.
        if not args.test:
            process = subprocess.Popen(['docker', 'cp', name + ':' + dockerfolder,
                                        folder + '/' + name])

    # Create archive, except in test-case.
    if not args.test:
        print "Creating %s.tar.gz..." % folder
        with tarfile.open(folder + '.tar.gz', 'w:gz') as tar:
            tar.add(folder, arcname=os.path.basename(folder))
        print "-done"

if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', help='Name of archive')
    parser.add_argument('-f', '--force', help='Force using archive name for folder that already exists.', action='store_true')
    parser.add_argument('-s', '--students', help='File containing accounts of students to archive.')
    parser.add_argument('-t', '--test', help='Just test what it would do.', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    main(args)


