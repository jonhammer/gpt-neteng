import json
import logging
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from gpt_neteng.args import get_arguments
from gpt_neteng.llm_utils import create_initial_prompt, send_message_to_claude
from gpt_neteng.network_utils import run_commands
from gpt_neteng.util import (
    get_topology_data,
)

console = Console()


def parse_response(response):
    try:
        response_json = json.loads(response, strict=False)
        info = response_json.get("info", "")
        commands = response_json.get("commands", [])
        question = response_json.get("question", "")
        finished = response_json.get("finished", False)
        return info, commands, question, finished
    except json.JSONDecodeError:
        console.print(
            "Error: Unable to parse JSON response from Claude", style="bold red"
        )
        return "", [], "", False


def confirm_commands(commands, auto_run):
    confirm_run_commands = True
    user_feedback = ""
    console.print("[bold blue]Commands to be executed:[/bold blue]")
    user_wait_time = 0
    for device, cmds in commands.items():
        console.print(f"[bold green]Device:[/bold green] {device}")
        console.print("[bold yellow]Commands:[/bold yellow]")
        for cmd in cmds:
            console.print(f"  - {cmd}")
        console.print()

    if not auto_run:
        console.print("[bold red]Please review the commands carefully.[/bold red]")
        console.print(
            "Press [bold green]Enter[/bold green] to continue, or [bold red]Ctrl+C[/bold red] to exit.\nIf you instead want to provide feedback (without running the commands), type it below."
        )
        user_wait_time_start = time.time()

        while True:
            try:
                user_input = console.input("> ")
                if not user_input or user_input == "y":
                    break
                if user_input != "":
                    user_feedback = user_input
                    confirm_run_commands = False
                    break
            except KeyboardInterrupt:
                console.print("\nTask stopped by the user.", style="bold red")
                sys.exit(0)

        user_wait_time_end = time.time()
        user_wait_time = user_wait_time_end - user_wait_time_start

    return confirm_run_commands, user_feedback, user_wait_time


def calculate_time(start_time, user_wait_time):
    end_time = time.time()
    total_time = int(end_time - start_time)
    total_time -= int(user_wait_time)
    return f"{total_time} seconds"


def send_message_to_llm(messages):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Sending message to Claude...", total=None)
        response = send_message_to_claude(messages)
    return response


def get_user_response(prompt):
    user_wait_time_start = time.time()
    user_response = console.input(prompt)
    user_wait_time_end = time.time()
    return user_response, user_wait_time_end - user_wait_time_start


def main():
    args = get_arguments()

    # Set up logging
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.loglevel}")
    if args.logfile:
        logging.basicConfig(
            filename=args.logfile,
            level=numeric_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(
            level=numeric_level, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    logging.debug(f"Starting application...")

    console.print("[bold green]GPT-NetEng[/bold green]")
    console.print("Starting task...\n")

    topology_type, topology_data = get_topology_data(args.topology)

    console.print("[bold blue]Topology Information:[/bold blue]")
    if topology_type == "text":
        console.print(Panel(topology_data, title="Topology", expand=False))
    else:
        console.print(f"Topology image: {args.topology}")

    try:
        with open(args.task, "r") as file:
            task = file.read()
    except FileNotFoundError:
        task = args.task

    console.print("\n[bold blue]Task Description:[/bold blue]")
    console.print(Panel(task, title="Task", expand=False))

    inital_prompt = create_initial_prompt(topology_type, topology_data, task)

    print("")
    try:
        console.input(
            "Begin? (press [bold green]Enter[/bold green] to continue or [bold red]Ctrl+C[/bold red] to exit)."
        )
    except KeyboardInterrupt:
        console.print("Task stopped by the user.", style="bold red")
        sys.exit(0)
    print("")

    start_time = time.time()

    messages = inital_prompt

    user_wait_time = 0

    while True:
        response = send_message_to_llm(messages)
        content = response.content[0].text
        messages.append({"role": "assistant", "content": content})
        info, commands, question, finished = parse_response(content)

        # Debugging
        end_time = time.time()
        logging.debug(f"Elapsed time: {int(end_time - start_time)} seconds")
        logging.debug(f"Response from Claude: {content}")
        logging.debug("Parsed response:")
        logging.debug(f"Info: {info}")
        logging.debug(f"Commands: {commands}")
        logging.debug(f"Question: {question}")
        logging.debug(f"Finished: {finished}")
        # End Debugging

        console.print(Panel(info, title="Response from GPT-NetEng", expand=False))

        if question:
            prompt = f"[bold blue]Question from Claude:[/bold blue] {question}\n[bold green]User Response:[/bold green] "
            user_response, wait_time = get_user_response(prompt)
            user_wait_time += wait_time
            messages.append({"role": "user", "content": user_response})
            continue

        if finished:
            prompt = "Task completed. Would you like to ask for additional assistance? (y/N): "
            user_response, wait_time = get_user_response(prompt)
            user_wait_time += wait_time
            if user_response.lower() != "y":
                console.print(
                    f"Task completed.\nTotal time elapsed (not including time spent waiting on user input): {calculate_time(start_time, user_wait_time)}",
                    style="bold green",
                )
                break
            else:
                prompt = "Please describe the issue you need assistance with: "
                user_response, wait_time = get_user_response(prompt)
                user_wait_time += wait_time
                messages.append({"role": "user", "content": user_response})
                continue

        confirm_run_commands, user_feedback, time_waited = confirm_commands(
            commands, auto_run=args.auto_run
        )
        user_wait_time += time_waited
        if confirm_run_commands:
            command_output = run_commands(
                commands, args.username, args.password, args.device_type
            )
            console.print(
                Panel(
                    Syntax(command_output, "text", theme="monokai", line_numbers=True),
                    title="Command Output",
                )
            )
            messages.append({"role": "user", "content": command_output})
        else:
            messages.append({"role": "user", "content": user_feedback})


if __name__ == "__main__":
    main()
