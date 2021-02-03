from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Code(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    auth_code = db.Column(db.Integer)
    attempt = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.user_id}:{self.auth_code}:{self.attempt}'
