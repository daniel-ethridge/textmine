import abc
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random

from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def html_soup(content: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(content, headers=headers)
    return BeautifulSoup(response.content, "html.parser")

# ...rest of existing code without comments and docstrings...
