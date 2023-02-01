import xmltojson
import json
import requests
import utils
import re
import html_to_json
from bs4 import BeautifulSoup
import urllib.request
import cloudscraper

import certifi

from string import Template
from SPARQLWrapper import SPARQLWrapper, JSON

import ssl

class Utility:

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

class Zoopla:

    def __init__(self, query, channel):
        self.searchquery = query
        self.channel = channel

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

    def requests(self):

        print("Zoopla Request")

        b_url = 'https://www.zoopla.co.uk/'

        radius = '?q=ct65hz&radius=0.5&search_source=refine&view_type=list'

        url = b_url+self.channel+"/property/"+self.searchquery+radius

        head = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

        req_resp = requests.get(url, headers=head)
        print(req_resp.text)
        soup = BeautifulSoup(req_resp.text, 'html.parser')
        results = soup.findAll('script', {'type':'application/json'})

        res_json = ''

        for r in results:
            res_text = r.text
            found = list(self.find_json_objects(res_text))
            list_js = found[0]
            print(found[0])
            res_json=json.dumps(list_js)
            print(res_json)

        test = json.loads(res_json)

        # function to get list of results
        listings = test['props']['pageProps']['initialProps']['searchResults']['listings']['extended']
        set = []
        for i in listings:
            li = []
            li.append(i['address'])
            li.append(i['price'])
            li.append(i['image']['src'])
            li.append(i['branch']['name'])
            li.append(i['listingId'])
            set.append(li)

        return set

class Rightmove:

    def __init__(self, query, channel):
        self.pcode = query
        self.channel = channel

    def requestSold(self):

        utils = Utility()
        pcode = self.pcode
        res = []

        for i in range(1, 20, 1):
            pconv = str(i)
            apiurl = f"https://www.rightmove.co.uk/house-prices/{pcode}.html?page={pconv}"
            req_url = requests.get(apiurl)

            soup = BeautifulSoup(req_url.text, 'html.parser')
            results = soup.findAll('script')

            li = []
            for r in results:
                res_text = r.text
                found = list(utils.find_json_objects(res_text))
                li.append(found)
            itm = li[3][0]['results']['properties']

            if len(itm) != 0:
                for prop in itm:
                    p_li = []
                    p_li.append(prop['address'])
                    pric_li = []
                    for transaction in prop['transactions']:
                        pric_li.append([transaction['displayPrice'], transaction['dateSold']])
                    p_li.append(pric_li)
                    p_li.append(prop['images']['imageUrl'])
                    p_li.append(prop['detailUrl'])
                    res.append(p_li)
                    print("\n")
        return res

    def request(self):

        postcode = self.pcode

        x = requests.get('https://www.rightmove.co.uk/property-for-sale/search.html?searchLocation=' + postcode)
        soup = BeautifulSoup(x.text, 'html.parser')
        results = soup.find('input', {'id': 'locationIdentifier'}).get('value')

        txt = results
        x = re.findall("[^^]*$", txt)
        code = x[0]

        baseurl = "https://www.rightmove.co.uk/api/_search?locationIdentifier=POSTCODE%5E"
        midurl = "&radius=0.5&sortType=2&index=0&includeSSTC=false&viewType=LIST&channel="
        endurl = "&areaSizeUnit=sqft&currencyCode=GBP&isFetching=false&viewport="

        "https://www.rightmove.co.uk/api/_search?locationIdentifier=POSTCODE%5E756476radius=0.5&sortType=2&index=0&includeSSTC=false&viewType=LIST"
        # https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE%5E756476&maxBedrooms=0&minBedrooms=0&radius=0.5&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords=

        apiurl = baseurl + code + midurl + self.channel + endurl
        req_url = requests.get(apiurl)
        soup = BeautifulSoup(req_url.text, 'html.parser')
        soup_json = json.loads(soup.text)
        properties = soup_json['properties']

        li_props = []

        for p in properties:
            li = []
            li.append(p['displayAddress'])
            li.append(p['price']['displayPrices'][0]['displayPrice'])
            li.append(p['propertyImages']['images'][0]['srcUrl'])
            li.append(p['customer']['branchDisplayName'])
            li.append(p['propertyUrl'])
            print("RMOVE: ", p['propertyUrl'])
            li_props.append(li)

        return li_props

