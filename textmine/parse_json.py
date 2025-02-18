import abc
from urllib.parse import urlparse


class ParseJsonBase(abc.ABC):

    @abc.abstractmethod
    def parse(self, json_data: dict):
        pass


# class ParseNytApi(ParseJsonBase):
#     def __init__(self, json_data_dict: dict):
#         super().__init__(json_data_dict)
#
#     def parse(self):
#         pass


class ParseNewsApiDotOrg(ParseJsonBase):

    def parse(self, json_data: dict):
        document_list = []
        for article in json_data["articles"]:
            title = article["title"]
            description = article["description"] if article["description"] is not None else ""
            timestamp = article["publishedAt"]
            url = article["url"]
            source = urlparse(url).netloc

            document_list.append({
                "title": title,
                "description": description,
                "timestamp": timestamp,
                "source": source,
                "url": url,
                "content": None
            })
        return document_list
