#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger()

import requests
import urlparse
import lxml.html
import regex

import os, hashlib

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

    presidentes_links = [urlparse.urljoin(url_biblioteca, x) for x in \
      root.xpath(u'//div[@class="banner-tile tile-content"]/a[position()=1]/@href')]

    for presidente_link in presidentes_links[13:]:
        # if presidente_link.find(u'/jk') == -1:
        #     continue
        print presidente_link

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

    for presidente in presidentes:
        print u'======================= %s =======================' % presidente[u'nome']

        for secao, links in presidente[u'secoes'].iteritems():
            path = './data/discursos/%s/%s' % (presidente[u'nome'], secao)
            try: os.makedirs(path)
            except: pass

            for link in links:
                for x in go_until_pdf(link):
                    h = hashlib.md5()
                    h.update(x[1])
                    with open(os.path.join(path, u'%s.pdf' % h.hexdigest()), 'wb') as f:
                        f.write(x[1])

    return

def go_until_pdf(link):
    if link.find(u'twitter.com') != -1 or link.find(u'facebook.com') != -1:
        return

    print link

    try:
        r = requests.get(link)

        if r.headers[u'content-type'].find(u'html') != -1:
            root = lxml.html.fromstring(r.content)

            links_inside = root.xpath(u'//div[@id="content"]//a[not(ancestor::ul[@class="paginacao listingBar"]) or @class="proximo"]/@href')

            for link_inside in links_inside:
                for link_inside_inside in go_until_pdf(link_inside):
                    yield link_inside_inside
        else:
            yield [link, r.content, r.headers[u'content-type']]
    except Exception as e:
        logger.info(u'erro ao tentar acessar pagina, descartando')

    return

if __name__ == u'__main__':
    extract_discursos()
