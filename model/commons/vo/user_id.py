from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    user_id: str

    def __post_init__(self):
        if len(self.user_id) == 0:
            raise ValueError("user id cannot be empty; it's not a valid value")
