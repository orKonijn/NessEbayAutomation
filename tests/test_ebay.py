import allure

from ebay.pages.ebay_site import EbaySite


@allure.feature("eBay")
@allure.story("User can login")
def test_login(page) -> None:
    ebay = EbaySite(page).open()
    ebay.header.login_page.login()


@allure.feature("eBay")
@allure.story("User can search for a product")
def test_search_lists_products(page) -> None:
    ebay = EbaySite(page).open()
    results = ebay.advanced_search.search_items_by_query("iphone", 5000)

    assert isinstance(results, list)


@allure.feature("eBay")
@allure.story("User can add items to cart")
def test_add_items_to_cart(page) -> None:
    ebay = EbaySite(page).open()

    ebay.item_page.add_items_to_cart(
        [
            "https://www.ebay.com/itm/305921508775",
            "https://www.ebay.com/itm/406874175758",
        ]
    )

    ebay.cart_page.assert_cart_total_not_exceeds(1000, 2)
