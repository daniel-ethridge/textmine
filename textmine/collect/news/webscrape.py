import abc

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random

from selenium.common import ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from newspaper import Article


def _htmlify_query(query):
    return query.replace(" ", "+")


def _html_soup(content: str, headers=None):
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(content, headers=headers)
    # return BeautifulSoup(response.content, "html5lib")
    return BeautifulSoup(response.content, "html.parser")


def selenium_soup(content: str, check_for_modal: bool=False, browser="chrome"):
    driver = webdriver.Firefox()
    driver.get(content)

    try:
        if check_for_modal:
            try:
                modal = WebDriverWait(driver, random.uniform(5, 10)).until(
                    ec.visibility_of_element_located((By.CLASS_NAME, "css-j07ljx")))
                time.sleep(random.uniform(0.5, 1.5))
                modal.click()
            except TimeoutException:
                pass

        html_info = driver.page_source
        
        time.sleep(random.uniform(2, 5))
        driver.quit()
        
        return BeautifulSoup(html_info, "html.parser")
    
    except Exception as e:
        print(f"Error during page load: {e}")
        driver.quit()
        return None

def write_soup_html(soup):
    with open("soup.html", "w") as f:
        f.write(str(soup))


class BaseWebscrapeContent(abc.ABC):
    def __init__(self):
        self._title = None
        self._site_content = None
        self._soup = None

    @staticmethod
    @abc.abstractmethod
    def get_domain():
        pass

    @abc.abstractmethod
    def make_soup(self, url: str):
        pass

    @abc.abstractmethod
    def scrape_title(self):
        pass

    @abc.abstractmethod
    def scrape_content(self):
        pass

    @property
    def title(self):
        return self._title

    @property
    def content(self):
        return self._site_content

    @property
    def soup(self):
        return self._soup


class BaseGetResults(abc.ABC):
    def __init__(self):
        self._search_results = None


    @abc.abstractmethod
    def get_search_results(self, query, max_results=1000):
        pass

class ScrapeAPContent(BaseWebscrapeContent, BaseGetResults):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain() -> str:
        return "apnews.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self._soup.find("h1", class_="Page-headline").text

    def scrape_content(self):
        body_text = self._soup.find("div", class_="RichTextStoryBody RichTextBody")
        paragraph_tags = body_text.find_all("p", recursive=False)
        text_list = []
        for tag in paragraph_tags:
            if tag.text != "":
                text_list.append(tag.text)
        self._site_content = " ".join(text_list)

    def get_search_results(self, query, max_results=1000):
        page = 1
        links = []

        while True:

            page += 1
            endpoint = f"https://apnews.com/search?q={_htmlify_query(query)}&s=0&p={page}"
            self.make_soup(endpoint)
            tags = self.soup.find_all("a", {"class": re.compile("Link.*")})

            if len(tags) == 0:
                break

            for tag in tags:
                try:
                    link = tag["href"]
                    if "article" in link:
                        links.append(link)
                except KeyError:
                    continue

            links = list(set(links))
            if len(links) >= max_results:
                break

        if len(links) > max_results:
            return links[:max_results]

        return links


class ScrapeCNNContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "cnn.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self.soup.find("h1", id="maincontent").text

    def scrape_content(self):
        paragraph_tags = self.soup.find_all("p", class_="paragraph inline-placeholder vossi-paragraph")
        text_list = []
        for tag in paragraph_tags:
            tag = tag.text.replace("\n", "").lstrip().rstrip()
            text_list.append(tag)

        self._site_content = " ".join(text_list)



class ScrapeNYTContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "nytimes.com"

    def make_soup(self, url: str):
        self._soup = selenium_soup(url, True)

    def scrape_title(self):
        self._title = self.soup.find("h1", class_="css-1fyu99 e1h9rw200")

    def scrape_content(self):
        paragraph_tags = self.soup.find_all("p", class_="css-at9mc1 evys1bk0")
        text_list = []
        for tag in paragraph_tags:
            text_list.append(tag.text)
        self._site_content = " ".join(text_list)


class ScrapeBBCContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "bbc.com,bbc.co.uk"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self.soup.select("article > div > h1")[0].text

    def scrape_content(self):
        paragraph_tags = self.soup.select("article > div > p")
        text_list = []
        for tag in paragraph_tags:
            text_list.append(tag.text)
        self._site_content = " ".join(text_list)


class ScrapeMSNBCContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "msnbc.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)
        print(self.soup)

    def scrape_title(self):
        self._title = self.soup.find("h1", {"class": re.compile(".*headline.*")}).text

    def scrape_content(self):
        body = self.soup.find("div", {"class": re.compile(".*content.*")})
        paragraph_tags = body.find_all("p", {"class": re.compile(".*body.*|.*graf.*")})
        tags = []
        for tag in paragraph_tags:
            tags.append(tag.text)

        self._site_content = " ".join(tags)


class ScrapeNewYorkPostContent(BaseWebscrapeContent, BaseGetResults):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "nypost.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self.soup.find("h1", class_="headline headline--single-fallback").text

    def scrape_content(self):
        content_div = self.soup.find("div", class_="single__content entry-content m-bottom")
        paragraph_tags = content_div.find_all("p")
        tags_list = []
        for tag in paragraph_tags:
            tags_list.append(tag.text)

        self._site_content = " ".join(tags_list)


    def get_search_results(self, query, max_results=1000):
        page = 1
        links = []

        while True:

            page += 1
            endpoint = f"https://nypost.com/search/{_htmlify_query(query)}/page/{page}/?orderby=relevance"
            self.make_soup(endpoint)
            tags = self.soup.find_all("a", {"class": re.compile("postid.*")})

            if len(tags) == 0:
                break

            for tag in tags:
                try:
                    links.append(tag["href"])
                except KeyError:
                    continue

            links = list(set(links))
            if len(links) >= max_results:
                break

        if len(links) > max_results:
            return links[:max_results]


class ScrapeMotherJonesContent(BaseWebscrapeContent, BaseGetResults):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "motherjones.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)
        print(self.soup.prettify())

    def scrape_title(self):
        self._title = self.soup.find("h1", {"class": re.compile(".*title.*")}).text

    def scrape_content(self):
        body = self.soup.find("article", {"class": re.compile(".*content.*")})
        paragraph_tags = [tag.text for tag in body.find_all("p")]
        self._site_content = " ".join(paragraph_tags)

    def get_search_results(self, query, max_results=1000):
        page = 1
        links = []

        while True:

            page += 1
            endpoint = f"https://www.motherjones.com/page/{page}/?s={_htmlify_query(query)}"
            self.make_soup(endpoint)
            headers = self.soup.find_all("h3", {"class": re.compile(".*hed.*")})
            tags = []
            for header in headers:
                tags.append(header.find("a"))

            if len(tags) == 0:
                break

            for tag in tags:
                try:
                    links.append(tag["href"])
                except KeyError:
                    continue

            links = list(set(links))
            if len(links) >= max_results:
                break

        if len(links) > max_results:
            return links[:max_results]


class ScrapeCenterSquareContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "thecentersquare.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self.soup.find("h1", {"class": re.compile(".*headline.*")}).text

    def scrape_content(self):
        body = self.soup.find("div", {"id": re.compile(".*article-body.*")})
        paragraph_tags = body.find_all("p")
        paragraph_tags = [tag.text for tag in paragraph_tags]
        self._site_content = " ".join(paragraph_tags)


class ScrapeDispatchContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "thedispatch.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self.soup.find("h1", {"class": re.compile(".*h1.*")}).text

    def scrape_content(self):
        body = self.soup.find("section", {"id": re.compile(".*article-body.*")})
        paragraph_tags = body.find_all("p")
        paragraph_tags = [tag.text for tag in paragraph_tags]
        self._site_content = " ".join(paragraph_tags)


