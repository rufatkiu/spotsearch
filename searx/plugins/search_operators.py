import shlex

from flask_babel import gettext

name = gettext("Search operators")
description = gettext(
    """Filter results using hyphen, site: and -site:.
Please note that you might get less results with the additional filtering."""
)
default_on = False


def on_result(request, search, result):
    q = search.search_query.query
    qs = shlex.split(q)
    spitems = [x.lower() for x in qs if " " in x]
    mitems = [x.lower() for x in qs if x.startswith("-")]
    siteitems = [x.lower() for x in qs if x.startswith("site:")]
    msiteitems = [x.lower() for x in qs if x.startswith("-site:")]
    url, title, content = (
        result["url"].lower(),
        result["title"].lower(),
        (result.get("content").lower() if result.get("content") else ""),
    )
    if all((x not in title or x not in content) for x in spitems):
        return False
    if all((x in title or x in content) for x in mitems):
        return False
    if all(x not in url for x in siteitems):
        return False
    if all(x in url for x in msiteitems):
        return False
    return True
