import datetime
import json
import logging
import os
import sys
import time

from datetime import datetime, timedelta, timezone

import requests

from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger(__name__)

def get_services(session, endpoint, headers):
    response = session.get(
        "{0}/api/services".format(endpoint),
        headers=headers,
        verify=True
    )

    if response.status_code != 200:
        logger.warning("unable to query jaeger for services")
        return []

    content = response.json()
    return content.get("data", [])

def get_operations(session, endpoint, headers, service):
    response = session.get(
        "{0}/api/operations".format(endpoint),
        headers=headers,
        params={
            'service': service,
        },
        verify=True
    )

    if response.status_code != 200:
        logger.warning("unable to query jaeger for operations related to {0}".format(service))
        return []

    content = response.json()
    return content.get("data", [])

def get_traces(session, endpoint, headers, service, operation, time_window):
    name = operation.get("name")
    if name is None:
        logger.warning("unable to discover name of operation: {0}".format(operation))
        return []

    response = session.get(
        "{0}/api/traces".format(endpoint),
        headers=headers,
        params={
            'service': service,
            "operation": name,
            "start": time_window[0],
            "end": time_window[1],
            "limit": 1
        },
        verify=True
    )

    if response.status_code != 200:
        logger.warning("unable to query jaeger for traces related to operation ({0})".format(name))
        return []

    content = response.json()
    return content.get("data", [])

def main():
    endpoint = os.environ.get("JAEGER_ENDPOINT")
    if endpoint is None:
        sys.exit("error: JAEGER_ENDPOINT environment variable is not set")

    headers = { "Content-Type": "application/json" }

    retries = Retry(total=3, backoff_factor=0.1)
    adapter = HTTPAdapter(max_retries=retries)

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    while True:
        next_datetime = datetime.now() + timedelta(seconds=300)

        traces = []

        end_time = int(time.time_ns() // 1000)
        start_time = end_time - (300 * 1_000_000)

        services = get_services(session, endpoint, headers)
        logger.info("retrieved {0} services from jaeger".format(len(services)))

        for service in services:
            operations = get_operations(session, endpoint, headers, service)
            logger.info("retrieved {0} operations from jaeger".format(len(operations)))

            for operation in operations:
                t = get_traces(session, endpoint, headers, service, operation, (start_time, end_time))
                logger.info("retrieved {0} traces from jaeger".format(len(ts)))

                traces.extend(t)

        if len(traces) > 0:
            utc_seconds = (datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
            file_path = os.path.join(os.path.expanduser("~"), "records", "{0}-traces.json".format(round(utc_seconds)))

            with open(file_path, "w") as f:
                json.dump(traces, f, indent=4)

        sleep_interval = (next_datetime - datetime.now()).total_seconds()
        if sleep_interval > 0:
            logger.debug("sleep for {0} seconds".format(sleep_interval))
            time.sleep(sleep_interval)

if __name__ == "__main__":
    main()
