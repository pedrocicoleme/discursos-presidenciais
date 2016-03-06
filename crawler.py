#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger()

import requests
import urlparse
import lxml.html

def html_viewer(html, block=False):
    import uuid
    filename = u'/tmp/%s.html' % uuid.uuid4()
    
    with open(filename, 'w') as f:
        f.write(html)

    import click
    click.launch(filename)

    if block:
        raw_input()

    return

def extract_discursos():
    presidentes = []

    url = u'http://www.biblioteca.presidencia.gov.br/ex-presidentes'

    r = requests.get(url)

    root = lxml.html.fromstring(r.content)

    presidentes_links = [x+u'/' for x in root.xpath(u'//div[@class="photoAlbum"]/div/a[position()=1]/@href')]

    for presidente_link in presidentes_links:
        r = requests.get(presidente_link)

        html_viewer(r.content)

        root = lxml.html.fromstring(r.content)

        nome = root.xpath(u'//h1[@class="documentFirstHeading"]/span/text()')[0].strip()
        pronunciamento_link = root.xpath(u'//a[@title="pronunciamento"]/@href')
        discursos_link = root.xpath(u'//a[@title="Discursos"]/@href')
        mensagens_link = root.xpath(u'//a[contains(@title, "Mensagens")]/@href')

        presidentes.append({
            u'nome': nome,
            u'presidente_link': presidente_link,
            u'pronunciamento_link': urlparse.urljoin(presidente_link, pronunciamento_link[0]) if len(pronunciamento_link) else None,
            u'discursos_link': urlparse.urljoin(presidente_link, discursos_link[0]) if len(discursos_link) else None,
            u'mensagens_link': urlparse.urljoin(presidente_link, mensagens_link[0]) if len(mensagens_link) else None})

    for idx, presidente in enumerate(presidentes):
        if presidente[u'mensagens_link'] != None:
            r = requests.get(presidente[u'mensagens_link'])

            root = lxml.html.fromstring(r.content)

            presidentes[idx][u'mensagens_links'] = root.xpath(u'//span[@class="contenttype-file summary"]/a/@href')

    from pprint import pprint
    pprint(presidentes)

    return

if __name__ == u'__main__':
    extract_discursos()