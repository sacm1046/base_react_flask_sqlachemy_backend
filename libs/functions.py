from flask import jsonify
from flask_mail import Mail, Message
mail = Mail()

def sendMail(subject, name, from_email, to_email, html):
    msg = Message(subject, sender=[name, from_email], recipients=[to_email])
    msg.html = html
    mail.send(msg)
    return jsonify({"msg": "Email send successfully"}), 200