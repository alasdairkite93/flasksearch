from flask import Flask, session, request, render_template, json, jsonify
from werkzeug.serving import make_ssl_devcert
import json
import sites
import ssl
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.errorhandler(500)
def pageNotFound(error):
    return render_template('form.html'), 500

@app.route('/planningdata', methods=["GET"])
def planning_data():
    planapps = sites.Planning(session['postcode'])
    plans = planapps.request()
    return plans

@app.route('/landregistry')
def sold_prices():
    landregister = sites.LandRegistry()
    registry = landregister.req()
    print(registry)
    return registry

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

@app.route('/rightmovesale', methods=["GET"])
def rmove_sales():
    rmove = sites.Rightmove(session['postcode'], "BUY")
    rmove_results = rmove.request()
    return jsonify(rmove_results)

@app.route('/rmoverent', methods=["GET"])
def rmove_lets():
    rmove = sites.Rightmove(session['postcode'], "RENT")
    rmove_results = rmove.request()
    return jsonify(rmove_results)

@app.route('/rmovesold', methods=["GET"])
def rmov_sold():
    rmove = sites.Rightmove(session['postcode'], None)
    rmov_res = rmove.requestSold()
    return jsonify(rmov_res)

@app.route('/otmsale', methods=["GET"])
def otm_sales():
    otmsale = sites.OnTheMarket(session['postcode'], "for-sale")
    otm_results = otmsale.request()
    return jsonify(otm_results)

@app.route('/otmrent', methods=["GET"])
def otm_rent():
    otmrent = sites.OnTheMarket(session['postcode'], "to-rent")
    otm_results = otmrent.request()
    return jsonify(otm_results)

@app.route('/crystalroof', methods=["GET"])
def crystal_stats():
    crysstats = sites.CrystalRoof(session['postcode'])
    resp = crysstats.stats()
    return jsonify(resp)

@app.route('/pcodeupdate', methods=["POST"])
def update_session():
    if request.method == "POST":
        update = request.form.get("pcodeupdate")
        session['postcode'] = update
        return render_template('testpage.html')

@app.route('/', methods =["GET", "POST"])
def search():

    if request.method == "POST":
        search_query = request.form.get("pcode")
        session['postcode'] = search_query
        return render_template('testpage.html')

    return render_template('form.html')

if __name__ == '__main__':
    context = ('local.crt', 'local.key')
    # , ssl_context = context
    app.secret_key = "super secret key"
    app.config['SECRET_KEY'] = 'the random string'
    app.run(host= '0.0.0.0', debug=False)
    # ssl_context = 'adhoc'