import argparse
import json
import os
from pathlib import Path

import requests
from ratelimit import limits, sleep_and_retry
from retrying import retry

import boomi_cicd
from boomi_cicd import logger


def parse_json(file_path):
    """
    Parse a JSON file and return the parsed data.

    :param file_path: The path to the JSON file.
    :type file_path: str
    :return: The parsed data from the JSON file.
    :rtype: dict or list
    """
    data = open_json_file(file_path)
    return data


def parse_release(file_path):
    """
    Parse a release file and return the parsed data.

    :param file_path: The path to the release file.
    :type file_path: str
    :return: The parsed data from the release file.
    :rtype: dict
    """
    file_path = os.path.join(boomi_cicd.RELEASE_BASE_DIR, file_path)
    logger.info(f"Parsing release file: {file_path}")
    data = open_json_file(file_path)
    return data


def open_json_file(file_path):
    """
    Open a JSON file and return the parsed data.
    Function used to sanatize the file path and check if the file exists.
    :param file_path:
    :return: JSON data from file path.
    :rtype: dict
    """
    path = Path(file_path).resolve()
    logger.info(f"Opening file: {path}")
    if not path.is_file():
        raise FileNotFoundError(
            "Invalid file_path: The provided path does not exist or is not a file."
        )
    with path.open("r") as f:
        data = json.load(f)
    return data


