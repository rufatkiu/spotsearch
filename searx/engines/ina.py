# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 INA (Videos)
"""

from html import unescape
from urllib.parse import urlencode
from lxml import html
from searx.utils import extract_text

# about
about = {
    "website": 'https://www.ina.fr/',
    "wikidata_id": 'Q1665109',
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['videos']
paging = True
page_size = 12

# search-url
base_url = 'https://www.ina.fr'
search_url = base_url + '/ajax/recherche?{query}&espace=1&sort=pertinence&order=desc&offset={start}&modified=size'

# specific xpath variables
results_xpath = '//div[@id="searchHits"]/div'
url_xpath = './/a/@href'
title_xpath = './/div[contains(@class,"title-bloc-small")]'
thumbnail_xpath = './/img/@data-src'
publishedDate_xpath = '//div[@id="searchHits"]//div[contains(@class,"dateAgenda")]'


# do search-request
def request(query, params):
    params['url'] = search_url.format(start=params['pageno'] * page_size,
                                      query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)
    # parse results
    for result in dom.xpath(results_xpath):
        url_relative = result.xpath(url_xpath)[0]
        url = base_url + url_relative
        title = unescape(extract_text(result.xpath(title_xpath)))
        thumbnail = extract_text(result.xpath(thumbnail_xpath))
        results.append({'url': url,
                        'title': title,
                        'template': 'videos.html',
                        'thumbnail': thumbnail})

    # return results
    return results
