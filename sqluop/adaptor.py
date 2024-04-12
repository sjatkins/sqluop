from uop import db_collection as db_coll, database
from pydantic import BaseModel

class AlchemyCollection(db_coll.DBCollection):
    def __init__(self, table, schema):
        # TODO consider preprocessed statements
        self._table = table
        self.ensure_table(schema)

    def get_table_description(self):
        pass

    def ensure_pydantic_table(self, existing, schema):
        pass

    def ensure_instance_table(self, existing, schema):
        pass

    def ensure_table(self, schema):
        existing = self.get_table_description()
        if isinstance(schema, BaseModel):
            self.ensure_pydantic_table(existing, schema)
        elif isinstance(schema, list):
            # list of UOP attributes
            self.ensure_instance_table(existing, schema)





class AlchemyDatabase(database.Database):
    def __init__(self, index=None, collections=None,
                 tenancy='no_tenants', **dbcredentials):
        pass

