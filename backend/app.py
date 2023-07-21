from db.base_model import db
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from peewee import DoesNotExist
from product import Product, Tag

app = Flask(__name__)
CORS(app, resources={r'/*': {'origin': '*'}})


@app.route("/products", methods=['GET'])
def route_products():
    products = Product.select()
    return [p.to_dict() for p in products], 200


@app.route("/tags", methods=['GET'])
def route_tags():
    tags = Tag.select()
    return [tag.name for tag in tags], 200


@app.route("/product/<pid>", methods=['GET', 'PATCH'])
def route_product_data(pid: str):
    if request.method == 'GET':
        try:
            product = Product.get(Product.id_ == pid)
        except DoesNotExist:
            return "No such product!", 404
        else:
            return product.to_dict()
    elif request.method == 'PATCH':
        try:
            product = Product.get(Product.id_ == pid)
        except DoesNotExist:
            return {'success': False, 'message': "No such product!"}, 404
        else:
            for key, value in request.get_json().items():
                product.update_field(key, value)
            product.save(force_insert=False)
            return {'success': True}


@app.route("/product/next-unrated", methods=['GET'])
def route_product_next_unrated():
    excluded_pid = request.args.get('excluded') or None
    product = (
        Product.get(
            Product.id_ != excluded_pid,
            Product.rated == False  # noqa: E712
        )
        if excluded_pid
        else Product.get(Product.rated == False)  # noqa: E712
    )
    return product.to_dict(), 200


@app.route('/static/<path:path>')
def route_static(path):
    print(path)
    return send_from_directory('static', path)


if __name__ == "__main__":
    db.connect()
    try:
        app.run("0.0.0.0", 5000, debug=True)
    except KeyboardInterrupt:
        db.close()
