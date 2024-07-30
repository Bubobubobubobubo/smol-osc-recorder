# Smol OSC Recorder

A CLI tool to record Open Sound Control (OSC) messages, with optional message forwarding.

## Features

- Record OSC messages.
    - Forward messages to multiple ports.
    - Quantize messages if needed.
    - Display messages on the terminal.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/bubobubobubobubo/osc-recorder.git
```

2. Navigate to the project directory:

```sh
cd osc-recorder
```

3. Install the required dependencies:

```sh
pip install -m install .
```

## Usage

Run the `record_osc` command with the necessary options:

```sh
python -m osc_recorder.record_osc --address <ADDRESS> --port <PORT> --file <FILE_PATH> --scheme <SCHEME> [--repeaters <PORTS>] [--quantized]
```

### Options

- `--address` (required): The address to listen to.
- `--port` (required): The port to listen to.
- `--file` (required): Path to the final file that will contain the recording.
- `--scheme` (required): Specify a specific schema.
- `--repeaters`: Comma-separated list of ports to forward the received messages to. If not specified, no forwarding will occur.
- `--quantized`: Quantize the recording so that the first message starts at time 0.

## Schemes

Schemes define how the OSC messages are processed and recorded. You can specify a scheme using the `--scheme` option. The available schemes are:

- `dirt_basic`: A basic schema for recording OSC messages, taking the first element of the args.
- `dirt_strip`: Returns only odd arguments from the args.
- `basic`: A basic schema for recording OSC messages, including all arguments.
- `only_numbers`: Returns only numerical arguments (integers and floats) from the args.

Each scheme is defined as a function that processes the OSC message's address and arguments, returning a dictionary with the processed data. You can extend or modify these schemes by editing the `ALL_SCHEMES` dictionary in the code.

### Example

```sh
python -m osc_recorder.record_osc --address 127.0.0.1 --port 8000 --file recordings.json --scheme basic --repeaters 8001,8002 --quantized
```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Python-OSC](https://github.com/attwad/python-osc) for the OSC library.
- [Click](https://click.palletsprojects.com/) for the command-line interface.
- [Colorama](https://pypi.org/project/colorama/) for colored terminal output.