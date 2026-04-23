import json

import boomi_cicd
import boomi_cicd.util.json.environment
from boomi_cicd import logger


# https://help.boomi.com/bundle/developer_apis/page/r-atm-Environment_object.html


def query_environment(environment_name):
    """
    Query the Boomi environment by name to retrieve the environment ID.

    :param environment_name: The name of the Boomi environment.
    :type environment_name: str
    :return: The environment ID.
    :rtype: str
    :raises SystemExit: If the environment is not found.
    """
    resource_path = "/Environment/query"

    payload = boomi_cicd.util.json.environment.query()
    payload["QueryFilter"]["expression"]["argument"][0] = environment_name

    response = boomi_cicd.requests_post(resource_path, payload)

    json_response = json.loads(response.text)
    if json_response["numberOfResults"] == 0:
        logger.error(f"Environment not found. EnvironmentName: {environment_name}")
        raise ValueError(f"Environment not found. Environment Name: {environment_name}")
    environment_id = json_response["result"][0]["id"]
    return environment_id
