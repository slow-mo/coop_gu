# coding: utf-8

import scraperwiki
import lxml.html
import re
import datetime

LAST_MONTH = 0
DEBUG = 0
BASE_URL = 'http://www.gazzettaufficiale.it'

mesi = ('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto',
        'settembre', 'ottobre', 'novembre', 'dicembre')

def str_date(str):
    data_s = str.split("-")
    if len(data_s) == 3 and data_s[0].isdigit() and data_s[1].isdigit() and data_s[2].isdigit():
        return datetime.date(int(data_s[2]), int(data_s[1]), int(data_s[0]))
    else:
        return ""

def scrape_gu(url):
    html = scraperwiki.scrape(url)
    root = lxml.html.fromstring(html)

    t = root.cssselect("span[class='estremi']")
    gu_num = int(t[0].text)
    gu_data = str_date(t[1].text)


    for i in root.cssselect(".risultato"):
        if "coop." in i[1].text or "Coop." in i[1].text or "Cooperativ" in i[1].text or "cooperativ" in i[1].text:
            searchObj = re.search(r"atto\.codiceRedazionale=(.+?)(?:&|$)", i[1].attrib['href'], re.I)
            if searchObj:
                codice = searchObj.group(1)
            else:
                continue
                
            provvedimento = " ".join(i.cssselect('.data')[0].text.split())
            
            expr = "(\d+) (%s) (\d+)" % "|".join(mesi)
            dSrcObj = re.search(expr, provvedimento, re.I)
            if dSrcObj:
                prov_data = datetime.date(int(dSrcObj.group(3)), mesi.index(dSrcObj.group(2))+1, int(dSrcObj.group(1)))
            else:
                prov_data = ""
                
            if i.cssselect('.pagina'):
                pagina = int(i.cssselect('.pagina')[0].text.replace("Pag. ", ""))
            else:
                pagina = ""
				
            record = {
                "codice" : codice,
                "titolo" : " ".join(i[1].text.split()).replace(". (" + codice + ")", ""),
                "provvedimento" : provvedimento,
                "prov_data" : prov_data,
                "gu_num" : gu_num,
                "gu_data" : gu_data,
                "pagina" : pagina,
                "url" : BASE_URL + i[1].attrib['href'],
            }
            if DEBUG == 1:
                print i[1].text.strip().replace("\n", " ")
            else:
                scraperwiki.sqlite.save(unique_keys=["codice"], data=record)

if LAST_MONTH == 1:
    gu_html = scraperwiki.scrape('http://www.gazzettaufficiale.it/30giorni/serie_generale')
    gu_root = lxml.html.fromstring(gu_html)

    for i in gu_root.cssselect(".elenco_ugazzette"):
        scrape_gu(BASE_URL + i.attrib['href'])
        
if LAST_MONTH == 2:
    for i in range(2013, 2019):
        gu_html = scraperwiki.scrape('http://www.gazzettaufficiale.it/ricercaArchivioCompleto/serie_generale/%i' % i)
        gu_root = lxml.html.fromstring(gu_html)

        for i in gu_root.cssselect(".elenco_gazzette"):
            scrape_gu(BASE_URL + i.attrib['href'])

else:
    gu_html = scraperwiki.scrape(BASE_URL)
    gu_root = lxml.html.fromstring(gu_html)
    url = gu_root.cssselect(".ultimelist li a")[0].attrib['href']
    scrape_gu(BASE_URL + url)
