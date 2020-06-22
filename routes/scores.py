from flask import Blueprint, jsonify, request
from models import db, Score

score_route = Blueprint('score_route', __name__)
@score_route.route('/scores', methods=['GET'])
@score_route.route('/score/<int:id>', methods=['GET'])
def getscore(id=None):
    if request.method == 'GET':
        if id is not None:
            score = Score.query.get(id)
            if score:
                return jsonify(score.serialize()), 200
            else:
                return jsonify({"error":"Not found"}), 404
        else:
            scores = Score.query.all()
            scores = list(map(lambda score:score.serialize(), scores))
            return jsonify(scores), 200

@score_route.route('/scores', methods=['POST'])
def postscore():
    name = request.json.get('name')
    value = request.json.get('value')
    user_id = request.json.get('user_id')
    if not name:
        return jsonify({"error": "Insert your name"}), 422
    if not value:
        return jsonify({"error": "Insert your value"}), 422
    if not user_id:
        return jsonify({"error": "Insert your user_id"}), 422
    score = Score()
    score.name = name
    score.value = value
    score.user_id = user_id
    db.session.add(score)
    db.session.commit()
    return jsonify(score.serialize()), 201

@score_route.route('/score/<int:id>', methods=['DELETE'])
def deletescore(id):
    if request.method == 'DELETE':
        score = Score.query.get(id)
        db.session.delete(score)
        db.session.commit()
        return jsonify({"msg":"Deleted"}), 200

@score_route.route('/score/user/<int:user_id>/average', methods=['GET'])
@score_route.route('/score/average', methods=['GET'])
def getaverage(user_id=None):
    if request.method == 'GET':
        if user_id is not None:
            scores = Score.query.filter_by(user_id=user_id).all()
            scores = list(map(lambda score: score.average(), scores))
            print(scores)
            suma=0
            average=0
            for number in scores:
                suma += number
            average = suma/len(scores)
            return jsonify({
                "suma": suma,
                "average": average
                }), 200
        else:
            scores = Score.query.all()
            scores = list(map(lambda score: score.names(), scores))
            return jsonify(scores), 200
            print(scores)
            suma=0
            average=0
            for number in scores:
                suma += number
            average = suma/len(scores)
            return jsonify({
                "suma": suma,
                "average": average
                }), 200