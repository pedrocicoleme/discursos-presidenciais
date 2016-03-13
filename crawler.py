#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger()

import requests
import urlparse
import lxml.html
import regex

from pprint import pprint

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

    url_biblioteca = u'http://www.biblioteca.presidencia.gov.br/'
    url = u'http://www.biblioteca.presidencia.gov.br/presidencia/ex-presidentes'

    r = requests.get(url)

    root = lxml.html.fromstring(r.content)

    presidentes_links = [urlparse.urljoin(url_biblioteca, x) for x in root.xpath(u'//div[@class="banner-tile tile-content"]/a[position()=1]/@href')]

    for presidente_link in presidentes_links:
        r = requests.get(presidente_link)

        #html_viewer(r.content)

        root = lxml.html.fromstring(r.content)

        sections = root.xpath(u'//h2[@class="outstanding-title"]')

        if not len(sections):
            logger.info(u'nao foi possivel encontrar os dados na página')
            continue

        secoes = {}
        for section in sections[1:]:
            if not regex.search(ur'^(Biografia|Foto|Ministérios|Resumo do Governo|Vice|Viage|Órgã|Entrevistas|Substituto|Nereu|Café|Galeria|Publicações Oficiais da PR|Espaço|Acervo de|Programas)', section.text_content(), regex.VERSION1|regex.IGNORECASE):
                #print section.text_content()

                links = section.xpath(u'./ancestor::div[@class="tile azul"][1]/following-sibling::div[@class="tile tile-default"][1]//a/@href')
                
                secoes[section.text_content()] = links

        presidentes.append({
            u'nome': sections[0].text_content().strip(),
            u'url': presidente_link,
            u'secoes': secoes})

        # break

    # for idx, presidente in enumerate(presidentes):
    #     if presidente[u'mensagens_link'] != None:
    #         r = requests.get(presidente[u'mensagens_link'])

    #         root = lxml.html.fromstring(r.content)

    #         presidentes[idx][u'mensagens_links'] = root.xpath(u'//span[@class="contenttype-file summary"]/a/@href')

    for presidente in presidentes:
        print u'======================= %s =======================' % presidente[u'nome']

        for secao, links in presidente[u'secoes'].iteritems():
            for link in links:
                r = requests.get(link)

                print r.headers[u'content-type']

    return

if __name__ == u'__main__':
    extract_discursos()