from fastapi import HTTPException


class SimulatedException(HTTPException):
    def __init__(self, step: str, reason: str):
        self.step = step
        self.reason = reason
        super().__init__(status_code=503,detail=f"Simulated Exception: {self.step} caused by {self.reason}")

class CompensationException(SimulatedException):
   pass

class PacketLoss(SimulatedException):
    pass

class ConnectionLoss(SimulatedException):
    pass