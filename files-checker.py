#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import os
import subprocess

def navigate_dirs():
    logger.info(u'Iniciando conferência de texto em arquivos')

    total = 0
    no_text = 0

    for dirpath, dirnames, filenames in os.walk('./data'):
        for filename in filenames:
            if not filename.endswith('.pdf'):
                continue

            total += 1

            fullpath = os.path.join(dirpath, filename)

            out, err = subprocess.Popen(
             ['pdftotext', '-layout', fullpath, '-'],
             stdout=subprocess.PIPE).communicate()

            if len(out) < 1000:
                logger.info(fullpath)

                no_text += 1

    logger.info((
        u'=============\n' + \
        u'Existem {} arquivos, dos quais {} não tem texto\n' + \
        u'=============').format(total, no_text))

if __name__ == u'__main__':
    navigate_dirs()
