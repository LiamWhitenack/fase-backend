from dataclasses import dataclass

from app.modeling.payload_types.core import MLPayload


@dataclass
class DraftMLPayload(MLPayload): ...
