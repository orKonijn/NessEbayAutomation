import allure

from ebay.pages.home_page import HomePage


@allure.feature("eBay")
@allure.story("User can login")
def test_login(page) -> None:
    home_page = HomePage(page).open()

    home_page.header.login_page.login(
        "EbayTestingAutomation@protonmail.com",
        "TestingAutomation1!",
    )


@allure.feature("eBay")
@allure.story("User can search for a product")
def test_search_lists_products(page) -> None:
    home_page = HomePage(page).open()

    lens = home_page.advanced_search.search_items_by_query("iphone", 5000)