class OnTheMarket:

    def __init__(self, query, channel):
        self.pcode = query
        self.channel = channel

    def request(self):

        print("On The Market Request")

        # base_url = 'https://www.onthemarket.com/for-sale/property/'

        url = 'https://www.onthemarket.com/'



        pcode = self.pcode.split(" ")
        p1 = pcode[0].lower()
        p2 = pcode[1].lower()
        p_tot = p1+"-"+p2
        url_end = '/?radius=0.5&view=grid'
        search_url = url + self.channel + "/property/" + p_tot+url_end

        # search_url = base_url + p_tot + url_end

        scraper = cloudscraper.create_scraper()
        req = scraper.get(search_url)

        # req_resp = requests.get(search_url, headers=user_agent)

        soup = BeautifulSoup(req.text, 'html.parser')
        results = soup.findAll('script', {'type': 'text/javascript'})

        for r in results:
            res_text = r.text
            try:
                found = list(self.find_json_objects(res_text))
                try:
                    for f in found:
                        if len(f) > 20:
                            var = f

                except IndexError:
                    pass
            except TypeError:
                pass

        otm_li = []

        for prop in var['properties']:
            li = []
            li.append(prop['display_address'])
            li.append(prop['price'])
            li.append(prop['images'][0]['default'])
            li.append(prop['agent']['name'])
            li.append("https://www.onthemarket.com/"+prop['property-link'])
            print(li)
            otm_li.append(li)

        return otm_li

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

class CrystalRoof:

    def __init__(self, pcode):
        self.pcode = pcode

    def stats(self):

        split = self.pcode.split(" ")
        p1 = split[0]
        p2 = split[1]
        pc = p1+p2

        search_url = f"https://crystalroof.co.uk/report/postcode/{pc}/overview"
        response = urllib.request.urlopen(search_url)
        data = response.read()  # a `bytes` object
        soup = BeautifulSoup(data, 'html.parser')
        results = soup.findAll('script', {"id": "__NEXT_DATA__"})

        r = results[0].text
        parsed = json.loads(r)
        data = parsed['props']['initialReduxState']['report']['sectionResponses']['overview']['data']

        print(json.dumps(data, indent=4))

        li = []
        li.append(("Supergroupname", data['loac']['supergroupname']))
        li.append(("Supergroupdescription", data['loac']['supergroupdescription']))
        li.append(("Groupname", data['loac']['groupname']))
        li.append(("Groupdescription", data['loac']['groupdescription']))
        li.append(("Income Mean", data['income_lsoa']['mean']))
        li.append(("Income Median", data['income_lsoa']['median']))
        li.append(("Deprivation imdb_score", data['indices_of_deprivation_lsoa']['imdb_score']))
        li.append(("Crime Rate", data['crime_lsoa']['rate']))
        if data['transport']['metro']['name'] != None:
            li.append(("Metro Name", data['transport']['metro']['name']))
            li.append(("Metro Lines", data['transport']['metro']['lines'][0]['overground']))
            li.append(("National Rail Lines", data['transport']['metro']['lines'][0]['national-rail']))
        if data['transport']['rail']['name'] != None:
            li.append(data['transport']['rail']['name'])
            li.append(data['transport']['rail']['lines'])
        li.append(("Amenities Supermarkets", data['amenities']['supermarkets']['businessname']))
        schools = []
        for school in range(len(data['schools']['name'])):
            schools.append((("Schools name", data['schools']['name'][school]),
                            ("Schools Ofsted Rating", data['schools']['ofstedrating'][school])))
        li.append(schools)
        li.append(("Road Noise", data['noise']['road']['noiseclass']))
        li.append(("Rail Noise", data['noise']['rail']['noiseclass']))
        li.append(("Aircraft Noise", data['noise']['aircraft']['noiseclass']))
        li.append(("Total EthnicGroups", data['ethnicgroup']['total']))
        li.append(("White British", data['ethnicgroup']['white_british']))
        li.append(("White Irish", data['ethnicgroup']['white_irish']))
        li.append(("Gypsy", data['ethnicgroup']['gypsy']))
        li.append(("Other-White", data['ethnicgroup']['other_white']))
        li.append(("Mixed Ethnicity", data['ethnicgroup']['mixed']))
        li.append(("Indian", data['ethnicgroup']['indian']))
        li.append(("Pakistani", data['ethnicgroup']['pakistani']))
        li.append(("Bangladeshi", data['ethnicgroup']['bangladeshi']))
        li.append(("Chinese", data['ethnicgroup']['chinese']))
        li.append(("Other Asian", data['ethnicgroup']['other_asian']))
        li.append(("Black", data['ethnicgroup']['black']))
        li.append(("Other", data['ethnicgroup']['other']))
        li.append(("Total Religion", data['religion']['total']))
        li.append(("Has Religion", data['religion']['has_religion']))
        li.append(("Christian", data['religion']['christian']))
        li.append(("Buddhist", data['religion']['buddhist']))
        li.append(("Hindu", data['religion']['hindu']))
        li.append(("Jewish", data['religion']['jewish']))
        li.append(("Muslim", data['religion']['muslim']))
        li.append(("Sikh", data['religion']['sikh']))
        li.append(("Other Religion", data['religion']['other']))
        li.append(("No-Religion", data['religion']['no_religion']))
        li.append(("Total Household", data['household']['total']))
        li.append(("One Person Household", data['household']['one_person']))
        li.append(("Couples with Children", data['household']['couple_with_children']))
        li.append(("Couples without Children", data['household']['couple_without_children']))
        li.append(("Same sex couples", data['household']['same_sex_couple']))
        li.append(("Lone Parents with Children", data['household']['lone_parent_with_children']))
        li.append(("Lone parents without Children", data['household']['lone_parent_without_children']))
        li.append(("Multi Student Households", data['household']['multi_person_student']))
        li.append(("Other Multi Person Households", data['household']['multi_person_other']))
        li.append(("Total Household Lifestage", data['householdlifestage']['total']))
        li.append(("Lifestage Under 35", data['householdlifestage']['ageunder35']))
        li.append(("Lifesstage 35-64", data['householdlifestage']['age35to54']))
        li.append(("Lifestage 55-64", data['householdlifestage']['age55to64']))
        li.append(("Lifestage 65 and Above", data['householdlifestage']['age65above']))

        return li

    # print(data['income_lsoa']['mean'])
    # print(data['income_lsoa']['median'])
    # print("crime rate: ", data['crime_lsoa']['rate'])
    # print("crime rank: ", data['crime_lsoa']['rank'])
    # print("\n")
    #
    # # Transport
    # print("transport metro: ", data['transport']['metro']['name'])
    # print("transport rail name: ", data['transport']['rail']['name'])
    # print("transport rail lines: ", data['transport']['rail']['lines'][0])
    #
    # # Amenities
    # print("Supermarkets names: ", data['amenities']['supermarkets']['businessname'])
    #
    # # Schools
    # print("School name: ", data['schools']['name'])
    # print("School ofsted ratings: ", data['schools']['ofstedrating'])
    #
    # # noise
    # print("Road noise class: ", data['noise']['road']['noiseclass'])
    #
    # # ethnicity
    # print("Ethnicity total: ", data['ethnicgroup']['total'])
    # print("Religion total: ", data['religion']['total'])
    # print("Household total: ", data['household']['total'])

