import allure

from ebay.pages import ebay_site
from ebay.pages.ebay_site import EbaySite


@allure.feature("eBay")
@allure.story("User can login")
def test_login(page) -> None:
    ebay = EbaySite(page).open()

    ebay.header.login_page.login(
        "EbayTestingAutomation@protonmail.com",
        "TestingAutomation1!",
    )


@allure.feature("eBay")
@allure.story("User can search for a product")
def test_search_lists_products(page) -> None:
    ebay = EbaySite(page).open()

    lens = ebay.advanced_search.search_items_by_query("iphone", 5000)


@allure.feature("eBay")
@allure.story("User can add items to cart")
def test_add_items_to_cart(page) -> None:
    ebay = EbaySite(page).open()

    ebay.item_page.add_items_to_cart(
        [
            "https://www.ebay.com/itm/305921508775?itmmeta=01KQHVGEWY9S4SEW43ZVBMJ646&hash=item473a57c5a7:g:MAkAAeSwFPNozSv-&itmprp=enc%3AAQALAAAA4DKQclQvzFwZQpmMrsO4LurhM8tHKX7Vh3NhecC34I%2BI%2FL3gWhEPTBJyxQyFDevzIT%2Bi0cwhB4NBM99k44eSmLGsoq3WLeRAOqW1Lu8LUyDmeBcgds1lHYpHEXROLtXK0m7j%2FM3Nzkedz%2FfjL3eDkQpckJKjGF42qMQOXCAdQoc%2Bkt5pJuUsESAisK8wfAOdImJOwvdElokBopbYyEjxEaHjJJ7rMXsYgKhRV6jwhzQGdUOiDEs9Ej2Fnrq9hnCsAVsegmay6cw1M8ZzDyBaPMf3w48eKy%2Fx9kLtTIYHgHv9%7Ctkp%3ABk9SR8buwbu8Zw",
            "https://www.ebay.com/itm/406874175758?itmmeta=01KQHVGEWYR3RQC9EE9P6VR9B4&hash=item5ebb97390e:g:QTMAAeSwiCtpahAH&itmprp=enc%3AAQALAAAA4DKQclQvzFwZQpmMrsO4LuqgB2QrDXcFzFhBJOQTpHgWiGtjdYOS2xnWFBz1H0OSoDhyvWOfnONJthYHFO3IuLUssFruNESatmxcUGPmQ0BXywVcZMHTagI72%2BgEtARbltGs66HAELKvCMmb%2BHZBHFYf1AenrJVlmA%2BiDbMC7cLEjI6mDjcLtngX1jLlc99z9XpTV%2FnzdWC8Oa3q27xvBOp2RD24Ox3h7DaMhl8keNR78HEA4a7L8HRC62N3jdzzKp2v4X7KADaww2dl7wC9mYQ1XZqgp28eX1fJqrG8SAnj%7Ctkp%3ABFBMxu7Bu7xn",
        ]
    )

    ebay.cart_page.assert_cart_total_not_exceeds(1000, 2)
