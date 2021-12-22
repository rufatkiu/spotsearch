# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Bing (Web)
"""

import re
from urllib.parse import urlencode
from lxml import html
from searx import logger
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

    safesearch_value = safesearch_types.get(params['safesearch'], 'DEMOTE')

    params['cookies'] = {
        'SUID': 'M',
        'MUID': '3F25FB51B96768F432B2EA44B81B6980',
        'MUIDB': '3F25FB51B96768F432B2EA44B81B6980',
        '_EDGE_V': '1',
        'SRCHD': 'AF=NOFORM',
        'SRCHUID': 'V=2&GUID=EC616793C71B437DAA4F508DF5133DEE&dmnchg=1',
        '_HPVN': 'CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMS0xMi0yMlQwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIkRmdCI6bnVsbCwiTXZzIjowLCJGbHQiOjAsIkltcCI6Mn0=',
        '_SS': 'SID=2347483D1B9D6F77147D59281AE16ED5&R=0&RB=0&GB=0&RG=0&RP=0',
        'ipv6': 'hit=1640126600313&t=4',
        '_EDGE_S': 'F=1&SID=2347483D1B9D6F77147D59281AE16ED5&mkt=pt-br',
        'SRCHUSR': 'DOB=20211221&T=1640122998000&TPC=1640123002000',
        'BCP': 'AD=1&AL=1&SM=1',
        '_RwBf': 'ilt=6&ihpd=1&ispd=2&rc=0&rb=0&gb=0&rg=0&pc=0&mtu=0&rbb=0&g=0&cid=&v=6&l=2021-12-21T08:00:00.0000000Z&lft=00010101&aof=0&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2021-12-21T21:43:40.1584505+00:00&rwred=0',
        'SRCHHPGUSR': f'SRCHLANG=en&BRW=XW&BRH=T&CW=1920&CH=1011&SW=1920&SH=1080&DPR=1&UTC=-180&DM=1&HV=1640123020&WTS=63775719814&NEWWND=0&NRSLT=-1&LSL=0&AS=1&ADLT={safesearch_value}&NNT=1&HAP=0&VSRO=1',
    }

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
