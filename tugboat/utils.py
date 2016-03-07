# encoding: utf-8
"""
Utility methodss
"""


def get_post_data(request, types={}):
    """
    Attempt to coerce POST json data from the request, falling
    back to the raw data if json could not be coerced.
    :param request: flask.request
    :param types: types that the incoming request object must cohere to

    :return: dict
    """
    try:
        post_data = request.get_json(force=True)
    except:
        post_data = request.values

    if types and isinstance(post_data, dict):
        for expected_key in types:
            if expected_key not in post_data.keys():
                continue

            if not isinstance(post_data[expected_key],
                              types[expected_key]):
                raise TypeError(
                    '{0} should be type {1} but is {2}'
                    .format(expected_key,
                            types[expected_key],
                            type(post_data[expected_key]))
                )

    return post_data
