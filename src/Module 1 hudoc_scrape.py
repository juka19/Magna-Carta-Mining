import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import pandas as pd
from random import uniform
from pickle import dump


def scroll():
    """Scrolls down page with Selenium

    Args:
        None
    """
    scroll_pause = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height



class Judgment:
    """Contains all essential information of the respective judgment

    Args:
        title (str): Title of the Judgment
        text (str): full text of the Judgment
        url (str): url of the Judgment
        case_details (dic): Dictionary of case_details
    
    Attributes:
        title (str): Title of the Judgment
        text (str): full text of the Judgment
        url (str): url of the Judgment
        case_details (dic): Dictionary of case_details

    """
    def __init__(self, title: str, ident: str, text:str, url:str, case_details: dict):
        self.title = title
        self.ident = ident
        self.text = text
        self.url = url
        self.case_details = case_details


def get_judgement(url, judgment_dict: dict, n: int):
    """Scrapes individual page

    It is also required to pass

    Args:
        url (str): url for individual judgment
        judgment_dict (dict): dictionary in which results are stored
    
    Returns:
        None
    """
    driver.get(url)
    sleep(uniform(4,6))
    if len(driver.find_elements_by_class_name("content")) > 1:
        text = driver.find_element_by_class_name("content").text
        title = driver.find_element_by_class_name("lineone").text
        ident = driver.find_element_by_class_name("linetwo").text.split("|")[0].strip()
        driver.find_element_by_id("notice").click()
        sleep(uniform(2,3))
        raw_text = driver.find_element_by_xpath('//*[@id="notice"]/div').text
        sleep(uniform(1,2))
        url = url
        judgment_dict[n] = Judgment(
            title = title,
            ident = ident,
            text = text,
            url = url,
            case_details = raw_text
        )
    else:
        next
 

driver = webdriver.Edge("C:/Users/julia/Downloads/msedgedriver.exe")
driver.implicitly_wait(5)       
driver.get("https://hudoc.echr.coe.int/eng#{%22documentcollectionid2%22:[%22GRANDCHAMBER%22]}")
scroll()

soup = BeautifulSoup(driver.page_source)
# urls = [('https://hudoc.echr.coe.int' + elem['href']) for elem in list(set(soup.find_all('a', class_ = re.compile('document-link'), href=True)))]

urls = list(set(["https://hudoc.echr.coe.int/eng#{" + elem['href'].partition('"GRANDCHAMBER"],')[2] for elem in soup.find_all(class_ = 'availableonlylink', href = True) if elem.text == 'English']))


n = 1 
judgment_dict = {}
for url in urls:
    get_judgement(url, judgment_dict, n)
    sleep(uniform(0.5,1))
    print(f"judgement: #{n}")
    print(f"dict-length: #{len(judgment_dict)}")
    driver.back()
    n += 1

with open('sample_data__unstructured.pickle', 'wb') as handle:
    dump(judgment_dict, handle)

# To-Dos:
# 1. More test runs
# 2. fix some bugs, figure out best sleeping times
# 3. Scrape the data


[elem.text for elem in soup.find_all(class_ = 'span2 noticefieldheading')]
[elem.text.replace("\t", "").split('\n') for elem in soup.find_all(class_ = 'col-offset-2 noticefieldvalue')]



driver.get('https://hudoc.echr.coe.int' + urls[0])
text = driver.find_element_by_class_name("content").text
title = driver.find_element_by_class_name("lineone").text
ident = driver.find_element_by_class_name("linetwo").text.split("|")[0].strip()
driver.find_element_by_id("notice").click()
soup = BeautifulSoup(driver.page_source)
sleep(uniform(2,3))
dicci = dict(
        zip(
        [elem.text for elem in soup.find_all(class_ = 'span2 noticefieldheading')],
        [elem.text.replace("\t", "").split('\n') for elem in soup.find_all(class_ = 'col-offset-2 noticefieldvalue')]
        )
    )
sleep(uniform(1,2))
url = 'https://hudoc.echr.coe.int' + urls[0]
judgment_dict[n] = Judgment(
    title = title,
    ident = ident,
    text = text,
    url = url,
    case_details = dicci
)

m = 0
for key in judgment_dict.keys():
    if bool(judgment_dict[key].case_details) == True:
        m += 1


judgment_dict.keys