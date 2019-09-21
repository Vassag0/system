#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
file_helpers.py.

https://github.com/krahsdevil/crt-for-retropie/

Copyright (C)  2018/2019 -krahs- - https://github.com/krahsdevil/
Copyright (C)  2019 dskywalk - http://david.dantoine.org

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 2 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os, logging
import hashlib, shutil, requests

from .core_paths import ROOT_PATH

def remove_line(p_sFile, p_sRemoveMask):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile,"r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            if p_sRemoveMask not in line:
                f.write(line) # valid line
        f.truncate() # remove everything after the last write
        return True

def modify_line(p_sFile, p_sLineToFind, p_sNewLine, p_bEndLine = True):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            if p_sLineToFind in line:
                line = p_sNewLine
                if p_bEndLine:
                    line += "\n"
            f.write(line) # new line
        f.truncate() # remove everything after the last write
        return True

def add_line(p_sFile, p_sNewLine, p_bEndLine = True):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "a") as f:
        line = p_sNewLine
        if p_bEndLine:
            line += "\n"
        f.write(line)

def ini_get(p_sFile, p_sFindMask, p_bFullData = False):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r") as f:
        for line in f:
            lValues = line.strip().replace('=',' ').split(' ')
            if p_sFindMask == lValues[0].strip():
                if p_bFullData:
                    return lValues
                else:
                    return lValues[-1].strip()
    return False

def ini_set(p_sFile, p_sKeyMask, p_sNewValue, p_bAddQuotes=False):
    if not os.path.isfile(p_sFile):
        return None
    with open(p_sFile, "r+") as f:
        new_file = f.readlines()
        f.seek(0) # rewind
        for line in new_file:
            lValues = line.strip().replace('=',' ').split(' ')
            if p_sKeyMask == lValues[0].strip():
                data = "%s" % p_sNewValue
                if p_bAddQuotes:
                    data = '"%s"' % data
                line = '%s = %s\n' % (p_sKeyMask, data)
            f.write(line) # new line
        f.truncate() # remove everything after the last write
        return True


def ini_getlist(p_sFile, p_sFindMask):
    lValues = ini_get(p_sFile, p_sFindMask, True)
    if lValues:
        return lValues[1:]
    else:
        return []

def md5_file(p_sFile):
    hasher = hashlib.md5()
    with open(p_sFile, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def remove_file(p_sFile):
    try:
        os.remove(p_sFile)
    except OSError:
        pass

def touch_file(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def dw_file(p_sUrl, p_sFile, p_oCallback):
    dAgent = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    CHUNK_SIZE = 32768
    session = requests.Session()
    response = session.get(p_sUrl, stream=True, headers=dAgent, verify=False)
    total_length = response.headers.get('content-length')
    if total_length is None: # no content length header
        print response.content
        return None
    dl = 0
    total_length = int(total_length)
    print "bytes", total_length
    with open(p_sFile, "wb") as f:
        for data in response.iter_content(CHUNK_SIZE):
            if not data: # filter out keep-alive new chunks
                continue
            dl += CHUNK_SIZE
            #sys.stdout.write("\r%s" % str(dl / 1024))
            f.write(data)
            done = int(30 * dl / total_length)
            sInfo = "%% [%s%s]" % ('=' * done, ' ' * (30-done))
            p_oCallback(sInfo)


def dw_gdrive(id, destination, p_oCallback, p_iTotal = None):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        total_dw = 0
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    total_dw += CHUNK_SIZE
                    sInfo = "Downloaded: %skb" % str(total_dw/1024)
                    if p_iTotal:
                        #sys.stdout.write("\r%s" % sInfo)
                        done = int(50 * total_dw / p_iTotal)
                        sInfo = "%% [%s%s]" % ('=' * done, ' ' * (50-done))
                    p_oCallback(sInfo)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    