def parse_args():
    """Will parse arguments from the command line. Looks for a release file with a -r or --release argument."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--release")
    args = parser.parse_args()
    return args


def set_release():
    """
    Set the release data based on command-line arguments or environment variable.

    This function retrieves the release data from either the command-line argument or the default configuration.
    If the `--release` argument is provided, it reads the JSON data from the specified file path.
    Otherwise, it reads the JSON data from the default release file path.

    :return: The release data as a dictionary.
    """
    args = parse_args()
    if args.release:
        return parse_json(args.release)
    else:
        if boomi_cicd.RELEASE_FILE is not None:
            release_file = boomi_cicd.RELEASE_FILE
        else:
            raise ValueError("No release file specified.")
        return parse_release(release_file)


def set_env_release():
    """
    Set the environment extensions release data based on the BOOMI_ENV_RELEASE_FILE environment variable.

    This function retrieves the environment extensions release file.

    :return: The environment extensions release data as a dictionary.
    """
    if boomi_cicd.ENV_RELEASE_FILE is not None:
        release_file = boomi_cicd.ENV_RELEASE_FILE
    else:
        raise ValueError("No environment extensions release file specified.")
    return parse_release(release_file)


@sleep_and_retry
@limits(calls=boomi_cicd.CALLS_PER_SECOND, period=boomi_cicd.RATE_LIMIT_SECONDS)
def check_limit():
    """
    Empty function to limit the number of calls to the Atomsphere API.

    This function is used as a decorator to enforce a rate limit on API calls. It ensures that the decorated function
    is called within the specified rate limit.

    :return: None
    """
    return


@retry(
    stop_max_attempt_number=3,
    wait_fixed=boomi_cicd.RATE_LIMIT_MILLISECONDS,
    retry_on_result=lambda x: x == 503,
)
def requests_get_xml(resource_path):
    """
    DEPRECIATED. Perform a GET request to the Atomsphere API and retrieve XML data.

    :param resource_path: The resource path for the API endpoint.
    :type resource_path: str
    :return: The response object containing the XML data.
    :rtype: requests.Response
    :raises requests.HTTPError: If the GET request fails (non-2xx response). A 503 response will be retried up to 3 times.
    """
    check_limit()
    logger.info(resource_path)
    headers = {"Accept": "application/xml"}
    url = boomi_cicd.BASE_URL + "/" + boomi_cicd.ACCOUNT_ID + resource_path

    response = requests.get(
        url, auth=(boomi_cicd.USERNAME, boomi_cicd.PASSWORD), headers=headers
    )
    logger.info(
        "Response: {}".format(response.text.replace("\r", "").replace("\n", ""))
    )

    response.raise_for_status()
    return response


@retry(
    stop_max_attempt_number=3,
    wait_fixed=boomi_cicd.RATE_LIMIT_MILLISECONDS,
    retry_on_result=lambda x: x == 503,
)
def requests_get(resource_path):
    """
    DEPRECIATED. Perform a GET request to the Atomsphere API and retrieve JSON data.

    :param resource_path: The resource path for the API endpoint.
    :type resource_path: str
    :return: The response object containing the JSON data.
    :rtype: requests.Response
    :raises requests.HTTPError: If the GET request fails (non-2xx response).  A 503 response will be retried up to 3 times.
    """
    check_limit()
    logger.info(resource_path)
    headers = {"Accept": "application/json"}
    url = boomi_cicd.BASE_URL + "/" + boomi_cicd.ACCOUNT_ID + resource_path

    response = requests.get(
        url, auth=(boomi_cicd.USERNAME, boomi_cicd.PASSWORD), headers=headers
    )
    logger.info("Response: {}".format(response.text))
    response.raise_for_status()
    return response


@retry(
    stop_max_attempt_number=3,
    wait_fixed=boomi_cicd.RATE_LIMIT_MILLISECONDS,
    retry_on_result=lambda x: x == 503,
)
def requests_post(resource_path, payload):
    """
    DEPRECIATED. Perform a POST request to the Atomsphere API with the specified payload.

    :param resource_path: The resource path for the API endpoint.
    :type resource_path: str
    :param payload: The payload to be sent in the request body (as JSON).
    :type payload: dict
    :return: The response object containing the JSON response data.
    :rtype: requests.Response
    :raises requests.HTTPError: If the POST request fails (non-2xx response). A 503 response will be retried up to 3 times.
    """
    check_limit()
    logger.info(resource_path)
    logger.info("Request: {}".format(json.dumps(payload)))
    headers = {"Accept": "application/json"}
    url = boomi_cicd.BASE_URL + "/" + boomi_cicd.ACCOUNT_ID + resource_path

    response = requests.post(
        url,
        auth=(boomi_cicd.USERNAME, boomi_cicd.PASSWORD),
        json=payload,
        headers=headers,
    )
    logger.info("Response: {}".format(response.text))
    response.raise_for_status()
    return response


@retry(
    stop_max_attempt_number=3,
    wait_fixed=boomi_cicd.RATE_LIMIT_MILLISECONDS,
    retry_on_result=lambda x: x == 503,
)
def requests_post_xml(resource_path, payload):
    """
    DEPRECIATED. Perform a POST request to the Atomsphere API with the specified payload.

    :param resource_path: The resource path for the API endpoint.
    :type resource_path: str
    :param payload: The payload to be sent in the request body as XML.
    :type payload: str
    :return: The response object containing the JSON response data.
    :rtype: requests.Response
    :raises requests.HTTPError: If the POST request fails (non-2xx response). A 503 response will be retried up to 3 times.
    """
    check_limit()
    logger.info(resource_path)
    logger.info("Request: {}".format(payload))
    headers = {"Accept": "application/xml", "Content-Type": "application/xml"}
    url = boomi_cicd.BASE_URL + "/" + boomi_cicd.ACCOUNT_ID + resource_path

    response = requests.post(
        url,
        auth=(boomi_cicd.USERNAME, boomi_cicd.PASSWORD),
        data=payload,
        headers=headers,
    )
    logger.info("Response: {}".format(response.text))
    response.raise_for_status()
    return response.text


@retry(
    stop_max_attempt_number=3,
    wait_fixed=boomi_cicd.RATE_LIMIT_MILLISECONDS,
    retry_on_result=lambda x: x == 503,
)
def requests_delete(resource_path):
    """
    DEPRECIATED. Perform a DELETE request to the Atomsphere API.

    :param resource_path: The resource path for the API endpoint.
    :type resource_path: str
    :return: The response object containing the JSON response data.
    :rtype: requests.Response
    :raises requests.HTTPError: If the DELETE request fails (non-2xx response). A 503 response will be retried up to 3 times.
    """
    check_limit()
    logger.info(resource_path)
    headers = {"Accept": "application/json"}
    url = boomi_cicd.BASE_URL + "/" + boomi_cicd.ACCOUNT_ID + resource_path

    response = requests.delete(
        url, auth=(boomi_cicd.USERNAME, boomi_cicd.PASSWORD), headers=headers
    )
    logger.info("Response: {}".format(response.text))
    response.raise_for_status()
    return response


# This function will be used going forward.
@retry(
    stop_max_attempt_number=3,
    wait_fixed=boomi_cicd.RATE_LIMIT_MILLISECONDS,
    retry_on_result=lambda x: x == 503,
)
def atomsphere_request(
    *,
    method,
    resource_path,
    payload=None,
    accept_header="application/json",
    pass_error=False,
):
    """
    Perform a request to the Atomsphere API.

    :param method: The HTTP method for the request. \
    Accepted values: get, post, put, delete.
    :type method: str
    :param resource_path: The resource path for the API endpoint.
    :type resource_path: str
    :param payload: The payload to be sent in the request body.
    :type payload: dict or str, optional
    :return: The response object containing the response data.
    :param accept_header: The HTTP Accept Header for the request.
    :type accept_header: str, defaults to "application/json"
    :param pass_error: Determine if an error should be passed.\
    If False, an non-2xx response with throw an error.\
    If True, the errow will be passed to the calling function.
    :rtype: requests.Response
    :raises requests.HTTPError: If the request fails (non-2xx response). A 503 response will be retried up to 3 times.
    """
    check_limit()
    logger.info(resource_path)
    logger.info("Request: {}".format(payload))
    headers = {"Accept": accept_header, "Content-Type": accept_header}
    url = boomi_cicd.BASE_URL + "/" + boomi_cicd.ACCOUNT_ID + resource_path

    response = getattr(requests, method.lower())(
        url,
        auth=(boomi_cicd.USERNAME, boomi_cicd.PASSWORD),
        data=payload if isinstance(payload, str) else json.dumps(payload),
        headers=headers,
    )
    logger.info("Response: {}".format(response.text))
    if not pass_error:
        response.raise_for_status()
    return response
