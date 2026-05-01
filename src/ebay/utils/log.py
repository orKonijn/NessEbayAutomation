def log_item_result(
    index: int,
    url: str,
    selected_variants: list[str],
    success: bool,
    error_message: str | None,
    screenshot_path: str,
) -> None:
    print(
        "[add_items_to_cart] "
        f"item={index} url={url} "
        f"selected_variants={selected_variants or 'none'} "
        f"status={'success' if success else 'failed'} "
        f"error={error_message or 'none'} "
        f"screenshot={screenshot_path}"
    )
