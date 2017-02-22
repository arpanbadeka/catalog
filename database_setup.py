from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    hometown = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'email': self.email,
            'hometown': self.hometown,
            'id': self.id,
        }

class Pokemon(Base):
    __tablename__ = 'pokemon'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

class PokemonUser(Base):
    __tablename__='pokemon_user'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    pokemon_id = Column(Integer, ForeignKey('pokemon.id'))
    pokemon = relationship(Pokemon)

engine = create_engine('sqlite:///pokemonusers.db')


Base.metadata.create_all(engine)