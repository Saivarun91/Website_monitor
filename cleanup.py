import os

from db import (
    get_old_screenshots,
    clear_screenshot_path
)

rows = get_old_screenshots()

deleted_count = 0

for check_id, screenshot_path in rows:

    if not screenshot_path:
        continue

    if os.path.exists(screenshot_path):

        os.remove(screenshot_path)

        clear_screenshot_path(
            check_id
        )

        deleted_count += 1

print(
    f"Deleted {deleted_count} screenshots"
)