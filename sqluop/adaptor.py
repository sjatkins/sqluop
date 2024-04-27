from uop import db_collection as db_coll, database
from pydantic import BaseModel
from sqlalchemy import inspect, PrimaryKeyConstraint, Column, Date, DateTime, Double, Integer, Boolean,  String, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

python_sql = dict(
    str = String,
    int = Integer,
    float = Float,
    bool = Boolean,
    json = JSON,
    email = String,
    phone = String,
    long = Double,
    uuid = String,
    string = String,
    text = Text,
    date = Date,
    datetime = DateTime
)

def column_type(pydantic_type):
    if isinstance(pydantic_type, str):
        return python_sql[pydantic_type]
    elif issubclass(pydantic_type, BaseModel):
        return JSON # stringified json
    elif isinstance(pydantic_type, type):
        if pydantic_type == str:
            return String
        elif pydantic_type == int:
            return Integer
        elif pydantic_type == float:
            return Float
        elif pydantic_type == bool:
            return Boolean

    print(f'returning JSON sql column type for {pydantic_type}')
    return JSON

Base = declarative_base()


def pks_and_columns(model):
    fields = model.__fields__
    keys = ['id'] if 'id' in fields else []
    columns = {}
    for field_name, field_info in model.__fields__.items():
        field_type = field_info.type_
        sql_type = column_type(field_type)
        columns[field_name] = Column(sql_type)
    return keys, columns

def table_from_pydantic(model, base, table_name=''):
    if not table_name:
        table_name = model.__name__.lower()
    primary_keys, columns = pks_and_columns(model)
    args = dict(
        __tablename__ = table_name,
        __table_args__ = (PrimaryKeyConstraint(*primary_keys),{}),
        **columns
    )
    return type(table_name, (base,), args)


def generate_table_from_pydantic(model, base, table_name=''):
    #
    #    __tablename__ = table_name or model.__name__.lower()
    #    id = Column(String, primary_key=True)







    if not table_name:
        table_name = model.__name__.lower()
    args = dict(
        __tablename__ = table_name,
        id = Column(String, primary_key=True)
    )
    table = type(table_name, (base,), args)


    # Add columns to the dynamically generated table
    for field_name, field_info in model.__fields__.items():
        field_type = field_info.type_
        if field_name != 'id':
            sql_type = column_type(field_type)
            setattr(table, field_name, Column(sql_type))

    return table


class AlchemyCollection(db_coll.DBCollection):
    def __init__(self, table_name, schema, indexed=False, tenant_modifier=None, *constraints):
        # TODO consider preprocessed statements
        self._table_name = table_name
        self._table = self.ensure_table(schema)
        super().__init__(self._table, indexed, tenant_modifier, *constraints)

    def get_existing_table(self):
        pass

    def ensure_pydantic_table(self, schema):
        return generate_table_from_pydantic(schema, Base)

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
    def __init__(self, db_name, index=None, collections=None, db_brand='sqlite',
                 tenancy='no_tenants', **dbcredentials):
        self._db_name = db_name
        self._connection_string = self.get_connection_string(db_brand, dbcredentials)
        self._engine = create_engine(self._connection_string)
        self._tables = self.get_tables()

    def get_connection_string(self, db_brand, dbcredentials):
        default = f'{db_brand}:///{self._db_name}'
        return default

    def get_tables(self):
        metadata = Base.metadata
        metadata.reflect(self._engine)
        return metadata.tables



