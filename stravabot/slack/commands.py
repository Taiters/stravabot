from dataclasses import dataclass
from typing import Callable

def connect(ack):
    ack("Connect")

def disconnect(ack):
    ack("disconnect")

def kick(ack):
    ack("kick")

def setup_commands(command: Callable[[str, str], Callable]):
    command("connect", "Connect to Strava")(connect)
    command("disconnect", "Disconnect from Strava")(disconnect)
    command("kick", "Kick me")(kick)