# coding: utf-8

import scraperwiki
import lxml.html
import re
import datetime

PREV = 2
BASE_URL = 'http://www.gazzettaufficiale.it'

mesi = ('gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto',
		'settembre', 'ottobre', 'novembre', 'dicembre')
expr = "(\d+) (%s) (\d+)" % "|".join(mesi)
		
def str_date(str):
	data_s = str.split("-")
	if len(data_s) == 3 and data_s[0].isdigit() and data_s[1].isdigit() and data_s[2].isdigit():
		return datetime.date(int(data_s[2]), int(data_s[1]), int(data_s[0]))
	else:
		return ""

def scrape_gu(url):
	print url
	html = scraperwiki.scrape(url)
	root = lxml.html.fromstring(html)
	t = root.cssselect("span[class='estremi']")
	gu_numero = int(t[0].text)
	gu_data = str_date(t[1].text)

	for i in root.cssselect("span.risultato, span.emettitore"):
		if i.attrib['class'] == "emettitore":
			emettitore = i.text
		elif re.search(r"(?im)\bcoop(?:\.|\b|erativ)", i[1].text):
			searchObj = re.search(r"atto\.codiceRedazionale=(.+?)(?:&|$)", i[1].attrib['href'], re.I)
			if searchObj:
				codice = searchObj.group(1)
			else:
				continue
				
			atto = " ".join(i.cssselect('.data')[0].text.split())
			
			dSrcObj = re.search(expr, atto, re.I)
			if dSrcObj:
				atto_data = datetime.date(int(dSrcObj.group(3)), mesi.index(dSrcObj.group(2))+1, int(dSrcObj.group(1)))
			else:
				atto_data = ""
				
			if i.cssselect('.pagina'):
				pagina = int(i.cssselect('.pagina')[0].text.replace("Pag. ", ""))
			else:
				pagina = ""
				
			record = {
				"codice" : codice,
				"emanante" : emettitore,
				"titolo" : " ".join(i[1].text.split()).replace(". (" + codice + ")", ""),
				"atto" : atto,
				"atto_data" : atto_data,
				"gu_numero" : gu_numero,
				"gu_data" : gu_data,
				"pagina" : pagina,
				"url" : BASE_URL + i[1].attrib['href'],
			}
			scraperwiki.sqlite.save(unique_keys=["codice"], data=record)

if PREV == 1:
	gu_html = scraperwiki.scrape('http://www.gazzettaufficiale.it/30giorni/serie_generale')
	gu_root = lxml.html.fromstring(gu_html)
	for i in gu_root.cssselect(".elenco_ugazzette"):
		scrape_gu(BASE_URL + i.attrib['href'])	
elif PREV == 2:
	for i in range(2015, 2019):
		gu_html = scraperwiki.scrape('http://www.gazzettaufficiale.it/ricercaArchivioCompleto/serie_generale/%i' % i)
		gu_root = lxml.html.fromstring(gu_html)
		for l in gu_root.cssselect(".elenco_gazzette"):
			scrape_gu(BASE_URL + l.attrib['href'])
else:
	gu_html = scraperwiki.scrape(BASE_URL)
	gu_root = lxml.html.fromstring(gu_html)
	url = gu_root.cssselect(".ultimelist li a")[0].attrib['href']
	scrape_gu(BASE_URL + url)
	
