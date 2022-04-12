from searx import logger
from numexpr import evaluate
from flask_babel import gettext


name = gettext('Calculator')
description = gettext('This plugin extends results when the query is a mathematical expression')
default_on = True
logger = logger.getChild("calculator")


def check_if_loaded():
    logger.debug("initializing calculator plugin")


def is_really_big(query):
    # For cases like 2**99999**9999
    if len(query.split("**")) >= 3:
        return True
    # Add more cases if needed
    return False


def post_search(request, search):
    if search.search_query.pageno > 1:
        return
    try:
        query = search.search_query.query.lower()
        unmodified_query = query
        query = query.replace("x", "*")
        query = query.replace("^", "**")

        # Not going to compute if only one number is present
        try:
            x = int(query) or float(query)
            return
        except ValueError:
            pass

        # Not going to compute if no numbers are present
        if not any(i.isdigit() for i in query):
            return

        # Not going to compute the result if the query is too big
        if len(query) > 30:
            return

        # Not going to compute the result if the query is not within permissible range
        if is_really_big(query):
            raise OverflowError

        value = evaluate(query).item()
        if type(value) in (int, float):
            search.result_container.answers.clear()
            answer = "{} = {}".format(unmodified_query, value)
            search.result_container.answers[answer] = {'answer': answer, 'calculator': True}
    except (ZeroDivisionError, ValueError, FloatingPointError, MemoryError, OverflowError) as e:
        answer = gettext('Error')
        search.result_container.answers[answer] = {'answer': answer, 'calculator': True}
    except Exception as e:
        logger.debug(e)

    return


check_if_loaded()
