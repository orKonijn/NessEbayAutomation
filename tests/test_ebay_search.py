import allure

from ebay.pages.home_page import HomePage


@allure.feature("eBay Search")
@allure.story("User can search for a product")
def test_search_lists_products(page) -> None:
    search_term = "wireless mouse"

    home = HomePage(page).open().assert_search_is_ready()
    results = home.search_for(search_term)

    (
        results.assert_loaded_for(search_term)
        .assert_has_visible_results()
    )

    with allure.step("Attach first visible result title"):
        allure.attach(
            results.first_result_title(),
            name="first-result-title",
            attachment_type=allure.attachment_type.TEXT,
        )