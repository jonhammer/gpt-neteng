import argparse
from getpass import getpass


def get_arguments():
    parser = argparse.ArgumentParser(description="gpt-neteng CLI")
    parser.add_argument(
        "--topology",
        type=str,
        help="Topology file (txt or image) containing device names and whatever topology information you want",
    )
    parser.add_argument(
        "--task", type=str, help="Text file containing the task to complete"
    )
    parser.add_argument("--username", type=str, help="Username for device connection")
    parser.add_argument("--password", type=str, help="Password for device connection")
    parser.add_argument(
        "--device-type", type=str, default="arista_eos", help="Device type"
    )
    parser.add_argument("--loglevel", type=str, default="WARNING", help="Logging level")
    parser.add_argument("--logfile", type=str, default=None, help="Log file")
    parser.add_argument(
        "--auto-run",
        action="store_true",
        help="Run commands without confirmation",
        default=False,
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=50,
        help="Maximum iterations to allow before stopping",
    )
    args = parser.parse_args()

    if not args.topology:
        args.topology = input(
            "Provide a description of the topology, or a path to a file containing the topology: "
        )

    if not args.username:
        args.username = input("Please enter the username for device connection: ")

    if not args.password:
        args.password = getpass("Please enter the password for device connection: ")

    if not args.device_type:
        args.device_type = input("Please enter the device type: ")

    if not args.task:
        args.task = input("Please describe the issue you need assistance with: ")

    return args
