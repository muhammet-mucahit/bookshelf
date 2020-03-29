import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "Not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "Unprocessable entity"}
            ),
            422,
        )

    def paginate_books(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF

        books = [book.format() for book in selection]
        current_books = books[start:end]

        return current_books

    @app.route("/books", methods=["GET", "POST"])
    def get_add_search_books():
        if request.method == "GET":
            books = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, books)

            if len(current_books) == 0:
                abort(404)

            return jsonify(
                {"success": True, "books": current_books, "total_books": len(books),}
            )
        else:
            body = request.get_json()
            if "title" in body:
                title, author, rating = (
                    body["title"],
                    body["author"],
                    body["rating"],
                )
                try:
                    book = Book(title, author, rating)
                    book.insert()
                    books = Book.query.order_by(Book.id).all()
                    current_books = paginate_books(request, books)
                    return jsonify(
                        {
                            "success": True,
                            "created": book.id,
                            "books": current_books,
                            "total_books": len(books),
                        }
                    )
                except:
                    abort(422)
            else:
                search_text = body["search"]
                selection = (
                    Book.query.order_by(Book.id)
                    .filter(Book.title.ilike("%{}%".format(search_text))).all()
                )
                current_books = paginate_books(request, selection)
                return jsonify(
                    {
                        "success": True,
                        "books": current_books,
                        "total_books": len(selection),
                    }
                )

    @app.route("/books/<int:book_id>", methods=["PATCH", "DELETE"])
    def update_delete_book(book_id):
        book = Book.query.filter(Book.id == book_id).one_or_none()
        if book is None:
            abort(404)

        if request.method == "PATCH":
            body = request.get_json()
            if "rating" in body:
                book.rating = body["rating"]
            book.update()
            return jsonify({"success": True, "updated": book.id,})
        else:
            book.delete()
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": book_id,
                    "books": current_books,
                    "total_books": len(selection),
                }
            )

    return app
