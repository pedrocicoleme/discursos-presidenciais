#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger()

import requests
import lxml.html

def html_viewer(html, block=False):
    with open(u'/tmp/tmp_html.html', 'w') as f:
        f.write(html)

    import click
    click.launch(u'/tmp/tmp_html.html')

    if block:
        raw_input()

    return

def extract_discursos():

    url = u'http://www.biblioteca.presidencia.gov.br/ex-presidentes'

    r = requests.get(url)

    root = lxml.html.fromstring(r.content)

    presidentes_links = root.xpath(u'//div[@class="photoAlbum"]/div/a[position()=1]/@href')

    for presidente_link in presidentes_links:
        print presidente_link
        #logger.info(presidente_link)

        r = requests.get(presidente_link)

        root = lxml.html.fromstring(r.content)

        nome = root.xpath(u'//h1[@class="documentFirstHeading"]/span/text()')[0]

        pronunciamento_link = root.xpath(u'//a[@title="pronunciamento"]/@href')
        discursos_link = root.xpath(u'//a[@title="Discursos"]/@href')
        mensagens_link = root.xpath(u'//a[@title="Mensagens presidenciais"]/@href')

        print discursos_link

        #print nome

if __name__ == u'__main__':
    extract_discursos()