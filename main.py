from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice


app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


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


with app.app_context():
    db.create_all()


def row_to_dict(row_or_rows):
    """Converts row(s) from a table to a dictionary or list of dictionaries."""
    if isinstance(row_or_rows, list):
        return [row_to_dict(row) for row in row_or_rows]

    row = row_or_rows
    dict = {}
    for column in row.__table__.columns:
        dict[column.name] = str(getattr(row, column.name))

    return dict


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record

@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return jsonify(cafes=[row_to_dict(cafe) for cafe in all_cafes])

@app.route("/random")
def get_random_cafe():
    cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    random_cafe = row_to_dict(choice(cafes))

    return jsonify(random_cafe)


@app.route("/search")
def search_for_cafe():
    """Returns cafes in a chosen location."""
    location = request.args.get('loc').title()

    search_results = db.session.execute(db.select(Cafe).where(Cafe.location == location)).scalars().all()
    if search_results:
        search_results_dict = row_to_dict(search_results)
        return jsonify(search_results_dict)
    else:
        return jsonify(error= {"Not found": "Sorry, we don't have a cafe at this location."})


## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={'success': 'Successfully added new cafe!'})




## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
