# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Bing (Web)
"""

import re
from urllib.parse import urlencode
from lxml import html
from searx import logger
from random import randrange
from searx.utils import eval_xpath, extract_text, match_language

logger = logger.getChild('bing engine')

# about
about = {
    "website": 'https://www.bing.com',
    "wikidata_id": 'Q182496',
    "official_api_documentation": 'https://www.microsoft.com/en-us/bing/apis/bing-web-search-api',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['general']
paging = True
supported_languages_url = 'https://www.bing.com/account/general'
language_aliases = {'zh-CN': 'zh-CHS', 'zh-TW': 'zh-CHT', 'zh-HK': 'zh-CHT'}

# search-url
base_url = 'https://www.bing.com/'
search_string = 'search?{query}&first={offset}'

# safesearch definitions
safesearch_types = {2: 'STRICT',
                    1: 'DEMOTE',
                    0: 'OFF'}


def _get_offset_from_pageno(pageno):
    return (pageno - 1) * 10 + 1


# do search-request
def request(query, params):
    offset = _get_offset_from_pageno(params.get('pageno', 0))

    if params['language'] == 'all':
        lang = 'EN'
    else:
        lang = match_language(params['language'], supported_languages, language_aliases)

    query = 'language:{} {}'.format(lang.split('-')[0].upper(), query)

    search_path = search_string.format(
        query=urlencode({'q': query}),
        offset=offset)

    params['url'] = base_url + search_path

    language = match_language(params['language'], supported_languages, language_aliases, 'en').lower()

    HV = randrange(1e10, 1e11)
    WTS = randrange(1e11, 1e12)
    CW = randrange(1e4, 1e5)
    CH = randrange(1e3, 1e5)

    params['cookies']['SRCHHPGUSR'] = \
        f'SRCHLANG={language}&BRW=XW&BRH=M&CW={CW}&CH={CH}&DPR=1&UTC=-180&DM=1&HV={HV}&WTS={WTS}&ADLT=' \
        + safesearch_types.get(params['safesearch'], 'DEMOTE')
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

    return params


# get response from search-request
def response(resp):
    results = []
    result_len = 0

    dom = html.fromstring(resp.text)
    # parse results
    for result in eval_xpath(dom, '//div[@class="sa_cc"]'):
        link = eval_xpath(result, './/h3/a')[0]
        url = link.attrib.get('href')
        title = extract_text(link)
        content = extract_text(eval_xpath(result, './/p'))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # parse results again if nothing is found yet
    for result in eval_xpath(dom, '//li[@class="b_algo"]'):
        link = eval_xpath(result, './/h2/a')[0]
        url = link.attrib.get('href')
        title = extract_text(link)
        content = extract_text(eval_xpath(result, './/p'))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    try:
        result_len_container = "".join(eval_xpath(dom, '//span[@class="sb_count"]//text()'))
        if "-" in result_len_container:
            # Remove the part "from-to" for paginated request ...
            result_len_container = result_len_container[result_len_container.find("-") * 2 + 2:]

        result_len_container = re.sub('[^0-9]', '', result_len_container)
        if len(result_len_container) > 0:
            result_len = int(result_len_container)
    except Exception as e:
        logger.debug('result error :\n%s', e)

    if result_len and _get_offset_from_pageno(resp.search_params.get("pageno", 0)) > result_len:
        return []

    results.append({'number_of_results': result_len})
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    lang_tags = set()

    setmkt = re.compile('setmkt=([^&]*)')
    dom = html.fromstring(resp.text)
    lang_links = eval_xpath(dom, "//li/a[contains(@href, 'setmkt')]")

    for a in lang_links:
        href = eval_xpath(a, './@href')[0]
        match = setmkt.search(href)
        l_tag = match.groups()[0]
        _lang, _nation = l_tag.split('-', 1)
        l_tag = _lang.lower() + '-' + _nation.upper()
        lang_tags.add(l_tag)

    return list(lang_tags)
