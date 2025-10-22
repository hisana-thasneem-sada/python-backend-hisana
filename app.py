from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import json
from sqlalchemy.types import TypeDecorator, TEXT


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cookbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class JSONEncodedList(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return "[]"
        return json.dumps(value)   

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)  
    

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(JSONEncodedList)   
    instructions = db.Column(JSONEncodedList)  
    image_url = db.Column(db.String, nullable=True)
    isFavorite = db.Column(db.Boolean, default=False)


class RecipeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Recipe
        load_instance = True
        include_fk = True
        fields = ("id", "name", "description", "ingredients", "instructions", "image_url", "isFavorite")
        
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)


@app.route("/api/recipes", methods=["POST"])
def add_recipe():
    data = request.json
    new_recipe = Recipe(
        name=data['name'],
        description=data['description'],
        ingredients=data.get('ingredients', []),  
        instructions=data.get('instructions', []), 
        image_url=data.get('imageUrl'),
        isFavorite=data.get('isFavorite', False)
    )
    db.session.add(new_recipe)
    db.session.commit()
    return recipe_schema.jsonify(new_recipe)

@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    all_recipes = Recipe.query.all()
    return recipes_schema.jsonify(all_recipes)

@app.route("/api/recipes/<int:id>", methods=["GET"])
def get_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    return recipe_schema.jsonify(recipe)


@app.route("/api/recipes/<int:id>/favorite", methods=["PATCH"])
def toggle_favorite(id):
    recipe = Recipe.query.get_or_404(id)
    recipe.isFavorite = not recipe.isFavorite
    db.session.commit()
    return recipe_schema.jsonify(recipe)

@app.route("/api/recipes/favorites", methods=["GET"])
def get_favorites():
    favorites = Recipe.query.filter_by(isFavorite=True).all()
    return recipes_schema.jsonify(favorites)


@app.route("/api/recipes/search", methods=["GET"])
def search_recipes():
    name = request.args.get("name")
    ingredient = request.args.get("ingredient")

    query = Recipe.query

    if name:
        query = query.filter(Recipe.name.ilike(f"%{name}%"))
    if ingredient:
        query = query.filter(Recipe.ingredients.like(f"%{ingredient}%"))

    results = query.all()
    return recipes_schema.jsonify(results)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

