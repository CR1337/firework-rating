from db.base_model import db
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from peewee import DoesNotExist
from product import Product, Tag, Color
from product_filter import ProductFilterEngine
from searches import Searches

app = Flask(__name__)
CORS(app, resources={r'/*': {'origin': '*'}})


@app.route("/products", methods=['GET'])
def route_products():
    products = Product.select()
    return [p.to_dict() for p in products], 200


@app.route("/product/<pid>", methods=['GET', 'PATCH'])
def route_product_data(pid: str):
    try:
        product = Product.get(Product.id_ == pid)
    except DoesNotExist:
        return {'success': False, 'message': "No such product!"}, 404

    if request.method == 'GET':
        return product.to_dict()

    elif request.method == 'PATCH':
        for key, value in request.get_json().items():
            product.update_field(key, value)
        product.save(force_insert=False)
        return {'success': True}


@app.route("/product/next-unrated", methods=['GET'])
def route_product_next_unrated():
    excluded_pid = request.args.get('excluded') or None
    try:
        product = (
            Product.get(
                Product.id_ != excluded_pid,
                Product.rated == False  # noqa: E712
            )
            if excluded_pid
            else Product.get(Product.rated == False)  # noqa: E712
        )
    except DoesNotExist:
        return {'success': False, 'message': "No more unrated products!"}, 404
    return product.to_dict(), 200


@app.route("/tags", methods=['GET'])
def route_tags():
    tags = Tag.select()
    return [tag.name for tag in tags], 200


@app.route("/colors", methods=['GET'])
def route_colors():
    colors = Color.select()
    return [color.name for color in colors], 200


@app.route("/text-fields", methods=['GET'])
def route_text_fields():
    return [
        "name", "article_number"
    ], 200


@app.route("/boolean-fields", methods=['GET'])
def route_boolean_fields():
    return [
        "is_new", "rated", "fan", "availability", "rating"
    ], 200


@app.route("/number-fields", methods=['GET'])
def route_number_fields():
    return [
        "price", "weight", "min_caliber", "max_caliber", "min_height",
        "max_height", "duration", "nem",
        "package_size", "nem_per_second", "nem_per_shot", "shots_per_second",
        "price_per_shot", "price_per_second", "price_per_nem", "shot_count"
    ], 200


@app.route("/find-products", methods=['POST'])
def route_find_products():
    print(request.json)
    filters_ = request.json['filters']
    inverted = request.json['inverted']
    engine = ProductFilterEngine(filters_, inverted)
    engine.run()
    return {'products': [
        product.to_dict()
        for product in engine.products
    ]}, 200


@app.route("/progress", methods=['GET'])
def route_progress():
    products = Product.select()
    product_count = len(products)
    rated_count = len([p for p in products if p.rated])
    return {
        'rating_progress': rated_count,
        'product_count': product_count
    }, 200


@app.route("/searches", methods=['GET', 'POST'])
def route_searches():
    if request.method == 'GET':
        return {'searches': Searches.get_all_search_names()}, 200
    elif request.method == 'POST':
        search_name = request.json['search_name']
        search = request.json['search']
        Searches.save_search(search_name, search)
        return {'success': True}, 200


@app.route("/searches/<search_name>", methods=['GET', 'DELETE'])
def route_search(search_name: str):
    if request.method == 'DELETE':
        Searches.delete_search(search_name)
        return {'success': True}, 200
    elif request.method == 'GET':
        search = Searches.get_search(search_name)
        if search is None:
            return {'success': False, 'message': "No such search!"}, 404
        return {'search': search}, 200


@app.route('/static/<path:path>')
def route_static(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    db.connect()
    try:
        app.run("0.0.0.0", 5000, debug=True)
    except KeyboardInterrupt:
        db.close()