class LandRegistry:

    def __init__(self, pcode):
        self.pcode = pcode
    def req(self):

        print("makeing a request to land registry")

        pcode = self.pcode.split(" ")
        pcode1 = pcode[0]
        pcode2 = '%20' + pcode[1]
        p_fin = pcode1 + pcode2
        num = 10
        li = []
        for i in range(num):
            base_url = f'https://landregistry.data.gov.uk/data/ppi/transaction-record.json?propertyAddress.postcode={p_fin}&_page={i}'
            x = requests.get(base_url).text
            loaded = json.loads(x)
            items = loaded['result']['items']
            if len(items) > 0:
                li.append(items)

        regs = []
        for itm in li:
            for list in itm:
                trans = []
                try:
                    trans.append((list['propertyAddress']['paon'], " " + list['propertyAddress']['street'],
                                  " " + list['propertyAddress']['town'], " " + list['propertyAddress']['county'],
                                  " " + list['propertyAddress']['district'], " " + list['propertyAddress']['locality'], " "+list['propertyAddress']['postcode']))
                    trans.append("£" + str(list['pricePaid']))
                    trans.append(list['transactionDate'])
                    regs.append(trans)
                except TypeError:
                    pass
                except KeyError:
                    pass

        return regs

    #Both methods below are for use with SPARQL
    # def getData(self):
    #
    #
    #     print("GET DATA")
    #
    #
    #
    #     # query built from https://landregistry.data.gov.uk/app/qonsole#
    #
    #     sparql = SPARQLWrapper("http://landregistry.data.gov.uk/landregistry/query", custom_cert_filename=certifi.where())
    #     sparql.setReturnFormat(JSON)
    #
    #     print("AFTER URL")
    #
    #     string = Template("""
    #         prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #         prefix owl: <http://www.w3.org/2002/07/owl#>
    #         prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    #         prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
    #         prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
    #         prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
    #         prefix skos: <http://www.w3.org/2004/02/skos/core#>
    #         prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>
    #
    #         SELECT ?paon ?saon ?street ?town ?county ?postcode ?amount ?date ?category
    #         WHERE
    #         {
    #           VALUES ?postcode {"$p1 $p2"^^xsd:string}
    #
    #           ?addr lrcommon:postcode ?postcode.
    #
    #           ?transx lrppi:propertyAddress ?addr ;
    #                   lrppi:pricePaid ?amount ;
    #                   lrppi:transactionDate ?date ;
    #                   lrppi:transactionCategory/skos:prefLabel ?category.
    #
    #           OPTIONAL {?addr lrcommon:county ?county}
    #           OPTIONAL {?addr lrcommon:paon ?paon}
    #           OPTIONAL {?addr lrcommon:saon ?saon}
    #           OPTIONAL {?addr lrcommon:street ?street}
    #           OPTIONAL {?addr lrcommon:town ?town}
    #         }
    #         ORDER BY ?amount
    #             """)
    #
    #     sparql.setQuery(string.substitute(p1='CT6', p2='5HZ'))
    #     li = []
    #     try:
    #         ret = sparql.queryAndConvert()
    #
    #         for r in ret["results"]["bindings"]:
    #             li.append(r)
    #             print(r)
    #         return li
    #     except Exception as e:
    #         print("ERROR")
    #         print(e)

    # def data2(self):
    #
    #
    #     # query built from https://landregistry.data.gov.uk/app/qonsole#
    #
    #     sparql = SPARQLWrapper("https://landregistry.data.gov.uk/landregistry/query")
    #     sparql.setReturnFormat(JSON)
    #
    #     string = Template("""
    #         prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    #         prefix owl: <http://www.w3.org/2002/07/owl#>
    #         prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    #         prefix sr: <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/>
    #         prefix ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>
    #         prefix lrppi: <http://landregistry.data.gov.uk/def/ppi/>
    #         prefix skos: <http://www.w3.org/2004/02/skos/core#>
    #         prefix lrcommon: <http://landregistry.data.gov.uk/def/common/>
    #
    #         SELECT ?paon ?saon ?street ?town ?county ?postcode ?amount ?date ?category
    #         WHERE
    #         {
    #           VALUES ?postcode {"$p1 $p2"^^xsd:string}
    #
    #           ?addr lrcommon:postcode ?postcode.
    #
    #           ?transx lrppi:propertyAddress ?addr ;
    #                   lrppi:pricePaid ?amount ;
    #                   lrppi:transactionDate ?date ;
    #                   lrppi:transactionCategory/skos:prefLabel ?category.
    #
    #           OPTIONAL {?addr lrcommon:county ?county}
    #           OPTIONAL {?addr lrcommon:paon ?paon}
    #           OPTIONAL {?addr lrcommon:saon ?saon}
    #           OPTIONAL {?addr lrcommon:street ?street}
    #           OPTIONAL {?addr lrcommon:town ?town}
    #         }
    #         ORDER BY ?amount
    #             """)
    #
    #     sparql.setQuery(string.substitute(p1='CT6', p2='5HZ'))
    #
    #     try:
    #         ret = sparql.queryAndConvert()
    #
    #         for r in ret["results"]["bindings"]:
    #             print(r)
    #     except Exception as e:
    #         print(e)

