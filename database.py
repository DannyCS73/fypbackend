from app import db
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func



Base = declarative_base()
engine = create_engine('sqlite:///smartoffice.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                        autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()


class Client(Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(50), nullable=False)
    tokens = db.Column(db.Integer)
    # is_validator = db.Column(db.Boolean)

class Validators(Base):
    __tablename__ = 'validators'
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.Integer,db.ForeignKey("user.id"))
    staked_amount = db.Column(db.Integer)

class BlocksToValidate(Base):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True)
    validator = db.Column(db.Integer,db.ForeignKey("validators.id"))
    data = db.Column(db.JSON)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())



# Client.__table__.drop(engine)
# Validators.__table__.drop(engine)
#BlocksToValidate.__table__.drop(engine)


Base.metadata.create_all(engine)
db_session.commit()
