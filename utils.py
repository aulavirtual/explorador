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

from sugar import profile
from sugar.activity import activity
from sugar.datastore import datastore

MYFILES = os.path.join(activity.get_activity_root(), 'data')
SERVER = '192.168.1.100'
USERNAME = 'servidor'
PASSWORD = 'grupos'
GROUPS_DIR = "Groups"


def _get_group():
    file = open('config')
    group = file.read()[:-1]
    file.close()
    
    return group

GROUP = _get_group()


def connect_to_server():
    """Connects to sftp server"""
    transport = paramiko.Transport((SERVER, 22))
    transport.connect(username=USERNAME, password=PASSWORD)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(os.path.join(GROUPS_DIR, GROUP))

    return sftp


def get_documents(sftp, subject):
    documents = []

    for i in sftp.listdir(subject):  
        if not i.startswith("."):
            documents.append(i)            

    return documents


def save_document(sftp, subject, document, mimetype):
    group = GROUP
    groups_dir = GROUPS_DIR

    remotepath = os.path.join(groups_dir, group)
    path = os.path.join(MYFILES, document)
    sftp.get(os.path.join(subject, document), path)
    
    jobject = datastore.create()
    jobject.metadata['title'] = document
    jobject.metadata['icon-color'] = \
            profile.get_color().to_string()
    jobject.metadata['mime_type'] = mimetype
    jobject.file_path = path
    datastore.write(jobject)


def get_info(sftp, subject, document, only_mime=False):
    file = sftp.open(os.path.join(subject, ".desc"))
    descs = json.load(file)
    file.close()
    if only_mime:
        return descs[document][-1]
    else:
        return descs[document]
        
def is_downloaded():
    pass
