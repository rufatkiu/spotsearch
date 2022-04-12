from searx import logger
from numexpr import evaluate
from flask_babel import gettext
from wrapt_timeout_decorator import timeout

name = gettext('Calculator')
description = gettext('This plugin extends results when the query is a mathematical expression')
default_on = True
logger = logger.getChild("calculator")


def check_if_loaded():
    logger.debug("initializing calculator plugin")


# Set timeout so that the plugin doesn't hang for long computations
@timeout(5)
def calculate(query):
    return evaluate(query).item()


def post_search(request, search):
    if search.search_query.pageno > 1:
        return
    try:
        query = search.search_query.query.lower()
        unmodified_query = query

        # Replace all frequently used substitutes
        query = query.replace("x", "*")
        query = query.replace("^", "**")
        query = query.replace("%", "*(0.01)*")

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

        # Multiply by float to upcast all numbers to floats
        # https://numexpr.readthedocs.io/projects/NumExpr3/en/latest/user_guide.html#casting-rules
        query += "*1.0"

        value = calculate(query)
        if type(value) in (int, float):
            search.result_container.answers.clear()
            answer = "{} = {}".format(unmodified_query, value)
            search.result_container.answers['calculator'] = {'answer': answer, 'calculator': True}
    except (ZeroDivisionError, ValueError, FloatingPointError, MemoryError, OverflowError, TimeoutError) as e:
        answer = gettext('Error')
        search.result_container.answers['calculator'] = {'answer': answer, 'calculator': True}
    except Exception as e:
        logger.debug(e)

    return


check_if_loaded()
