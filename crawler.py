#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger()

import requests
import urlparse
import lxml.html
import regex

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

        #html_viewer(r.content)

        root = lxml.html.fromstring(r.content)

        all_links = dict()

        for link in root.xpath(u'//div[@id="content"]/div[@id="parent-fieldname-text"]/ul[1]/li/a'):
            titulo = link.get(u'title')
            real_link = link.get(u'href')

            if not regex.search(ur'^(Biografia|Foto|Ministérios|Vice-presidente|Viage|Órgã|Discursos Vice-Presidente|Substituto|Nereu)', titulo, regex.VERSION1|regex.IGNORECASE):
                all_links[titulo] = urlparse.urljoin(presidente_link, real_link)

        pronunciamento_link = root.xpath(u'//a[@title="pronunciamento"]/@href')
        discursos_link = root.xpath(u'//a[@title="Discursos"]/@href')
        mensagens_link = root.xpath(u'//a[contains(@title, "Mensagens")]/@href')

        presidentes.append({
            u'nome': root.xpath(u'//h1[@class="documentFirstHeading"]/span/text()')[0].strip(),
            u'url': presidente_link,
            u'links': all_links})

    # for idx, presidente in enumerate(presidentes):
    #     if presidente[u'mensagens_link'] != None:
    #         r = requests.get(presidente[u'mensagens_link'])

    #         root = lxml.html.fromstring(r.content)

    #         presidentes[idx][u'mensagens_links'] = root.xpath(u'//span[@class="contenttype-file summary"]/a/@href')

    for presidente in presidentes:
        if len(presidente[u'links']):
            from pprint import pprint
            pprint(presidente)

    return

if __name__ == u'__main__':
    extract_discursos()