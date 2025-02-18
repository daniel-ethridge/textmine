import requests
import abc
from typing import Tuple, Union, Dict, Any
from .parse_json import ParseJsonBase


def read_api_key_from_file(path_to_file: str):
    """Read API key from file.
    
    Args:
        path_to_file (str): Path to file containing API key
        
    Returns:
        str: API key string
        
    Raises:
        FileNotFoundError: If key file doesn't exist
    """
    try:
        with open(path_to_file, "r") as f:
            api_key_ = f.read()
        return api_key_
    except FileNotFoundError as e:
        raise e


class BaseApiGetRequest(abc.ABC):
    """Abstract base class for API GET requests.
    
    Provides common functionality for making API requests and handling responses.
    
    Attributes:
        _api_key (str): API authentication key
        _endpoint (str): API endpoint URL
        _parser (ParseJsonBase): Optional response parser
        _params (Dict): Request parameters
        _response (Response): Last API response
    """

    def __init__(self, api_key_: str, parser: ParseJsonBase=None):
        """Initialize API request handler.
        
        Args:
            api_key_ (str): API authentication key
            parser (ParseJsonBase, optional): Response parser
        """
        self._api_key = api_key_
        self._endpoint = None
        self._parser = parser
        self._params: Dict[str, Any] = {}
        self._response = None

    @abc.abstractmethod
    def get(self) -> Tuple[bool, Union[Dict, requests.Response]]:
        """Execute API request.
        
        Returns:
            Tuple[bool, Union[Dict, Response]]: Success flag and response
        """
        pass

    @property
    def response(self):
        """Get last API response.
        
        Returns:
            Response: Last response object or None
        """
        return self._response

    def get_last_request(self):
        """Get URL from last request.
        
        Returns:
            str: Complete URL or None if no request made
        """
        if self.response is None:
            return None
        else:
            return self.response.url


class NewsApiDotOrgEverything(BaseApiGetRequest):
    """NewsAPI.org /everything endpoint implementation.
    
    Provides access to all articles including query and filtering options.
    
    Attributes:
        _endpoint (str): /v2/everything endpoint URL
        _parser (ParseJsonBase): Optional response parser
    """

    def __init__(self, api_key_: str, parser: ParseJsonBase=None):
        """Initialize everything endpoint.
        
        Args:
            api_key_ (str): NewsAPI authentication key
            parser (ParseJsonBase, optional): Response parser
        """
        super().__init__(api_key_, parser)
        self._endpoint = "https://newsapi.org/v2/everything"

    def q(self, q_: str) -> 'NewsApiDotOrgEverything':
        """Set search query.
        
        Args:
            q_ (str): Keywords or phrases to search for
            
        Returns:
            self: For method chaining
        """
        self._params["q"] = q_
        return self

    def search_in(self, fields: str) -> 'NewsApiDotOrgEverything':
        """Restrict search to specific fields.
        
        Args:
            fields (str): Comma-separated fields (title,description,content)
            
        Returns:
            self: For method chaining
        """
        self._params["searchIn"] = fields
        return self

    def sources(self, sources_: str) -> 'NewsApiDotOrgEverything':
        """Set sources to search within.
        
        Args:
            sources_ (str): Comma-separated list of sources
            
        Returns:
            self: For method chaining
        """
        self._params["sources"] = sources_
        return self

    def domains(self, domains_: str) -> 'NewsApiDotOrgEverything':
        """Set domains to search within.
        
        Args:
            domains_ (str): Comma-separated list of domains
            
        Returns:
            self: For method chaining
        """
        self._params["domains"] = domains_
        return self

    def exclude_domains(self, domains_: str) -> 'NewsApiDotOrgEverything':
        """Exclude domains from search.
        
        Args:
            domains_ (str): Comma-separated list of domains to exclude
            
        Returns:
            self: For method chaining
        """
        self._params["excludeDomains"] = domains_
        return self

    def from_date(self, date_: str) -> 'NewsApiDotOrgEverything':
        """Set start date for articles.
        
        Args:
            date_ (str): Date in YYYY-MM-DD format
            
        Returns:
            self: For method chaining
        """
        self._params["from"] = date_
        return self

    def to_date(self, date_: str) -> 'NewsApiDotOrgEverything':
        """Set end date for articles.
        
        Args:
            date_ (str): Date in YYYY-MM-DD format
            
        Returns:
            self: For method chaining
        """
        self._params["to"] = date_
        return self

    def language(self, lang_: str) -> 'NewsApiDotOrgEverything':
        """Set language for articles.
        
        Args:
            lang_ (str): 2-letter ISO-639-1 code of the language
            
        Returns:
            self: For method chaining
        """
        self._params["language"] = lang_
        return self

    def sort_by(self, sort_: str) -> 'NewsApiDotOrgEverything':
        """Set sorting order for articles.
        
        Args:
            sort_ (str): Sorting order (relevancy, popularity, publishedAt)
            
        Returns:
            self: For method chaining
        """
        self._params["sortBy"] = sort_
        return self

    def page_size(self, size_: int) -> 'NewsApiDotOrgEverything':
        """Set number of results per page.
        
        Args:
            size_ (int): Number of results per page
            
        Returns:
            self: For method chaining
        """
        self._params["pageSize"] = size_
        return self

    def page(self, num_: int) -> 'NewsApiDotOrgEverything':
        """Set page number for results.
        
        Args:
            num_ (int): Page number
            
        Returns:
            self: For method chaining
        """
        self._params["page"] = num_
        return self

    def get(self) -> Tuple[bool, Union[Dict, requests.Response]]:
        """Execute API request with all set parameters.
        
        Returns:
            Tuple[bool, Union[Dict, Response]]: Success status and either 
            parsed JSON response or raw Response object
        """
        self._params["apiKey"] = self._api_key
        self._response = requests.get(self._endpoint, params=self._params)
        self._params.clear()
        if self._response.status_code == 200:
            if self._parser is not None:
                return True, self._parser.parse(self._response.json())
            else:
                return True, self._response.json()
        return False, self._response


