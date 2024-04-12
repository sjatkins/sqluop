from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Dictionary containing field names and their types
field_dict = {
    'id': Integer,
    'name': String,
    'age': Integer,
    'email': String
}

# Create a base class for declarative models
Base = declarative_base()

# Generate the SQLAlchemy table dynamically
class DynamicTable(Base):
    __tablename__ = 'dynamic_table'
    id = Column(Integer, primary_key=True)

# Add columns to the dynamically generated table
for field_name, field_type in field_dict.items():
    setattr(DynamicTable, field_name, Column(field_type))

# Create a database engine and table
engine = create_engine('sqlite:///dynamic_table.db', echo=True)
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create a new record
new_record = DynamicTable(name='John Doe', age=30, email='john@example.com')
session.add(new_record)
session.commit()

# Query the records
records = session.query(DynamicTable).all()
for record in records:
    print(record.id, record.name, record.age, record.email)

# Close the session
session.close()

######

"""Sure! If you want to generate an SQLAlchemy table from a Pydantic class using the internal description of the Pydantic fields (field names and types), you can follow this approach:

python"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Define your Pydantic model
class Person(BaseModel):
    id: int
    name: str
    age: int
    email: str

# Create a base class for declarative models
Base = declarative_base()

# Generate the SQLAlchemy table dynamically using the Pydantic model description
def generate_table_from_pydantic(model, base):
    class Table(base):
        __tablename__ = model.__name__.lower()
        id = Column(Integer, primary_key=True)

    # Add columns to the dynamically generated table
    for field_name, field_type in model.__annotations__.items():
        if field_name != 'id':
            setattr(Table, field_name, Column(field_type))

    return Table

# Create the SQLAlchemy table dynamically
PersonTable = generate_table_from_pydantic(Person, Base)

# Create a database engine and table
engine = create_engine('sqlite:///person_table.db', echo=True)
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Create a new record using Pydantic model
new_record = Person(id=1, name='John Doe', age=30, email='john@example.com')

# Convert Pydantic model to SQLAlchemy model
person_table_record = PersonTable(**new_record.dict())

# Add the SQLAlchemy model to the session and commit
session.add(person_table_record)
session.commit()

# Query the records
records = session.query(PersonTable).all()
for record in records:
    print(record.id, record.name, record.age, record.email)

# Close the session
session.close()

"""
In this example, the generate_table_from_pydantic function dynamically generates an SQLAlchemy table using the Pydantic model's annotations (field names and types). The function then creates the table with the specified columns, similar to the previous example.

Make sure to install the sqlalchemy and pydantic packages before running the code. Adapt and modify the example according to your specific use case.
"""


