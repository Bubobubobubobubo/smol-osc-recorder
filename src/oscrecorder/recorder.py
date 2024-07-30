"""A CLI tool to record OSC messages."""

import os
import json
import socket
import time
from typing import List, Dict, Tuple, Any
import click
from pythonosc import dispatcher, osc_server, udp_client
from colorama import Fore, Style, init
from .scheme import ALL_SCHEMES

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def record_message(
    address: str,
    args: Tuple[Any, ...],
    start_time: float,
    messages: List[Dict[str, Any]],
    clients: List[udp_client.SimpleUDPClient],
    scheme: str,
    repeater_ports: List[int],
) -> None:
    """Record the message, print it for the user, and forward if repeaters are specified.

    Args:
        address (str): The OSC address.
        args (Tuple[Any, ...]): The OSC message arguments.
        start_time (float): The start time of the recording.
        messages (List[Dict[str, Any]]): List to store recorded messages.
        clients (List[udp_client.SimpleUDPClient]): List of OSC clients for repeating messages.
        scheme (str): The schema used for processing messages.
        repeater_ports (List[int]): List of ports to forward messages to.
    """
    elapsed_time = time.perf_counter() - start_time
    message = ALL_SCHEMES[scheme](address, args)
    message["time"] = elapsed_time
    messages.append(message)
    clear_screen_and_display_messages(messages)

    if repeater_ports:
        for client in clients:
            client.send_message(address, args)


def clear_screen_and_display_messages(messages: List[Dict[str, Any]]) -> None:
    """Clear the screen and display the last 10 messages with alternating colors.

    Args:
        messages (List[Dict[str, Any]]): List of recorded messages.
    """
    os.system("cls" if os.name == "nt" else "clear")
    for i, msg in enumerate(messages[-10:]):
        color = Fore.GREEN if i % 2 == 0 else Fore.YELLOW
        print(f"{color}Recorded message: {msg}{Style.RESET_ALL}")


def process_messages(
    messages: List[Dict[str, Any]], quantized: bool
) -> List[Dict[str, Any]]:
    """Process the messages before saving to file.

    Args:
        messages (List[Dict[str, Any]]): List of recorded messages.
        quantized (bool): Whether to quantize the messages or not.

    Returns:
        List[Dict[str, Any]]: Processed list of messages.
    """
    if quantized and messages:
        offset = messages[0]["time"]
        for message in messages:
            message["time"] -= offset
    return messages


class ReusableOSCUDPServer(osc_server.ThreadingOSCUDPServer):
    """A subclass of ThreadingOSCUDPServer that allows the reuse of the server address."""

    def server_bind(self) -> None:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


@click.command()
@click.option("--address", required=True, help="The address to listen to.")
@click.option("--port", required=True, type=int, help="The port to listen to.")
@click.option(
    "--file",
    "file_path",
    required=True,
    help="Path to the final file that will contain the recording.",
)
@click.option("--scheme", required=True, help="Specify a specific schema.")
@click.option(
    "--repeaters",
    type=str,
    help="Comma-separated list of ports to forward the received messages to. If not specified, no forwarding will occur.",
)
@click.option(
    "--quantized",
    is_flag=True,
    default=False,
    help="Quantize the recording so that the first message starts at time 0.",
)
def record_osc(
    address: str,
    port: int,
    file_path: str,
    scheme: str = "basic",
    repeaters: str = None,
    quantized: bool = False,
) -> None:
    """A CLI tool to record OSC messages.

    Args:
        address (str): The address to listen to.
        port (int): The port to listen to.
        file_path (str): Path to the final file that will contain the recording.
        scheme (str): Specify a specific schema.
        repeaters (str): Comma-separated list of ports to forward the received messages to. If not specified, no forwarding.
        quantized (bool): Quantize the recording so that the first message starts at time 0.
    """
    start_time = time.perf_counter()
    messages: List[Dict[str, Any]] = []
    repeater_ports = list(map(int, repeaters.split(","))) if repeaters else []

    clients = [udp_client.SimpleUDPClient(address, port) for port in repeater_ports]

    disp = dispatcher.Dispatcher()
    disp.map(
        "/*",
        lambda addr, *args: record_message(
            addr, args, start_time, messages, clients, scheme, repeater_ports
        ),
    )

    server = ReusableOSCUDPServer((address, port), disp)
    print(f"Recording on {server.server_address}", end=" ")

    if repeater_ports:
        print(f"and repeating messages to ports {', '.join(map(str, repeater_ports))}")
    print("\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
        server.shutdown()
        processed_messages = process_messages(messages, quantized)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(processed_messages, f, indent=4)
        print(f"Recording saved to {file_path}")
