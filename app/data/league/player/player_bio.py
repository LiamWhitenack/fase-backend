from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerBio:
    height_inches: int | None
    weight_pounds: int | None
    country: str | None

    position: str | None

    draft_year: int | None
    draft_round: int | None
    draft_number: int | None
