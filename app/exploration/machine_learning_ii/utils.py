def to_filename(title: str) -> str:
    keep_characters = set("qwertyuiopasdfghjklzxcvbnm _-")
    kept = "".join([char for char in title.lower() if char in keep_characters])
    return kept.replace(" ", "-").replace("_", "-")
