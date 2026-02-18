from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerBio:
    height_inches: int
    weight_pounds: int
    country: str

    position: str

    draft_year: int
    draft_round: int | None
    draft_number: int | None
