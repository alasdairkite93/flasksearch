import os
import pytest
import search
import unittest
from flask import session
from unittest import TestCase
from search import create_app
from flask import Flask
from flask_testing import TestCase
from flask_testing import LiveServerTestCase
from urllib.request import urlopen
import requests
import random
import urllib
import json
import subprocess
import re
from seleniumwire import webdriver
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from bs4 import BeautifulSoup
import smtplib, ssl
from email.message import EmailMessage


class Utility():

    def find_json_objects(self, text: str, decoder=json.JSONDecoder()):
        pos = 0
        while True:
            match = text.find("{", pos)
            if match == -1:
                break
            try:
                result, index = decoder.raw_decode(text[match:])
                yield result
                pos = match + index
            except ValueError:
                pos = match + 1

    def getProxy(self):

        prox_list = ['185.199.229.156:7492',
                     '185.199.228.220:7300',
                     '185.199.231.45:8382',
                     '188.74.210.207:6286',
                     '188.74.183.10:8279',
                     '188.74.210.21:6100',
                     '45.155.68.129:8133',
                     '154.95.36.199:6893',
                     '45.94.47.66:8110',
                     '144.168.217.88:8780']

        proxlen = len(prox_list) - 1
        proxy = prox_list[random.randint(0, proxlen)]

        return proxy


@pytest.fixture()
def app():
    app = create_app()

    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_planning_response(client):

    requestobj = f'https://api.propertydata.co.uk/planning?key=KVB3BXNFRZ&postcode=CT65HZ&decision_rating=positive&category=EXTENSION,LOFT%20CONVERSION&max_age_update=120&results=20'
    response = requests.get(requestobj)
    assert response.status_code == 200
#
# def test_planning_data(client):
#     requestobj = f'https://api.propertydata.co.uk/planning?key=KVB3BXNFRZ&postcode=CT65HZ&decision_rating=positive&category=EXTENSION,LOFT%20CONVERSION&max_age_update=120&results=20'
#     response = requests.get(requestobj)
#     assert response.status_code == 200


def test_langreg_request(client):
    base_url = f'https://landregistry.data.gov.uk/data/ppi/transaction-record.json?propertyAddress.postcode=SE10%200AA&_page=0'
    response = requests.get(base_url)
    assert response.status_code == 200


def test_rmovesold_request(client):
    rmovesold_url = 'https://www.rightmove.co.uk/house-prices/CR0 0AB.html?page=1'
    response = requests.get(rmovesold_url)
    assert response.status_code == 200


def test_rmovesales_request(client):
    rmovesale_url = 'https://www.rightmove.co.uk/property-for-sale/search.html?searchLocation=CR0 0AA'
    response = requests.get(rmovesale_url)
    assert response.status_code == 200


# def test_gumtreerent_requestanddata(client):
#
#     url = 'https://www.gumtree.com/search?search_category=property-to-rent&search_location=SE100AA&property_number_beds=100-bedroom&max_price=25000&min_price=1'
#
#     options = webdriver.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#
#     driver = webdriver.Chrome(options=options)
#     stealth(driver,
#             languages=["en-US", "en"],
#             vendor="Google Inc.",
#             platform="Win32",
#             webgl_vendor="Intel Inc.",
#             renderer="Intel Iris OpenGL Engine",
#             fix_hairline=True,
#             )
#     driver.get(url)
#     status = driver.find_elements(By.TAG_NAME, 'h1')
#     source = driver.page_source
#     rent_text = "rent"
#     assert "404" not in status and rent_text in source

def test_rmovelets_request(client):
    search_url = 'https://www.rightmove.co.uk/property-to-rent/search.html?searchLocation='
    x = requests.get(search_url + 'SE1')

    assert x.status_code == 200


