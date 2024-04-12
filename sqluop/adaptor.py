from uop import db_collection as db_coll, database
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
def generate_table_from_pydantic(model, base):
    class Table(base):
        __tablename__ = model.__name__.lower()
        id = Column(Integer, primary_key=True)

    # Add columns to the dynamically generated table
    for field_name, field_type in model.__annotations__.items():
        if field_name != 'id':
            setattr(Table, field_name, Column(field_type))

    return Table


class AlchemyCollection(db_coll.DBCollection):
    def __init__(self, table_name, schema):
        # TODO consider preprocessed statements
        self._table_name = table_name
        self._table = self.ensure_table(schema)

    def get_existing_table(self):
        pass

    def ensure_pydantic_table(self, schema):
        pass

    def ensure_instance_table(self, existing, schema):
        pass

    def ensure_table(self, schema):
        table = self.get_existing_table()
        if not table:
            if isinstance(schema, BaseModel):
                table = self.ensure_pydantic_table(schema)
            elif isinstance(schema, list):
                # list of UOP attribuntes
                table = self.ensure_instance_table(schema)
        return table





class AlchemyDatabase(database.Database):
    def __init__(self, index=None, collections=None,
                 tenancy='no_tenants', **dbcredentials):
        pass

