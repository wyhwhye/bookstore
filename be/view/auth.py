from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(
        user_id=user_id, password=password, terminal=terminal
    )
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(
        user_id=user_id, old_password=old_password, new_password=new_password
    )
    return jsonify({"message": message}), code


@bp_auth.route("/view_order_history", methods=["POST"])
def view_order_history():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    u = user.User()
    code, message, orders = u.view_order_history(user_id=user_id, password=password)
    return jsonify({"message": message, "orders": orders}), code


@bp_auth.route("/search_books", methods=["POST"])
def search_books():
    store_id = request.json.get("store_id")
    title = request.json.get("title")
    tags = request.json.get("tags")
    content = request.json.get("content")
    if not store_id:
        store_id = ''
    if not title:
        title = ''
    if not tags:
        tags = ''
    if not content:
        content = ''
    u = user.User()
    code, message, books = u.search_books(store_id=store_id, title=title, tags=tags, content=content)
    return jsonify({"message": message, "books": books}), code
