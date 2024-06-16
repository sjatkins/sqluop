from uop import db_collection as db_coll, database
from pydantic import BaseModel
from sqlalchemy import (inspect, PrimaryKeyConstraint, Column, Date,
                        DateTime, Double, Integer, Boolean,  String,
                        Text, Float, JSON, create_engine, Index, Table)
from sqlalchemy.ext.declarative import declarative_base
from uopmeta.schemas import meta
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
    has_id = 'id' in fields
    keys = ['id'] if has_id else []
    columns = {}
    for field_name, field_info in model.__fields__.items():
        if field_name == 'kind':
            continue
        field_type = field_info.type_
        sql_type = column_type(field_type)
        columns[field_name] = Column(sql_type)
        if not has_id:
            keys.append(field_name)
    print(f'keys: {keys}')
    return keys, columns

def make_table(base, table_name, columns, keys):
    return type(table_name, (base,), dict(
        __tablename__ = table_name,
        __table_args = (PrimaryKeyConstraint(*keys), {}),
        **columns))


def table_from_pydantic(model, base, table_name=''):
    if not table_name:
        table_name = model.__name__.lower()
    primary_keys, columns = pks_and_columns(model)
    return make_table(base, table_name, columns, primary_keys)


def table_from_attrs(attrs, base, table_name):
    columns = {}
    for attr in attrs:
        sql_type = column_type(attr.type)
        columns[attr.name] = Column(sql_type)
    return make_table(base, table_name, columns, ('id',))

def create_index(table, columns):
    pass

class AlchemyCollection(db_coll.DBCollection):
    def __init__(self, table, indexed=False, tenant_modifier=None, *constraints):
        # TODO consider preprocessed statements
        self._table = table
        super().__init__(self._table, indexed=indexed, tenant_modifier=tenant_modifier, *constraints)

    def add_index(self, index_name, field_names):
        columns = [self._table.getattr(s) for s in field_names]
        Index(None, _table=self._table, )

    def ensure_pydantic_table(self, schema):
        return table_from_pydantic(schema, Base, self._table_name)

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
    def __init__(self, db_name, collections=None, db_brand='sqlite',
                 tenancy='no_tenants', **dbcredentials):
        self._db_name = db_name
        self._connection_string = self.get_connection_string(db_brand, dbcredentials)
        self._engine = create_engine(self._connection_string)
        self._tables = self.get_tables()
        super().__init__(**dbcredentials)

    def get_existing_table(self, table_name):
        return self.get_tables().get(table_name)

    def get_connection_string(self, db_brand, dbcredentials):
        default = f'{db_brand}:///{self._db_name}'
        return default

    def get_managed_collection(self, coll_name):
        coll = self.get_existing_collection(coll_name)
        if not coll:
            table = self.get_existing_table(coll_name)
            if table:
                coll = AlchemyCollection(table)
            else:
                raise Exception(f'Expected existing table named {coll_name}')
        return coll

    def get_standard_collection(self, kind, tenant_modifier=None, name=''):
        coll_name = name or database.uop_collection_names[kind]
        coll = self.get_existing_collection(coll_name)
        if coll:
            return coll
        schema = meta.kind_map[kind]
        table = self.get_existing_table(coll_name)
        if not table:
            # TODO remmeber to add secondary indices.
            indices = meta.secondary_indices.get(kind)
            table = table_from_pydantic(schema, Base, coll_name)
        return AlchemyCollection(table, tenant_modifier=tenant_modifier)

    def get_instance_collection(self, cls):
        coll_name = cls.instance_collection or self.random_collection_name()

        table = self.get_existing_table(coll_name)
        if not table:
            attrs = cls.attributes
            table = table_from_attrs(attrs, Base, coll_name)
        return AlchemyCollection(table)

    def get_tables(self):
        metadata = Base.metadata
        metadata.reflect(self._engine)
        return metadata.tables



def test_basics():
    metadata = Base.metadata
    db = AlchemyDatabase('foobar')