from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///pilgrimages.db')
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

# Delete PilgrimageName if exisitng.
session.query(PilgrimageName).delete()
# Delete StateName if exisitng.
session.query(StateName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="santhisri",
             email="santhisrigovind@gmail.com",
             picture='http://www.enchanting-costarica.com/wp-content/'
             'uploads/2018/02/jcarvaja17-min.jpg')
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample pilgrimage names
Pilgrimage1 = PilgrimageName(name="BODHGAYA",
                             user_id=1)
session.add(Pilgrimage1)
session.commit()

Pilgrimage2 = PilgrimageName(name="HAMPI",
                             user_id=1)
session.add(Pilgrimage2)
session.commit

Pilgrimage3 = PilgrimageName(name="TIRUPATI",
                             user_id=1)
session.add(Pilgrimage3)
session.commit()

Pilgrimage4 = PilgrimageName(name="SHIRDI",
                             user_id=1)
session.add(Pilgrimage4)
session.commit()

Pilgrimage5 = PilgrimageName(name="RAMESHWARAM",
                             user_id=1)
session.add(Pilgrimage5)
session.commit()

Pilgrimage6 = PilgrimageName(name="VRINDAVAN",
                             user_id=1)
session.add(Pilgrimage6)
session.commit()

# Populare pilgrimages with models for testing
# Using different users for pilgrimages names year also
State1 = StateName(name="Bihar",
                   address="Mahabodhi temple complex in Gaya district",
                   god="Gautama Buddha",
                   area="20.2km",
                   date=datetime.datetime.now(),
                   pilgrimagenameid=1,
                   user_id=1)
session.add(State1)
session.commit()

State2 = StateName(name="Karnataka",
                   address="
                   Located along the Tungabhadra river in Ballari district",
                   god="Parvati",
                   area="4,187.24 ha",
                   date=datetime.datetime.now(),
                   pilgrimagenameid=2,
                   user_id=1)
session.add(State2)
session.commit()

State3 = StateName(name="Andhra Pradesh",
                   address="Tirupati in Chittoor District",
                   god="Sri Venkateswara",
                   area="27.44 km",
                   date=datetime.datetime.now(),
                   pilgrimagenameid=3,
                   user_id=1)
session.add(State3)
session.commit()

State4 = StateName(name="Shirdi",
                   address="located in Rahata Taluka in Ahmednagar District",
                   god="Sai Baba",
                   area="13km",
                   date=datetime.datetime.now(),
                   pilgrimagenameid=4,
                   user_id=1)
session.add(State4)
session.commit()

State5 = StateName(name="Rameshwaram",
                   address="Tamil Nadu",
                   god="Shiva",
                   area="55km",
                   date=datetime.datetime.now(),
                   pilgrimagenameid=5,
                   user_id=1)
session.add(State5)
session.commit()

State6 = StateName(name="Uttar Pradesh",
                   address="Mathura District",
                   god="Krishna",
                   area="63,005",
                   date=datetime.datetime.now(),
                   pilgrimagenameid=6,
                   user_id=1)
session.add(State6)
session.commit()

print("Your states database has been inserted!")
