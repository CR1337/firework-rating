from flask import (Flask, redirect, render_template, request,
                   send_from_directory)
from peewee import DoesNotExist

from product import Product
from scraper import Scraper

app = Flask(__name__)


@app.route("/", methods=['GET'])
def route_index():
    return render_template("index.html")


@app.route("/overview", methods=['GET'])
def route_overview():
    products = list(Product.select())
    return render_template("overview.html", products=products)


@app.route("/scrape", methods=['GET'])
def route_scrape():
    scraper = Scraper()
    scraper.scrape()
    return {'success': True}, 200


@app.route("/rating", methods=['GET'])
def route_rating():
    return redirect("/next-unrated-product")


@app.route("/next-unrated-product", methods=['GET'])
def route_next_unrouted_product():
    try:
        product = Product.select().where(~(Product.rated)).get()
    except DoesNotExist:
        return "No unrated product!", 200
    else:
        return redirect(f"/product/{product.id_}")


@app.route("/product/<pid>", methods=['GET'])
def route_product(pid: str):
    try:
        product = Product.get(Product.id_ == pid)
    except DoesNotExist:
        return "No such product!", 404
    else:
        return render_template('product.html', product=product.to_dict())


@app.route("/product/<pid>/json", methods=['GET'])
def route_product_data(pid: str):
    try:
        product = Product.get(Product.id_ == pid)
    except DoesNotExist:
        return "No such product!", 404
    else:
        return product.to_dict()


@app.route("/product/<pid>/update", methods=['PATCH'])
def route_product_update(pid: str):
    try:
        product = Product.get(Product.id_ == pid)
    except DoesNotExist:
        return "No such product!", 404
    else:
        for key, value in request.json:
            product.update_field(key, value)
        product.save(force_insert=False)


@app.route('/reports/<path:path>')
def send_report(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    app.run("0.0.0.0", 8080, debug=True)
