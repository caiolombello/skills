"""Finite reference reducer for Claim.tla, not a real lock or thread-safe API."""


def step(state, actor, action):
    owners, ready = state
    if actor not in (1, 2):
        raise ValueError("the example has exactly two actors")
    if action == "check":
        if owners:
            return None
        return owners, ready | {actor}
    if action == "take":
        if actor not in ready or owners:
            return None
        return owners | {actor}, ready - {actor}
    if action == "release":
        if actor not in owners:
            return None
        return owners - {actor}, ready
    raise ValueError("unknown example action")
