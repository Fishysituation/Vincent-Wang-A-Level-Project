from app import db

class user(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    emailHash = db.Column(db.String(32), index=True, unique=True)
    apiKey = db.Column(db.String(16), index=True, unique=True)
    dateJoined = db.Column(db.DateTime)
    timeOfLastRequest = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.id)


class prediction(db.Model):
    __tablename__ = "prediction"

    dateTime = db.Column(db.DateTime, primary_key=True)
    pred15 = db.Column(db.Float)
    pred30 = db.Column(db.Float)
    pred60 = db.Column(db.Float)
    pred120 = db.Column(db.Float)
    pred240 = db.Column(db.Float)
    pred480 = db.Column(db.Float)

    def __repr__(self):
        return '<Prediction {}>'.format(self.dateTime)