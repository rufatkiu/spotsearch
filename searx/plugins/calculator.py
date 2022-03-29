from searx import logger
from numexpr import evaluate

name = "Calculator"
# TODO: translate the following line
description = 'This plugin extends results when the query is a mathematical expression'
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
        return True
    try:
        query = search.search_query.query.lower()
        query = query.replace("x", "*")

        # Not going to compute if no numbers are present
        if not any(i.isdigit() for i in query):
            return True

        # Not going to compute the result if the query is too big
        if len(query) > 30:
            return True
        
        # Not going to compute the result if the query is not within permissible range
        if is_really_big(query):
            raise OverflowError

        code = evaluate(query).item()
        if type(code) in (int, float):
            search.result_container.answers.clear()
            # TODO: translate the following line
            answer = "The value of {} is {}".format(query, code)
            search.result_container.answers[answer] = {'answer': str(answer)}
    except (ZeroDivisionError, ValueError, FloatingPointError, MemoryError) as e:
        logger.debug(e)
        # TODO: translate the following line
        search.result_container.answers[f'Please recheck the above query: {e}'] = {'answer': None}
        return False
    except OverflowError as e:
        logger.debug(e)
        # TODO: translate the following line
        search.result_container.answers[f'Please recheck the above query: Too big to compute {e}'] = {'answer': None}
        return False
    except (SyntaxError, NameError, TypeError) as e:
        logger.debug(e)
        # TODO: translate the following line
        search.result_container.answers[f'Please recheck syntax of above query'] = {'answer': None}
        return False
    except Exception as e:
        logger.debug(e)
        return False
    return True


check_if_loaded()
