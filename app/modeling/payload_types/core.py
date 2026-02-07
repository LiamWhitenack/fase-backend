from dataclasses import dataclass


@dataclass
class MLPayload:
    relative_dollars: float | None  # target
