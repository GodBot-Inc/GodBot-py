from discord_slash.utils.manage_components import create_button, create_actionrow


def queue(specification: str = None):
    if specification is None:
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="queue_first"
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="queue_left"
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="queue_right"
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="queue_last"
                )
            )
        ]
    elif specification == "left_disabled":
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="disabled_queue_first",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="disabled_queue_left",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="queue_right"
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="queue_last"
                )
            )
        ]
    elif specification == "right_disabled":
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="queue_first"
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="queue_left"
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="disabled_queue_right",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="disabled_queue_last",
                    disabled=True
                )
            )
        ]
    elif specification == "disabled":
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀◀",
                    custom_id="disabled_queue_first",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="◀",
                    custom_id="disabled_queue_left",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="disabled_queue_right",
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶▶",
                    custom_id="disabled_queue_last",
                    disabled=True
                )
            )
        ]


def search(url: str, specification: str = None):
    if specification is None:
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀",
                    custom_id="search_left"
                ),
                create_button(
                    style=5,
                    label="Url",
                    url=url
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="search_right"
                )
            )
        ]
    elif specification == "no_left":
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀",
                    custom_id="search_left",
                    disabled=True
                ),
                create_button(
                    style=5,
                    label="Url",
                    url=url
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="search_right"
                )
            )
        ]
    elif specification == "no_right":
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀",
                    custom_id="search_left"
                ),
                create_button(
                    style=5,
                    label="Url",
                    url=url
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="disabled_search_right",
                    disabled=True
                )
            )
        ]
    elif specification == "disabled":
        return [
            create_actionrow(
                create_button(
                    style=2,
                    label="◀",
                    custom_id="disabled_search_left",
                    disabled=True
                ),
                create_button(
                    style=5,
                    label="Url",
                    url=url,
                    disabled=True
                ),
                create_button(
                    style=2,
                    label="▶",
                    custom_id="disabled_search_right",
                    disabled=True
                )
            )
        ]