def test_rmovelets_dataresponse(client):
    utility = Utility()

    search_url = 'https://www.rightmove.co.uk/property-to-rent/search.html?searchLocation='
    x = requests.get(search_url + 'SE1')
    # assert this API works

    soup = BeautifulSoup(x.text, 'html.parser')
    results = soup.find('input', {'id': 'locationIdentifier'}).get('value')
    t_url = 'https://www.rightmove.co.uk/property-to-rent/find.html?searchType=RENT&locationIdentifier=POSTCODE%5E2309&insId=1&radius=1&minPrice=100&maxPrice=25000&minBedrooms=2&maxBedrooms=4&displayPropertyType=houses&maxDaysSinceAdded=&sortByPriceDescending=&_includeLetAgreed=on&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare='
    req_url = requests.get(t_url)
    soup = BeautifulSoup(req_url.text, 'html.parser')
    results = soup.findAll('script')

    json_r = ''

    for r in results:
        l_r = list(utility.find_json_objects(r.text))
        for res in l_r:
            if len(res) > 0:
                json_r = res['properties']

    # assert price includes pcm

    try:
        p_l = []
        for props in json_r:
            price_l = props['price']['displayPrices'][0]['displayPrice']
            p_l.append(price_l)
    except IndexError:
        pass

    assert "pcm" in price_l


# def test_otmsales_request(client):
#
#     util = Utility()
#
#
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     driver = webdriver.Chrome(options=options)
#
#     stealth(driver,
#             languages=["en-US", "en"],
#             vendor="Google Inc.",
#             platform="Win32",
#             webgl_vendor="Intel Inc.",
#             renderer="Intel Iris OpenGL Engine",
#             fix_hairline=True,
#             )
#
#     url2 = 'https://www.onthemarket.com/for-sale/2-bed-detached/se10-0aa/?max-bedrooms=4&max-price=1250000&radius=1&view=grid'
#     driver.get(url2)
#
#
#     pagesource = driver.page_source
#
#     li = list(util.find_json_objects(pagesource))
#     for l in li:
#         try:
#             if l['header-data']:
#                 data = l
#                 dump = json.dumps(data, indent=4)
#                 load = json.loads(dump)
#                 lenproperties = len(load['properties'])
#                 assert lenproperties > 2
#         except:
#             pass

# def test_otmrent_request(client):
#
#     options = webdriver.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#
#     driver = webdriver.Chrome(options=options)
#     stealth(driver,
#             languages=["en-US", "en"],
#             vendor="Google Inc.",
#             platform="Win32",
#             webgl_vendor="Intel Inc.",
#             renderer="Intel Iris OpenGL Engine",
#             fix_hairline=True,
#             )
#
#     url2 = 'https://www.onthemarket.com/to-rent/2-bed-property/se1/?max-bedrooms=4&max-price=17500&min-price=100&radius=1&view=grid'
#     driver.get(url2)
#     pagesource = driver.page_source
#     assert "properties" in pagesource
#
#     # li = list(util.find_json_objects(pagesource))
#     # for l in li:
#     #     try:
#     #         if l['header-data']:
#     #             data = l
#     #             dump = json.dumps(data, indent=4)
#     #             load = json.loads(dump)
#     #             lenproperties = len(load['properties'])
#     #             assert lenproperties > 2
#     #     except:
#     #         pass

def test_crystalstates(client):
    search_url = "https://crystalroof.co.uk/report/postcode/SE12EA/overview"
    response = urllib.request.urlopen(search_url)
    data = response.read()  # a `bytes` object
    soup = BeautifulSoup(data, 'html.parser')
    results = soup.findAll('script', {"id": "__NEXT_DATA__"})
    r = results[0].text
    parsed = json.loads(r)
    data = parsed['props']['initialReduxState']['report']['sectionResponses']['overview']['data']
    assert len(data) == 15



def send_simple_message():
    return requests.post(
        "https://api.mailgun.net/v3/sandbox85b0a26ea8a84fa69641ff672b7b4c76.mailgun.org/messages",
        auth=("api", "cd398dae491d36a4ffb12d485bcc1cf5-7764770b-790de9f8"),
        files=[("attachment", ("report.html", open("report.html", "rb").read()))],
        data={"from": "Mailgun Sandbox <postmaster@sandbox85b0a26ea8a84fa69641ff672b7b4c76.mailgun.org>",
              "to": "Alasdair <alasdairkite@onlinewebservices.uk>",
              "subject": "Warning Test Failed",
              "text": "One of the web scrapers have failed. Please review the test results and undertake maintenance."})

if __name__== "__main__":
    os.system('pytest --html=report.html')
    data = open('report.html').read()
    soup = BeautifulSoup(data, 'html.parser')
    results = soup.find('span', {'class', 'failed'})
    if "0" not in results.text:
        send_simple_message()
