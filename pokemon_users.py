from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Pokemon, PokemonUser

engine = create_engine('sqlite:///pokemonusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


#Create Dummy Users1

User1 = User(name="Arpan Badeka", email="arpan.badeka@gmail.com", hometown="Ujjain")
session.add(User1)
session.commit()


#Create Dummy Users2

User2 = User(name="Ankur Khemani", email="ankurkhe@usc.edu", hometown="Delhi")
session.add(User2)
session.commit()


#Add Pokemons to PokemonDB

Pokemon1 = Pokemon(name="Pikachu")
session.add(Pokemon1)
session.commit()

Pokemon2 = Pokemon(name="Raichu")
session.add(Pokemon2)
session.commit()

Pokemon3 = Pokemon(name="Squirtle")
session.add(Pokemon3)
session.commit()

#Link users to Pokemons

pokemonuser1 = PokemonUser(user_id=1, pokemon_id=1)
session.add(pokemonuser1)
session.commit()

pokemonuser2 = PokemonUser(user_id=1,pokemon_id=3)
session.add(pokemonuser2)
session.commit()

pokemonuser3 = PokemonUser(user_id=2,pokemon_id=2)
session.add(pokemonuser3)
session.commit()

print "databse updated!"