class NewsApiDotOrgHeadlines(BaseApiGetRequest):
    """NewsAPI.org /top-headlines endpoint implementation.
    
    Access breaking news headlines filtered by country or category.
    
    Note: country/category parameters cannot be mixed with sources parameter.
    """

    def __init__(self, api_key_: str, parser: ParseJsonBase):
        """Initialize headlines endpoint.
        
        Args:
            api_key_ (str): NewsAPI authentication key  
            parser (ParseJsonBase): Response parser
        """
        super().__init__(api_key_, parser)
        self._endpoint = "https://newsapi.org/v2/top-headlines"

    def country(self, country_: str) -> 'NewsApiDotOrgHeadlines':
        """Filter articles by country.
        
        Args:
            country_ (str): 2-letter ISO 3166-1 country code
            
        Returns:
            self: For method chaining
        """
        self._params["country"] = country_
        return self

    def category(self, category_: str) -> 'NewsApiDotOrgHeadlines':
        """Filter articles by category.
        
        Args:
            category_ (str): News category (business, technology, etc)
            
        Returns:
            self: For method chaining
        """
        self._params["category"] = category_
        return self

    def sources(self, sources_: str) -> 'NewsApiDotOrgHeadlines':
        """Set sources to search within.
        
        Args:
            sources_ (str): Comma-separated list of sources
            
        Returns:
            self: For method chaining
        """
        self._params["sources"] = sources_
        return self

    def q(self, q_: str) -> 'NewsApiDotOrgHeadlines':
        """Set search query.
        
        Args:
            q_ (str): Keywords or phrases to search for
            
        Returns:
            self: For method chaining
        """
        self._params["q"] = q_
        return self

    def page_size(self, size_: int) -> 'NewsApiDotOrgHeadlines':
        """Set number of results per page.
        
        Args:
            size_ (int): Number of results per page
            
        Returns:
            self: For method chaining
        """
        self._params["pageSize"] = size_
        return self

    def page(self, num_: int) -> 'NewsApiDotOrgHeadlines':
        """Set page number for results.
        
        Args:
            num_ (int): Page number
            
        Returns:
            self: For method chaining
        """
        self._params["page"] = num_
        return self

    def get(self) -> Tuple[bool, Union[Dict, requests.Response]]:
        """Execute API request with all set parameters.
        
        Returns:
            Tuple[bool, Union[Dict, Response]]: Success status and either 
            parsed JSON response or raw Response object
        """
        self._params["apiKey"] = self._api_key
        self._response = requests.get(self._endpoint, params=self._params)
        self._params.clear()
        if self._response.status_code == 200:
            return True, self._response.json()
        return False, self._response


class NytApi(BaseApiGetRequest):
    def __init__(self, api_key_: str, parser: ParseJsonBase=None):
        super().__init__(api_key_, parser)

        self._endpoint = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

    def page(self, page_):
        self._params["page"] = page_
        return self

    def q(self, query: str):
        self._params["q"] = query
        return self


    def get(self) -> Tuple[bool, Union[Dict, requests.Response]]:
        self._params["api-key"] = self._api_key
        self._response = requests.get(self._endpoint, params=self._params)
        self._params.clear()
        if self._response.status_code == 200:
            if self._parser is not None:
                return True, self._parser.parse(self._response.json())
            else:
                return True, self._response.json()
        return False, self._response


if __name__ == "__main__":
    api_key = read_api_key_from_file("../../text-mining-project/text_mining/api_keys/news-api-key.txt")
    news = NewsApiDotOrgEverything(api_key)
    success, data = news.q('mass shooting').get()
    if success:
        print(data)
    else:
        print(data.reason)
