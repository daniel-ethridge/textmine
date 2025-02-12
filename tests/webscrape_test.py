import pytest
import textmine.webscrape as webscrape


def test_mother_jones():
    url = "https://www.motherjones.com/politics/2025/02/donald-trump-elon-musk-jd-vance-ignore-defy-court-orders/"
    jones = webscrape.ScrapeMotherJonesContent()
    assert jones.get_domain() == "motherjones.com"
    jones.make_soup(url)
    jones.scrape_title()
    jones.scrape_content()
    assert jones.title is not None
    assert jones.content is not None
