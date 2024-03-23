from netmiko import ConnectHandler
from rich.progress import Progress


def run_commands(commands, username, password, device_type):
    outputs = []

    with Progress() as progress:
        for device, cmds in commands.items():
            task = progress.add_task(
                f"Running commands on {device}...", total=len(cmds)
            )

            try:
                device_config = {
                    "device_type": device_type,
                    "ip": device,
                    "username": username,
                    "password": password,
                }

                # Establish an SSH connection to the device
                with ConnectHandler(**device_config) as ssh:
                    ssh.enable()
                    # Send the commands to the device and capture the output
                    output = ssh.send_config_set(cmds)
                    outputs.append(f"Hostname: {device}\n{output}")

                progress.update(task, advance=len(cmds))

            except Exception as e:
                outputs.append(
                    f"Hostname: {device}\nThe following error occurred while attempting to connect or run commands on the device: {str(e)}"
                )

    return "\n\n".join(outputs)
