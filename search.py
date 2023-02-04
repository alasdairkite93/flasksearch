import werkzeug
from flask import Flask, session, request, render_template, json, jsonify
from werkzeug.serving import make_ssl_devcert
import json
import sites
import ssl
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/planningdata', methods=["GET"])
def planning_data():
    planapps = sites.Planning(session['postcode'])
    plans = planapps.request()
    return jsonify(plans)

@app.route('/landregistry')
def sold_prices():
    landregister = sites.LandRegistry(session['postcode'])
    registry = landregister.req()
    return jsonify(registry)

@app.route('/zooplasale', methods=["GET"])
def zoopla_sales():
    zoop = sites.Zoopla(session['postcode'], "for-sale")
    zooplaresults = zoop.requests()
    return jsonify(zooplaresults)

@app.route('/zooplalet', methods=["GET"])
def zoopla_lets():
    zoop = sites.Zoopla(session['postcode'], "to-rent")
    zooplaresults = zoop.requests()
    return jsonify(zooplaresults)

@app.route('/pageloadsales', methods=["GET"])
def get_page():
    rmove= sites.Rightmove(session['postcode'], "SALE", 0.5, 2, 90000, 350000)
    rmove_results = rmove.requestScrape()
    return jsonify(rmove_results)

@app.route('/rightmovesale', methods=["GET"])
def rmove_sales():
    session['page'] = 0
    rmove = sites.Rightmove(session['postcode'], "SALE", session['radius'], session['brooms'], session['minprice'], session['maxprice'], session['page'])
    rmove_results = rmove.requestScrape()
    return jsonify(rmove_results)

@app.route('/rmoverent', methods=["GET"])
def rmove_lets():
    rmove = sites.Rightmove(session['postcode'], "RENT", session['radius'], session['brooms'], session['minprice'], session['maxprice'])
    rmove_results = rmove.requestScrape()
    return jsonify(rmove_results)

@app.route('/rmovesold', methods=["GET"])
def rmov_sold():
    rmove = sites.Rightmove(session['postcode'], None, None, None, None, None)
    rmov_res = rmove.requestSold()
    return jsonify(rmov_res)

@app.route('/otmsale', methods=["GET"])
def otm_sales():
    otmsale = sites.OnTheMarket(session['postcode'], "for-sale", session['radius'], session['brooms'], session['minprice'], session['maxprice'])
    otm_results = otmsale.request()
    return jsonify(otm_results)

@app.route('/otmrent', methods=["GET"])
def otm_rent():
    otmrent = sites.OnTheMarket(session['postcode'], "to-rent", session['radius'], session['brooms'], session['minprice'], session['maxprice'])
    otm_results = otmrent.request()
    return jsonify(otm_results)

@app.route('/crystalroof', methods=["GET"])
def crystal_stats():
    crysstats = sites.CrystalRoof(session['postcode'])
    resp = crysstats.stats()
    print(resp)
    return jsonify(resp)

@app.route('/pcodeupdate', methods=["GET", "POST"])
def update_pcode():

    if request.method == "POST":
        update = request.form.get("pcodeupdate")
        session['postcode'] = update
        print("UPDATED POSTCODE", session['postcode'])
        if session['type'] == 'sales':
            return render_template('sales.html')

        if session['type'] == 'lettings':
            return render_template('lettings.html')

    return render_template('sales.html')

@app.route('/broomupdate', methods=["POST"])
def update_rooms():
    if request.method == "POST":
        brooms = request.form.get("minrooms")
        session['brooms'] = brooms

        if session['type'] == 'sales':
            return render_template('sales.html')

        if session['type'] == 'lettings':
            return render_template('lettings.html')

@app.route('/radiusupdate', methods=["POST"])
def update_radius():
    if request.method == "POST":
        radius = request.form.get("radius")
        session['radius'] = radius

        if session['type'] == 'sales':
            return render_template('sales.html')

        if session['type'] == 'lettings':
            return render_template('lettings.html')

@app.route('/priceupdate', methods=["POST"])
def update_min_price():
    if request.method == "POST":
        minprice = request.form.get("minprice")
        session['minprice'] = minprice

        if session['type'] == 'sales':
            return render_template('sales.html')

        if session['type'] == 'lettings':
            return render_template('lettings.html')
@app.route('/maxpriceupdate', methods=["POST"])
def update_max_price():
    if request.method == "POST":
        maxprice = request.form.get("maxprice")
        session['maxprice'] = maxprice

        if session['type'] == 'sales':
            return render_template('sales.html')

        if session['type'] == 'lettings':
            return render_template('lettings.html')

@app.route('/returnsales', methods=["GET", "POST"])
def salesform():
    if request.method == "POST":
        search_query = request.form.get("pcode")
        session['postcode'] = search_query
        return render_template('sales.html')
    return render_template('form.html')


@app.route('/lettings', methods=["POST"])
def letsform():
    if request.method == "POST":
        search_query = request.form.get("pcode")
        session['postcode'] = search_query
        return render_template('lettings.html')
    return render_template('form.html')

@app.route('/back', methods=["GET"])
def goBack():
    session.clear()
    return render_template('form.html')

@app.route('/', methods =["GET", "POST"])
def search():
    if request.method == "POST":
        search_query = request.form.get("pcode")
        session['postcode'] = search_query
        session['minprice'] = 'Min Price'
        session['maxprice'] = 'Max Price'

        salestype = request.form.get("sales")
        if salestype == 'sales':
            session['type'] = salestype
            return render_template('sales.html')

        lets = request.form.get("lettings")
        if lets == 'lettings':
            session['type'] = lets

            return render_template('lettings.html')

    return render_template('form.html')

if __name__ == '__main__':
    context = ('local.crt', 'local.key')
    # , ssl_context = context
    app.secret_key = "super secret key"
    app.config['SECRET_KEY'] = 'the random string'
    app.run()
    # ssl_context = 'adhoc'
