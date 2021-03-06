import functools
from flask import Flask, jsonify, request
from flask_swagger import swagger

app = Flask(__name__)
app.config.from_object('config.Config')

from models import db, HadithCollection, Book, Hadith

def paginate_results(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        limit = int(request.args.get('limit', 50))
        page = int(request.args.get('page', 1))

        queryset = f(*args, **kwargs).paginate(page=page, per_page=limit, max_per_page=100)
        result = {
            'data': [x.serialize() for x in queryset.items],
            'total': queryset.total,
            'limit': queryset.per_page,
            'previous': queryset.prev_num,
            'next': queryset.next_num
        }
        return jsonify(result)
    return decorated_function

@app.route('/', methods=['GET'])
def home():
    return "<h1>Welcome to sunnah.com API.</p>"

@app.route("/v1/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Sunnah.com API"
    return jsonify(swag)

@app.route('/v1/collections', methods=['GET'])
@paginate_results
def api_collections():
    return HadithCollection.query.order_by(HadithCollection.collectionID)

@app.route('/v1/collections/<string:collection_name>', methods=['GET'])
def api_collection(collection_name):
    """
        Get collection by name
        ---
        definitions:
          - schema:
              id: Collection
              properties:
                name:
                 type: string
                 description: the Collection's name
        parameters:
           - name: name
             in: path
             description: name of collection
             required: true
             type: string
        responses:
          200:
            description: A collection
            schema:
              $ref: "#/definitions/Collection"
        """
    collection = HadithCollection.query.filter_by(name=collection_name).first_or_404()
    return jsonify(collection.serialize())

@app.route('/v1/collections/<string:collection_name>/books', methods=['GET'])
@paginate_results
def api_collection_books(collection_name):
    return Book.query.filter_by(collection=collection_name).order_by(Book.ourBookID)

@app.route('/v1/collections/<string:collection_name>/books/<int:book_id>', methods=['GET'])
def api_collection_book(collection_name, book_id):
    book = Book.query.filter_by(collection=collection_name, ourBookID=book_id).first_or_404()
    return jsonify(book.serialize())

@app.route('/v1/collections/<string:collection_name>/books/<int:book_id>/hadiths', methods=['GET'])
@paginate_results
def api_collection_book_hadiths(collection_name, book_id):
    return Hadith.query.filter_by(collection=collection_name, bookID=book_id).order_by(Hadith.arabicURN)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
