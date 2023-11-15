from .storage_adapter import StorageAdapter

class SQLStorageAdapter(StorageAdapter):
    """
    The SQLStorageAdapter allows ChatterBot to store conversation
    data in any database supported by the SQL Alchemy ORM.

    All parameters are optional, by default a sqlite database is used.

    It will check if tables are present, if they are not, it will attempt
    to create the required tables.

    :keyword database_uri: eg: sqlite:///database_test.sqlite3',
        The database_uri can be specified to choose database driver.
    :type database_uri: str
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.database_uri = kwargs.get('database_uri', False)

        # None results in a sqlite in-memory database as the default
        if self.database_uri is None:
            self.database_uri = 'sqlite://'

        # Create a file database if the database is not a connection string
        if not self.database_uri:
            self.database_uri = 'sqlite:///db.sqlite3'

        self.engine = create_engine(self.database_uri,
                                    pool_size=100,
                                    pool_timeout=2,
                                    pool_recycle=30,
                                    max_overflow=0
                                    )

        if self.database_uri.startswith('sqlite://'):
            from sqlalchemy.engine import Engine
            from sqlalchemy import event

            @event.listens_for(Engine, 'connect')
            def set_sqlite_pragma(dbapi_connection, connection_record):
                dbapi_connection.execute('PRAGMA journal_mode=WAL')
                dbapi_connection.execute('PRAGMA synchronous=NORMAL')

        if not self.engine.dialect.has_table(self.engine.connect(), 'Statement'):
            self.create_database()

        self.Session = sessionmaker(bind=self.engine, expire_on_commit=True)
    


    def get_statement_model(self):
        """
        Return the statement model.
        """
        from MatchSys.storage.model_definition import Statement
        return Statement

    def get_semantic_model(self):
        """
        Return the conversation model.
        """
        from MatchSys.storage.model_definition import Semantic
        return Semantic

    def model_to_object(self, statement):
        from MatchSys.object_definition import Statement as StatementObject
        from MatchSys.object_definition import Semantic as SemanticObject
        from MatchSys.storage.model_definition import Statement as StatementModel
        from MatchSys.storage.model_definition import Semantic as SemanticModel
        if isinstance(statement, SemanticModel):
            return StatementObject(**statement.serialize())
        if isinstance(statement, StatementModel):
            return SemanticObject(**statement.serialize())

    def count(self):
        """
        Return the number of entries in the database.
        """
        Statement = self.get_model('statement')

        session = self.Session()
        statement_count = session.query(Statement).count()
        session.close()
        return statement_count

    def remove(self, statement_text):
        """
        Removes the statement that matches the input text.
        Removes any responses from statements where the response text matches
        the input text.
        """
        Statement = self.get_model('statement')
        session = self.Session()

        query = session.query(Statement).filter_by(text=statement_text)
        record = query.first()

        session.delete(record)

        self._session_finish(session)

    def get_statement_by_id(self, id):
        Statement = self.get_model('statement')
        session = self.Session()

        query = session.query(Statement).filter_by(id=id).first()
        query = self.model_to_object(query)
        session.close()
        return query
    def get_statements_by_id(self, id):
        Statement = self.get_model('statement')
        session = self.Session()

        query = session.query(Statement).filter_by(id=id).all()
        session.close()
        return query
    def get_statements_by_previous_id(self, id):
        Statement = self.get_model('statement')
        session = self.Session()

        query = session.query(Statement).filter_by(previous_id=id).all()
        for statement in query:
            yield self.model_to_object(statement)
        
        session.close()
    def get_statements_by_text(self, text):
        Statement = self.get_model('statement')
        session = self.Session()

        query = session.query(Statement).filter_by(text=text).all()
        for statement in query:
            yield self.model_to_object(statement)
        
        session.close()
    # TODO: 输入为semantic 先匹配predicate和对应元素非空的，然后根据规则返回结果
    def get_semantics_by_text(self, text):
        Semantic = self.get_model('semantic')
        session = self.Session()
        res = session.query(Semantic).filter_by(predicate=text).all()
        for semantic in res:
            yield self.model_to_object(semantic)
        
        session.close()
        
    # def semantic_filter(self, input_semantic):
    #     Semantic = self.get_model('semantic')
    #     session = self.Session()

    #     semantics = session.query(Semantic).filter(
    #         Semantic.predicate == input_semantic.predicate
            
    #         )
    #     session.close()
    #     return semantics

    def filter(self, **kwargs):
        """
        Returns a list of objects from the database.
        The kwargs parameter can contain any number
        of attributes. Only objects which contain all
        listed attributes and in which all values match
        for all listed attributes will be returned.
        """
        from sqlalchemy import or_

        Statement = self.get_model('statement')


        session = self.Session()

        page_size = kwargs.pop('page_size', 1000)
        order_by = kwargs.pop('order_by', None)
        exclude_text = kwargs.pop('exclude_text', None)
        exclude_text_words = kwargs.pop('exclude_text_words', [])
        persona_not_startswith = kwargs.pop('persona_not_startswith', None)
        search_text_contains = kwargs.pop('search_text_contains', None)

        if len(kwargs) == 0:
            statements = session.query(Statement).filter()
        else:
            statements = session.query(Statement).filter_by(**kwargs)

        if exclude_text:
            statements = statements.filter(
                ~Statement.text.in_(exclude_text)
            )

        if exclude_text_words:
            or_word_query = [
                Statement.text.ilike('%' + word + '%') for word in exclude_text_words
            ]
            statements = statements.filter(
                ~or_(*or_word_query)
            )

        if persona_not_startswith:
            statements = statements.filter(
                ~Statement.persona.startswith('bot:')
            )

        if search_text_contains:
            or_query = [
                Statement.search_text.contains(word) for word in search_text_contains.split(' ')
            ]
            statements = statements.filter(
                or_(*or_query)
            )

        if order_by:

            if 'created_at' in order_by:
                index = order_by.index('created_at')
                order_by[index] = Statement.created_at.asc()

            statements = statements.order_by(*order_by)

        total_statements = statements.count()

        for start_index in range(0, total_statements, page_size):
            for statement in statements.slice(start_index, start_index + page_size):
                yield self.model_to_object(statement)

        session.close()

    def create(self, **kwargs):
        """
        Creates a new statement matching the keyword arguments specified.
        Returns the created statement.
        """
        Statement = self.get_model('statement')

        session = self.Session()


        # if 'search_text' not in kwargs:
        #     kwargs['search_text'] = self.tagger.get_text_index_string(kwargs['text'])

        # if 'search_in_response_to' not in kwargs:
        #     in_response_to = kwargs.get('in_response_to')
        #     if in_response_to:
        #         kwargs['search_in_response_to'] = self.tagger.get_text_index_string(in_response_to)

        statement = Statement(**kwargs)

        session.add(statement)

        session.flush()

        session.refresh(statement)

        statement_object = self.model_to_object(statement)

        self._session_finish(session)

        return statement_object

    def create_many(self, statements):
        import time
        """
        Creates multiple statement entries.
        """
        start = time.perf_counter()
        Statement = self.get_model('statement')
        Semantic = self.get_model('semantic')

        session = self.Session()

        create_statements = []


        for statement in statements:

            statement_data = statement.serialize()
            semantics_data = statement_data.pop('semantics',[])

            statement_model_object = Statement(**statement_data)
            

            semantics = []
            for semantic in semantics_data:
                semantics.append(Semantic(**semantic.serialize()))

            statement_model_object.semantics = semantics
            create_statements.append(statement_model_object)
        

        session.add_all(create_statements)
        session.commit()
        end = time.perf_counter()
        print("运行时间：", end - start, "秒")

    def update(self, statement):
        """
        Modifies an entry in the database.
        Creates an entry if one does not exist.
        """
        Statement = self.get_model('statement')

        if statement is not None:
            session = self.Session()
            record = None

            if hasattr(statement, 'id') and statement.id is not None:
                record = session.query(Statement).get(statement.id)
            else:
                record = session.query(Statement).filter(
                    Statement.text == statement.text,
                    Statement.conversation == statement.conversation,
                ).first()

                # Create a new statement entry if one does not already exist
                if not record:
                    record = Statement(
                        text=statement.text,
                        conversation=statement.conversation,
                        persona=statement.persona
                    )

            # Update the response value
            record.in_response_to = statement.in_response_to

            record.created_at = statement.created_at


            # if statement.in_response_to:
            #     record.search_in_response_to = self.tagger.get_text_index_string(statement.in_response_to)


            session.add(record)

            self._session_finish(session)

    def get_random(self):
        """
        Returns a random statement from the database.
        """
        import random

        Statement = self.get_model('statement')

        session = self.Session()
        count = self.count()
        if count < 1:
            raise self.EmptyDatabaseException()

        random_index = random.randrange(0, count)
        random_statement = session.query(Statement)[random_index]

        statement = self.model_to_object(random_statement)
        session.close()
        return statement

    def drop(self):
        """
        Drop the database.
        """
        Statement = self.get_model('statement')

        session = self.Session()

        session.query(Statement).delete()

        session.commit()
        session.close()

    def create_database(self):
        """
        Populate the database with the tables.
        """
        from MatchSys.storage.model_definition import Base
        Base.metadata.create_all(self.engine)

    def _session_finish(self, session, statement_text=None):
        from sqlalchemy.exc import InvalidRequestError
        try:
            session.commit()
        except InvalidRequestError:
            # Log the statement text and the exception
            self.logger.exception(statement_text)
        finally:
            session.close()
