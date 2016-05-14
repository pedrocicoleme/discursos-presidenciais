#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import os
import subprocess
import tinydb
import tqdm
import deco

import time

@deco.concurrent
def read_pdf_disc(discurso_file, pres_dir, disc_dir, disc_file):
    # print os.getpid()

    out, err = subprocess.Popen(
        [u'pdftotext', discurso_file, '-'],
        stdout=subprocess.PIPE).communicate()

    return {
        'presidente': pres_dir,
        'discurso_tipo': disc_dir,
        'discurso': disc_file,
        'texto': out}

@deco.synchronized
def read_pdfs_list(disc_intermediate_list):
    almost_there_disc_list = [None] * len(disc_intermediate_list)

    for idx, x in enumerate(disc_intermediate_list):
        almost_there_disc_list[idx] = read_pdf_disc(*x)

    return almost_there_disc_list

def pdfs2db():
    db = tinydb.TinyDB('./data/discursos_db.json')
    q = tinydb.Query()

    logger.info(u'Searching in folders...')
    disc_intermediate_list = []
    for pres_dir in os.walk('./data/discursos').next()[1]:
        presidente_dir = os.path.join('./data/discursos', pres_dir)

        for disc_dir in os.walk(presidente_dir).next()[1]:
            discurso_dir = os.path.join(presidente_dir, disc_dir)

            for disc_file in os.walk(discurso_dir).next()[2]:
                if not disc_file.endswith('.pdf'):
                    continue

                if not db.search((q.presidente == pres_dir) \
                  & (q.discurso_tipo == disc_dir) & (q.discurso == disc_file)):
                    discurso_file = os.path.join(discurso_dir, disc_file)

                    disc_intermediate_list.append([
                        discurso_file,
                        pres_dir,
                        disc_dir,
                        disc_file])

    logger.info(u'Reading all pdfs...')
    almost_there_disc_list = read_pdfs_list(disc_intermediate_list)

    logger.info(u'Saving in tinydb...')
    for x in tqdm.tqdm(almost_there_disc_list):
        if x != None:
            db.insert(x)

    logger.info(u'Done')

if __name__ == u'__main__':
    pdfs2db()