class Planning:

    def __init__(self, pcode):
        self.pcode = pcode

    def request(self):
        API_KEY = 'KVB3BXNFRZ'
        P_CODE = self.pcode
        requestobj = f'https://api.propertydata.co.uk/planning?key={API_KEY}&postcode={P_CODE}&decision_rating=positive&category=EXTENSION,LOFT%20CONVERSION&max_age_update=120&results=20'
        obj = requests.get(requestobj)

        load = json.loads(obj.text)
        data = load['data']['planning_applications']

        applications = []

        for app in data:
            li = []
            li.append(('url: ', app['url']))
            li.append(('address: ', app['address']))
            li.append(('type: ', app['type']))
            li.append(('status: ', app['status']))
            li.append(('proposal: ', app['proposal']))
            li.append(('type: ', app['type']))
            li.append(('status: ', app['status']))
            li.append(('decision: ', app['decision']['text']))
            li.append(('date_received: ', app['dates']['received_at']))
            li.append(('date_validated: ', app['dates']['validated_at']))
            li.append(('date_decided: ', app['dates']['decided_at']))
            li.append(('date_published: ', app['dates']['published_at']))
            li.append(('latitude: ', app['lat']))
            li.append(('longitude: ', app['lng']))
            li.append(('distance: ', app['distance']))
            applications.append(li)

        return applications