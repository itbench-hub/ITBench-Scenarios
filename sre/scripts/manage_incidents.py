import argparse
import logging
import os
import sys
import time

import ansible_runner
import yaml

# Logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)

# Argument Parsing
parser = argparse.ArgumentParser(
    description="CLI for asynchronous fault injection for live ITBench SRE and FinOps scenarios"
)
parser.add_argument(
    "--private_project_directory",
    help="path to the directory of the project",
    required=True,
    type=str
)
parser.add_argument(
    "--incident_spec_file",
    help="path to the incident spec yaml file",
    required=True,
    type=str
)
parser.add_argument(
    "--run_tags",
    help="Ansible playbook tags",
    required=True,
    type=str
)

def main():
    args = parser.parse_args()

    try:
        spec = {}
        with open(args.incident_spec_file) as f:
            spec = yaml.safe_load(f)
    except:
        logger.exception("incident spec loading failure: {0}".format(sys.exception()))
        sys.exit("error: incident spec failed to load.")

    runners = []

    for group in range(0, len(spec["spec"]["faults"])):
        logger.info("start fault tasks for group {0}".format(group))

        _, runner = ansible_runner.interface.run_async(
            private_data_dir=args.private_project_directory,
            playbook="manage_incident_faults.yaml",
            ident="incident-{0}-fault-{1}".format(
                spec["metadata"]["id"],
                group
            ),
            cmdline="--tags {0} --extra-vars incident_id={1} --extra-vars fault_group={2}".format(
                args.run_tags,
                spec["metadata"]["id"],
                group
            )
        )
        runners.append(runner)

    for r in runners:
        logger.debug("waiting for runner to complete tasks")

        while r.status not in ['canceled', 'successful', 'timeout', 'failed']:
            time.sleep(1)
            continue

    logger.info("all fault tasks have been completed")

if __name__ == "__main__":
    main()
