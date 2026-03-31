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

    def to_scalar(self) -> dict[str, str | int | None]:
        return {
            "height_inches": self.height_inches,
            "weight_pounds": self.weight_pounds,
            "country": self.country,
            "position": self.position,
            "draft_year": self.draft_year,
            "draft_round": self.draft_round,
            "draft_number": self.draft_number,
        }
