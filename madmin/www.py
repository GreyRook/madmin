from __future__ import absolute_import

import urllib
from rw.www import RequestHandler, get, post, url_for
from tornado import gen
from motor import Op, MotorClient
from bson import ObjectId
from bson.json_util import dumps, loads

import rw.db


db = MotorClient(host=rw.cfg['mongodb']['host']).open_sync()


class Main(RequestHandler):

    @gen.engine
    @get('/')
    def database_index(self):
        databases = yield Op(db.database_names)
        self['databases'] = []
        self['stats'] = {}
        for db_name in databases:
            self['databases'].append(db_name)
            self['stats'][db_name] = yield Op(db[db_name].command, "dbstats")
        self.finish(template='list_databases.html')

    @gen.engine
    @get('/m/<db_name>')
    def list_collections(self, db_name):
        """ Open a database and lists all collections within. """
        self['databases'] = yield Op(db.database_names)
        self['current_db'] = db_name

        collections = yield Op(db[db_name].collection_names)
        self['collections'] = []
        self['stats'] = {}
        for collection in collections:
            self['collections'].append(collection)
            self['stats'][collection] = yield Op(db[db_name].command, "collstats", collection)

        self.finish(template='list_collections.html')

    @gen.engine
    @post('/d/')
    def delete_database(self):
        db_name = self.get_argument("db-name")
        yield Op(db.drop_database, db_name)
        self.redirect(url_for(self.database_index))

    @gen.engine
    @post('/c/<db_name>')
    def create_collection(self, db_name):
        col_name = self.get_argument("col-name")
        yield Op(db[db_name].create_collection, col_name)
        self.redirect(url_for(self.list_collections, db_name=db_name))

    @gen.engine
    @post('/d/<db_name>')
    def delete_collection(self, db_name):
        collection = self.get_argument("col-name")
        yield Op(db[db_name][collection].drop)
        self.redirect(url_for(self.list_collections, db_name=db_name))

    @gen.engine
    @post('/m/<db_name>/<col_name>')
    def query_collection(self, db_name, col_name):
        yield self.load_db(db_name, col_name)
        self['query'] = self.get_argument("query", "")
        self.finish(template='list_doc.html')
        
    @gen.engine
    @get('/m/<db_name>/<col_name>')
    def select_collection(self, db_name, col_name):
        """ Open a collection and shows the first 100 entries or so. """
        yield self.load_db(db_name, col_name)
        #cursor_to_all = db[db_name][col_name].find()
        #items = yield Op(cursor_to_all.to_list)
        #self['items'] = []
        #for item in items:
        #    item = {'_id': item.get('_id'), 'data': item}
        #    if '_id' in item['data']:
        #        del item['data']['_id']
        #    self['items'].append(item)
        self.finish(template='list_doc.html')

    @gen.engine
    @get('/m/<db_name>/<col_name>/<doc>')
    def edit_document(self, db_name, col_name, doc):
        """ Load a document and put it into the json editor. """
        yield self.load_db(db_name, col_name)
        # Currently the _id field is not retrieved (_id:0) as it cannot be properly parsed by json.dumps
        self['document'] = yield Op(db[db_name][col_name].find_one, {'_id':ObjectId(doc)}, {'_id':0})
        self['doc_id'] = doc # Add the document id in a separate variable as it is stripped from the result json doc
        self.finish(template='edit_doc.html')

    @gen.engine
    @get('/m/<db_name>/<col_name>/create')
    def create_document(self, db_name, col_name):
        """ Open the json editor with an empty json file. """
        yield self.load_db(db_name, col_name)
        self.finish(template='edit_doc.html')

    @gen.engine
    @post('/m/<db_name>/<col_name>/<doc>/update')
    def update_document(self, db_name, col_name, doc):
        """ Process the json-editor created json and place it in the db.
        Updates when the _id is set, else it creates a new document. """
        # TODO: use mongo's updateOrInsert?
        data = loads(self.get_argument('doc-data-field'))
        if doc:
            yield Op(db[db_name][col_name].update, {'_id' : ObjectId(doc)}, data)
        else:
            yield Op(db[db_name][col_name].insert, data)
        self.redirect(url_for(self.select_collection, db_name=db_name, col_name=col_name))

    @gen.engine
    @post('/m/<db_name>/<col_name>/delete')
    def delete_documents(self, db_name, col_name):
        ids = self.request.arguments["selected-docs"]
        ids = [ObjectId(_id) for _id in ids]
        yield Op(db[db_name][col_name].remove, {'_id': {'$in': ids}})
        self.redirect(url_for(self.select_collection, db_name=db_name, col_name=col_name))

    @get('/help')
    def open_help(self):
        self.finish(template='help.html')

    @gen.coroutine
    def load_db(self, db_name=None, col_name=None):
        self['databases'] = yield Op(db.database_names)
        if db_name is not None:
            self['collections'] = yield Op(db[db_name].collection_names)
            self['current_db'] = db_name

        if col_name is not None:
            self['current_col'] = col_name

    @gen.engine
    @get('/json/<db_name>/<col_name>/')
    def json_table(self, db_name, col_name):
        start = int(self.get_argument('iDisplayStart', 0))
        count = int(self.get_argument('iDisplayLength', 10))
        query_str = self.get_argument('query', None)
        if query_str:
            query = loads(query_str)
        else:
            query = None
        #query = None
        search = self.get_argument('sSearch', None).lower()
        cursor = db[db_name][col_name].find(query)
        total, filtered, db_data = yield [Op(db[db_name][col_name].count), \
                                         Op(cursor.count), \
                                         Op(cursor.limit(count).skip(start).to_list)]
        data = []
        for entry in db_data:
            if entry.has_key('_id'):
                _id = str(entry['_id'])
                del(entry['_id'])
            else:
                _id = ''
            row = ["", "", _id, dumps(entry)]
            if search:
                for field in row:
                    if search in field.lower():
                        data.append(row)
                        break
            else:
                data.append(row)

        self.finish({
            "sEcho": int(self.get_argument('sEcho')),
            "iTotalRecords": total,
            "iTotalDisplayRecords": filtered,
            "aaData": data
        })

