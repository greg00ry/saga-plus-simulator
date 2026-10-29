import os
import random
import time

from saga_plus_simulator.exceptions.simulated_exceptions import ConnectionLoss, PacketLoss

FAULT_PROBABILITY = float(os.environ["FAIL_PROBABILITY"])
TIMEOUT = float(os.environ["TIMEOUT"])

def inject_connection_loss(step: str) -> None:
    if random.random() > FAULT_PROBABILITY:
        raise ConnectionLoss(step, "inject_connection_loss")

def inject_delay() -> None:
    if random.random() > FAULT_PROBABILITY:
        time.sleep(TIMEOUT)

def packet_loss(step: str) -> None:
    if random.random() > FAULT_PROBABILITY:
        raise PacketLoss(step, "packet_loss")