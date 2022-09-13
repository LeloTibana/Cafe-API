from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record

@app.route("/random", methods=["GET"])
def cafe_random():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })


@app.route("/all", methods=["GET"])
def all_cafes():
    cafes_list = []
    cafes = db.session.query(Cafe).all()
    for cafe in cafes:
        each_cafe = {
            "id": cafe.id,
            "name": cafe.name,
            "location": cafe.location,
            "coffee_price": cafe.coffee_price,
            "seats": cafe.seats,
            "img_url": cafe.img_url,
            "map_url": cafe.map_url,
            'has_wifi': cafe.has_wifi,
            'has_sockets': cafe.has_sockets,
            'can_take_calls': cafe.can_take_calls,
            'has_toilet': cafe.has_toilet,
        }
        cafes_list.append(each_cafe)
    return jsonify(cafes=cafes_list)


@app.route("/search", methods=["GET"])
def search_cafe_location():
    find_location = request.args.get("loc")
    cafe_location = db.session.query(Cafe).filter(Cafe.location == find_location).all()
    if len(cafe_location) > 0:
        return jsonify(cafes=[cafe.stringify() for cafe in cafe_location])
    else:
        return jsonify(error={"Not Found": "Sorry we do not have a cafe at this location."})




@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.args.get("name"),
        map_url=request.args.get("map_url"),
        img_url=request.args.get("img_url"),
        location=request.args.get("location"),
        has_sockets=bool(int(request.args.get("has_sockets"))),
        has_toilet=bool(int(request.args.get("has_toilet"))),
        has_wifi=bool(int(request.args.get("has_wifi"))),
        can_take_calls=bool(int(request.args.get("can_take_calls"))),
        seats=request.args.get("seats"),
        coffee_price=request.args.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["GET", "PATCH"])
def edit_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully update price"}), 200
    else:
        return jsonify(response={"error": {
            "Not found": "Sorry no cafe with that id was found in the database"
        }}), 404


@app.route("/cafe-closed/<int:cafe_id>", methods=["GET", "DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKEY":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe_id)
            db.session.commit()
            return jsonify(response={"Success": "Cafe was successfully deleted from database"}), 200
        else:
            return jsonify(response={"Not Found": "Sorry no cafe with that id was found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure the API key is correct"}), 403


if __name__ == '__main__':
    app.run(debug=True)
