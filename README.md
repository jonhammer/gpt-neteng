# gpt-neteng

The first AI Network Engineer

[![GitHub](https://img.shields.io/github/license/jonhammer/gpt-neteng)](https://github.com/jonhammer/gpt-neteng/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/jonhammer/gpt-neteng)](https://github.com/jonhammer/gpt-neteng/issues)
[![GitHub stars](https://img.shields.io/github/stars/jonhammer/gpt-neteng)](https://github.com/jonhammer/gpt-neteng/stargazers)

## Description
gpt-neteng is the first AI-powered Network Engineer that can troubleshoot and configure live network devices on it's own, with or without human guidance along the way.

## Features
- Real-time AI-driven troubleshooting and configuration of actual network devices
- Intelligent analysis and decision-making based on output data (show commands, etc.) from devices
- Support for various network devices and technologies

## Requirements

- Python 3.9+
- [Anthropic](https://www.anthropic.com/) API key
- SSH access to network lab devices (or production devices if you are an insane person)

## Lab Environment

I highly recommend using [ContainerLab](https://containerlab.srlinux.dev/) for setting up local lab environments.

In my testing I used [cEOS](https://www.arista.com/en/support/software-download).

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jonhammer/gpt-neteng.git
   ```

2. Change to the project directory:
   ```
   cd gpt-neteng
   ```

3. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install the package:
   ```
   pip install .
   ```

5. Create a `.env` file in the project root and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
   
## Usage

### CLI

To run the gpt-neteng CLI, use the following command:
```
gpt-neteng [options]
```

If no arguments are provided, the CLI will prompt you interactively for the required information.

#### Options

- `--topology`: Path to the topology file (txt or image)
- `--task`: Path to the task description file
- `--username`: Username for device connection
- `--password`: Password for device connection
- `--loglevel`: Logging level (default: WARNING)
- `--logfile`: Path to the log file
- `--auto-run`: Run commands without confirmation

##### Example

```
gpt-neteng --topology example-lab.jpg --task example-task.txt --username admin --password admin
```

### Docker

Not currently recommended, web app coming soon.

To run gpt-neteng using Docker Compose:

1. Build the Docker image:
   ```
   docker compose build
   ```

2. Start the container:
   ```
   docker compose run app
   ```



## Example
### Topology/Device information
First you need to tell gpt-neteng what devices it is working with. In addition to the devices, you can provide a topology image or simple description of the topology, or you can just tell it to try to figure it out on it's own.

In my tests I provided the following expertly crafted topology diagram:

<img src="example-lab.jpg" alt="Lab topology that looks like it was drawn by a toddler" width="500"/>

It also worked well just providing it with the link information from my [ContainerLab](https://containerlab.srlinux.dev/) definition:

```yaml
name: gpt-lab
prefix: ""

topology:
  nodes:
    lab1:
      kind: arista_ceos
      image: ceos:latest
    lab2:
      kind: arista_ceos
      image: ceos:latest
    lab3:
      kind: arista_ceos
      image: ceos:latest
    lab4:
      kind: arista_ceos
      image: ceos:latest

  links:
    - endpoints: ["lab1:eth1", "lab2:eth1"]
    - endpoints: ["lab2:eth2", "lab4:eth2"]
    - endpoints: ["lab1:eth2", "lab3:eth1"]
    - endpoints: ["lab3:eth2", "lab4:eth1"]
```

Alternatively, as long as it has hostnames you can just give it those and have it try to figure out the topology on it's own.

### Problem description

I spun up a blank lab connected as shown above and provided the following description.

```commandline
This is a new lab environment of EOS devices.
It is a lab so use whatever numbering schemas (IP, ASNs, etc) you desire.
Configure all the connected links on our devices as point to point layer 3 links (e.g., /30s between each device).
Configure BGP on all devices and advertise the loopback interfaces into BGP.
When you verify BGP status, be aware of convergence times. It may take a while for BGP to converge, so don't spend too much time troubleshooting if it doesn't come up immediately. Come back to it later.
Ensure reachability from lab1 to lab3 loopback ip. For the lab3 loopback IP use 3.3.3.3
You can configure these steps in whatever order you think is most efficient. There may be some existing configurations on these devices so be aware of that.
When you finish configuration, verify connectivity by running a ping from lab1 to lab3 loopback ip. If you can ping, you are done. If you can't ping, troubleshoot and fix the issue.
Note that "no ip routing" is present in the default config, you will need to enable routing and set no switchport for any configured L3 interfaces.
```

It took a total of **164 seconds** for it to configure and verify everything ***without any human intervention.***

You can see how it worked through the task [here](https://gist.githubusercontent.com/jonhammer/959c7d5dc7348d8d89d5df9652cb29c5/raw/41151bdc65ce3acfdac68bd762f495c04fa5744e/gistfile1.txt).

## How it Works

1. gpt-neteng analyzes the topology and and the task description.
2. It decides on an approach, and iteratively provides the commands it wants to run.
3. At each step, the plan is presented to the user for confirmation (or optionally, without confirmation).
4. gpt-neteng executes the necessary commands on the specified network devices using Netmiko.
5. The output of the commands is captured and analyzed for further action.
6. gpt-neteng iteratively refines the plan based on the command outputs and user feedback.
7. Once the task is completed successfully, a summary of the actions taken is provided.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](https://github.com/jonhammer/gpt-neteng/blob/main/LICENSE).