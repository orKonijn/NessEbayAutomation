import allure


def attach_summary(
    index: int,
    url: str,
    success: bool,
    selected_options: list[str],
    error_message: str | None,
    screenshot_path: str | None,
) -> None:
    summary = (
        f"Index: {index}\n"
        f"URL: {url}\n"
        f"Success: {success}\n"
        f"Selected options: {selected_options}\n"
        f"Error: {error_message or 'None'}\n"
        f"Screenshot: {screenshot_path or 'N/A'}"
    )

    allure.attach(
        summary,
        name=f"Item {index} result",
        attachment_type=allure.attachment_type.TEXT,
    )
