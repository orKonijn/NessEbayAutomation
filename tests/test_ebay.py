import allure

from ebay.pages.home_page import HomePage


@allure.feature("eBay Search")
@allure.story("User can search for a product")
def test_search_lists_products(page) -> None:
    home = HomePage(page)
    home.page.pause()
