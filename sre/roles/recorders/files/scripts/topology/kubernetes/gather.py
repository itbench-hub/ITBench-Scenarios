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


def main():
    endpoint = os.environ.get("KUBERNETES_TOPOLOGY_MONITOR_ENDPOINT")
    if endpoint is None:
        sys.exit("error: KUBERNETES_TOPOLOGY_MONITOR_ENDPOINT environment variable is not set")

    headers = { "Content-Type": "application/json" }

    retries = Retry(total=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retries)

    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    while True:
        next_datetime = datetime.now() + timedelta(seconds=180)

        for item in ["nodes", "edges", "graph", "events"]:
            response = session.get("{0}/{1}".format(endpoint, item), headers=headers, verify=True)

            if response.status_code != 200:
                logger.warning("unable to query kubernetes topology mapper for {0}".format(item))
            else:
                content = response.json()

                logger.info("retrieved {0} data".format(item))

                utc_seconds = (datetime.now(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
                file_path = os.path.join(os.path.expanduser("~"), "records", "{0}-{1}.json".format(round(utc_seconds), item))

                with open(file_path, "w") as f:
                    json.dump(content, f, indent=4)

        sleep_interval = (next_datetime - datetime.now()).total_seconds()
        if sleep_interval > 0:
            logger.debug("sleep for {0} seconds".format(sleep_interval))
            time.sleep(sleep_interval)

if __name__ == "__main__":
    main()