class ScrapeOANNContent(BaseWebscrapeContent, BaseGetResults):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "oann.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self.soup.find("h1", {"class": re.compile(".*title.*")}).text

    def scrape_content(self):
        body = self.soup.find("article", {"class": re.compile(".*content.*")})
        paragraph_tags = [tag.text for tag in body.find_all("p")]
        self._site_content = " ".join(paragraph_tags)

    def get_search_results(self, query, max_results=1000):
        links = []
        page = 0

        while True:
            page += 1
            query = _htmlify_query(query)
            endpoint = f"https://www.oann.com/page/{page}/?s={query}"
            self.make_soup(endpoint)
            entries = self.soup.find_all("h2", class_="entry-title")

            for entry in entries:
                try:
                    tag = entry.find("a")
                    links.append(tag["href"])
                except KeyError:
                    continue

            if len(entries) == 0:
                break
            elif len(links) > max_results:
                links = links[:max_results]
                break

        return links


class ScrapeABCContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "abcnews.go.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        self._title = self.soup.find("h1", {
            "class": re.compile(".*vMjAx.*|.*gjbzK.*|.*tntuS.*|.*eHrJ.*|.*mTgUP.*")}).text

    def scrape_content(self):
        paragraph_tags = self.soup.find_all("p", {
            "class": re.compile(".*EkqkG.*|.*IGXmU.*|.*nlgHS.*|.*yuUao.*|.*MvWXB.*|.*TjIXL.*|.*aGjvy.*|.*ebVHC.*")
        })
        paragraph_tags = [tag.text for tag in paragraph_tags]
        self._site_content = " ".join(paragraph_tags)



class ScrapeUSATodayContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeCNBCContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeNationalReviewContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeFederalistContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeReasonContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeWashingtonExaminerContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeRealClearPoliticsContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeVoxContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeSlateContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeTheNationContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeDailyWireContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeHuffingtonPostContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeInterceptContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeWesternJournalContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeDailyKosContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


class ScrapeForbesContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = _html_soup(url)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass

class ScrapeFoxContent(BaseWebscrapeContent, BaseGetResults):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return "foxnews.com"

    def make_soup(self, url: str):
        self._soup = _html_soup(url)
        with open("test.html", "w") as f:
            f.write(self.soup.prettify())

    def scrape_title(self):
        self._title = self.soup.find("h1", {"class": re.compile("headline.*")}).text

    def scrape_content(self):
        body = self.soup.find("div", class_="article-body")
        paragraphs = body.find_all("p", recursive=False)

        tag_list = []
        for tag in paragraphs:
            tag_list.append(tag.text)

        self._site_content = " ".join(tag_list)

    def get_search_results(self, query, max_results=1000):
        num_results = 0
        links = []

        endpoint = f"https://www.foxnews.com/search-results/search#q={query.replace(" ", "%20")}"
        driver = webdriver.Chrome()
        driver.get(endpoint)

        # Adapted from
        button = driver.find_element(By.XPATH, "/html/body/div/div/div/div[2]/div[2]/div/div[3]/div[2]")
        interaction_failed_once = False
        while True:
            # Click then wait to load page
            try:
                button.click()
                num_results += 10
                if max_results is not None and num_results >= max_results:
                    break
            except ElementNotInteractableException:
                if not interaction_failed_once:
                    interaction_failed_once = True
                else:
                    break

            time.sleep(1)

        content = driver.page_source
        driver.close()

        self._soup = BeautifulSoup(content, "html.parser")
        titles = self.soup.find_all("h2", class_="title")
        for title in titles:
            try:
                links.append(title.find("a")["href"])
            except KeyError:
                continue

        if max_results is not None and len(links) > max_results:
            return links[:max_results]

        return links


class ScrapeReutersContent(BaseWebscrapeContent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_domain():
        return ""

    def make_soup(self, url: str):
        self._soup = selenium_soup(url)
        print(self.soup)

    def scrape_title(self):
        pass

    def scrape_content(self):
        pass


def main():
    scraper = ScrapeMotherJonesContent()
    scraper.get_search_results("mass shootings", max_results=2000)


if __name__ == "__main__":
    main()
