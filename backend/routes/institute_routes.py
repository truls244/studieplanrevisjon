from flask import Flask, jsonify, request, Blueprint
from app.models import db, Course, Institute
from flask_jwt_extended import  jwt_required


institute_bp = Blueprint('institutes', __name__)


@institute_bp.get("/get_all")
@jwt_required()
def get_all_institutes():
    institutes = db.session.query(Institute).all()
    return [institute.serialize() for institute in institutes]


