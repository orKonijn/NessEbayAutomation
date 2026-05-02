import allure

from ebay.pages.ebay_site import EbaySite


@allure.epic("eBay UI Automation")
@allure.feature("Authentication")
@allure.story("Login")
@allure.title("Login with eBay account")
def test_login(page) -> None:
    ebay = EbaySite(page).open()
    ebay.header.login_page.login()


@allure.epic("eBay UI Automation")
@allure.feature("Search")
@allure.story("Advanced search")
@allure.title("Search returns product URLs")
def test_search_lists_products(page) -> None:
    query = "iphone"
    max_price = 5000

    allure.dynamic.parameter("query", query)
    allure.dynamic.parameter("max_price", max_price)

    ebay = EbaySite(page).open()
    results = ebay.advanced_search.search_items_by_query(query, max_price)

    assert isinstance(results, list)


@allure.epic("eBay UI Automation")
@allure.feature("Cart")
@allure.story("Add items")
@allure.title("Add selected items to cart and verify total")
def test_add_items_to_cart(page) -> None:
    item_urls = [
        "https://www.ebay.com/itm/305921508775",
        "https://www.ebay.com/itm/406874175758",
    ]
    budget_per_item = 1000

    allure.dynamic.parameter("item_count", len(item_urls))
    allure.dynamic.parameter("budget_per_item", budget_per_item)

    ebay = EbaySite(page).open()

    ebay.item_page.add_items_to_cart(item_urls)

    ebay.cart_page.assert_cart_total_not_exceeds(budget_per_item, len(item_urls))
