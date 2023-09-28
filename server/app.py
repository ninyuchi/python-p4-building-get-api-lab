from flask import Flask, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

# Define a custom serializer method for your models (add this to models.py)
def to_dict(self):
    return {column.name: getattr(self, column.name) for column in self.__table__.columns}

setattr(Bakery, 'to_dict', to_dict)
setattr(BakedGood, 'to_dict', to_dict)

@app.route('/')
def index():
    return '<h1>Bakery GET API</h1>'

# GET all bakeries
@app.route('/bakeries')
def get_bakeries():
    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]
    response = make_response(jsonify(bakeries_serialized), 200)
    return response

# GET bakery by ID with nested baked goods
@app.route('/bakeries/<int:id>')
def get_bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if bakery is None:
        return jsonify({"message": "Bakery not found"}), 404

    bakery_serialized = bakery.to_dict()
    bakery_serialized['baked_goods'] = [bg.to_dict() for bg in bakery.baked_goods]
    
    response = make_response(jsonify(bakery_serialized), 200)
    return response

# GET baked goods sorted by price in descending order
@app.route('/baked_goods/by_price')
def get_baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    response = make_response(jsonify(baked_goods_by_price_serialized), 200)
    return response

# GET the most expensive baked good
@app.route('/baked_goods/most_expensive')
def get_most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if most_expensive is None:
        return jsonify({"message": "No baked goods found"}), 404

    most_expensive_serialized = most_expensive.to_dict()
    response = make_response(jsonify(most_expensive_serialized), 200)
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
