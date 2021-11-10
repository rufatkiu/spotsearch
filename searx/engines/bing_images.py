# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Bing (Images)
"""

from urllib.parse import urlencode
from lxml import html
from json import loads
from random import randrange
from searx.utils import match_language

from searx.engines.bing import language_aliases
from searx.engines.bing import _fetch_supported_languages, supported_languages_url  # NOQA # pylint: disable=unused-import

# about
about = {
    "website": 'https://www.bing.com/images',
    "wikidata_id": 'Q182496',
    "official_api_documentation": 'https://www.microsoft.com/en-us/bing/apis/bing-image-search-api',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['images']
paging = True
safesearch = True
time_range_support = True
supported_languages_url = 'https://www.bing.com/account/general'
number_of_results = 28

# search-url
base_url = 'https://www.bing.com/'
search_string = 'images/search'\
    '?{query}'\
    '&count={count}'\
    '&first={first}'\
    '&tsc=ImageHoverTitle'
time_range_string = '&qft=+filterui:age-lt{interval}'
time_range_dict = {'day': '1440',
                   'week': '10080',
                   'month': '43200',
                   'year': '525600'}

# safesearch definitions
safesearch_types = {2: 'STRICT',
                    1: 'DEMOTE',
                    0: 'OFF'}


# do search-request
def request(query, params):
    offset = ((params['pageno'] - 1) * number_of_results) + 1

    search_path = search_string.format(
        query=urlencode({'q': query}),
        count=number_of_results,
        first=offset)

    language = match_language(params['language'], supported_languages, language_aliases, 'en').lower()

    HV = randrange(1e10, 1e11)
    WTS = randrange(1e11, 1e12)
    CW = randrange(1e4, 1e5)
    CH = randrange(1e3, 1e5)

    params['cookies']['SRCHHPGUSR'] = \
        f'SRCHLANG={language}&BRW=XW&BRH=M&CW={CW}&CH={CH}&DPR=1&UTC=-180&DM=1&HV={HV}&WTS={WTS}&ADLT=' \
        + 'STRICT'

    params['cookies']['_EDGE_S'] = 'mkt=' + language +\
        '&ui=' + language + '&F=1'
    params['cookies']['_IDET'] = 'MIExp=0'
    params['cookies']['MMCA'] = 'ID=B361EE82CAB9425EB0EE47B5E80DF8C1'
    params['cookies']['BCP'] = 'AD=1&AL=1&SM=1'
    params['cookies']['_SS'] = 'SID=3208F62E63AF6F2F047CE6C462866EF2&R=0&RB=0&GB=0&RG=0&RP=0'
    params['cookies']['SRCHUID'] = 'V=2&GUID=EC79C7475528483B98FBE3F045357F18&dmnchg=1'
    params['cookies']['MUID'] = '11635A5F5EAA6FD83B3F4AB55F836EFF'
    params['cookies']['SRCHD'] = 'AF=IRPRST'
    params['cookies']['MUIDB'] = '11635A5F5EAA6FD83B3F4AB55F836EFF'
    params['cookies']['_EDGE_V'] = '1'
    params['cookies']['SUID'] = 'M'

    params['url'] = base_url + search_path
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_string.format(interval=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[@class="imgpt"]'):
        try:
            img_format = result.xpath('./div[contains(@class, "img_info")]/span/text()')[0]
            # Microsoft seems to experiment with this code so don't make the path too specific,
            # just catch the text section for the first anchor in img_info assuming this to be
            # the originating site.
            source = result.xpath('./div[contains(@class, "img_info")]//a/text()')[0]

            m = loads(result.xpath('./a/@m')[0])

            # strip 'Unicode private use area' highlighting, they render to Tux
            # the Linux penguin and a standing diamond on my machine...
            title = m.get('t', '').replace('\ue000', '').replace('\ue001', '')
            results.append({'template': 'images.html',
                            'url': m['purl'],
                            'thumbnail_src': m['turl'],
                            'img_src': m['murl'],
                            'content': '',
                            'title': title,
                            'source': source,
                            'img_format': img_format})
        except:
            continue

    return results
