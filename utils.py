#!/usr/bin/env python
# -*- coding: utf-8 -*-

# utils.py by:
#    Agustin Zubiaga <aguz@sugarlabs.org>
#    Cristhofer Travieso <cristhofert97@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
import os

sys.path.insert(0, 'lib')

import paramiko
import json
import time

from sugar import profile
from sugar.activity import activity
from sugar.datastore import datastore

MYFILES = os.path.join(activity.get_activity_root(), 'data')
SERVER = '192.168.1.100'
USERNAME = 'servidor'
PASSWORD = 'grupos'
GROUPS_DIR = "Groups"
MACHINES = '/home/servidor/serial_numbers.txt'
LOG = '/home/servidor/log.txt'


def get_group():
    _file = open('config')
    group = _file.read()
    _file.close()

    return group

GROUP = get_group()


def connect_to_server():
    """Connects to sftp server"""
    transport = paramiko.Transport((SERVER, 22))
    transport.connect(username=USERNAME, password=PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(os.path.join(GROUPS_DIR, GROUP))

    save_log(sftp, 'Connecting')

    return sftp


def get_documents(sftp, subject):
    documents = []

    for i in sftp.listdir(subject):
        if not i.startswith("."):
            documents.append(i)

    return documents


def save_document(sftp, subject, document, mimetype):
    path = os.path.join(MYFILES, document)
    sftp.get(os.path.join(subject, document), path)

    jobject = datastore.create()
    jobject.metadata['title'] = document
    jobject.metadata['icon-color'] = \
            profile.get_color().to_string()
    jobject.metadata['mime_type'] = mimetype
    jobject.file_path = path
    datastore.write(jobject)

    save_log(sftp, 'Saving document: %s' % (document))


def get_info(sftp, subject, document, only_mime=False):
    _file = sftp.open(os.path.join(subject, ".desc"))
    descs = json.load(_file)
    _file.close()
    if only_mime:
        return descs[document][-1]
    else:
        return descs[document]


def is_downloaded(sftp, subject, document):
    pass


def save_me(sftp, group, name):
    _file = sftp.open(MACHINES, 'r')
    machines = json.load(_file)
    _file.close()

    _file = open('/proc/device-tree/serial-number')
    serial_number = _file.read()[:-1]
    machines[serial_number] = (name, group)

    _file = sftp.open(MACHINES, 'w')
    try:
        json.dump(machines, _file)
    finally:
        _file.close()
        
    config_file = open('config', 'w')
    config_file.write(group)
    config_file.close()


def save_log(sftp, _log):
    log = sftp.open(LOG, 'r').read()

    _file = open('/proc/device-tree/serial-number')
    serial_number = _file.read()[:-1]
    new_log = sftp.open(LOG, 'w')
    log += "%f - %s - %s\n" % (time.time(), serial_number, _log)
    new_log.write(log)
    new_log.close()
    