import json
from pytz import UTC
from datetime import datetime
from dateutil import parser as date_parser
class SemanticBase(object):
    statement_field_names = [
        'id',
        'A0',
        'A1',
        'A2',
        'A3',
        'A4',
        'ADV',
        'BNF',
        'CND',
        'CRD',
        'DGR',
        'DIR',
        'DIS',
        'EXT',
        'FRQ',
        'LOC',
        'MNR',
        'PRP',
        'QTY',
        'TMP',
        'TPC',
        'predicate',
        'PSR',
        'PSE',
    ]

    extra_statement_field_names = []
    def get_not_null(self):
        res = {}
        for name in self.statement_field_names:
            value = self.__dict__[name]
            if value:
                if value != '':
                    if isinstance(value,int):
                        pass
                    else:
                        value = value.strip()
                        if len(value) > 0:
                            res[name] = value 
        return res
    

    def __repr__(self):
        return '<Semantic predicate:%s, A0:%s, A1:%s, A2:%s>' % (self.predicate,self.A0,self.A1,self.A2)

    def get_statement_field_names(self):
        """
        Return the list of field names for the statement.
        """
        return self.statement_field_names + self.extra_statement_field_names

    def serialize(self):
        """
        :returns: A dictionary representation of the statement object.
        :rtype: dict
        """
        data = {}

        for field_name in self.get_statement_field_names():
            format_method = getattr(self, 'get_{}'.format(
                field_name
            ), None)

            if format_method:
                data[field_name] = format_method()
            else:
                data[field_name] = getattr(self, field_name)

        return data
class Semantic(SemanticBase):
    statement_field_names = [
        'id',
        'A0',
        'A1',
        'A2',
        'A3',
        'A4',
        'ADV',
        'BNF',
        'CND',
        'CRD',
        'DGR',
        'DIR',
        'DIS',
        'EXT',
        'FRQ',
        'LOC',
        'MNR',
        'PRP',
        'QTY',
        'TMP',
        'TPC',
        'predicate',
        'PSR',
        'PSE',
    ]

    extra_statement_field_names = []

    def __init__(self,**kwargs):
        for field in self.statement_field_names:
            setattr(self,field,None)
        for key,value in kwargs.items():
            setattr(self,key,value)

    

    def get_statement_field_names(self):
        """
        Return the list of field names for the statement.
        """
        return self.statement_field_names + self.extra_statement_field_names

    def serialize(self):
        """
        :returns: A dictionary representation of the statement object.
        :rtype: dict
        """
        data = {}

        for field_name in self.get_statement_field_names():
            format_method = getattr(self, 'get_{}'.format(
                field_name
            ), None)

            if format_method:
                data[field_name] = format_method()
            else:
                data[field_name] = getattr(self, field_name)

        return data


class StatementMixin(object):
    """
    This class has shared methods used to
    normalize different statement models.
    """

    statement_field_names = [
        'id',
        'text',
        'search_text',
        'intent',
        'semantics',
        'conversation',
        'persona',
        'previous_id',
        'next_id',
        'created_at',
        'type_of',
        'source',
        'mark',
        'matedata',
    ]

    extra_statement_field_names = []

    def get_statement_field_names(self):
        """
        Return the list of field names for the statement.
        """
        return self.statement_field_names + self.extra_statement_field_names

    def serialize(self):
        """
        :returns: A dictionary representation of the statement object.
        :rtype: dict
        """
        data = {}

        for field_name in self.get_statement_field_names():
            format_method = getattr(self, 'get_{}'.format(
                field_name
            ), None)

            if format_method:
                data[field_name] = format_method()
            else:
                data[field_name] = getattr(self, field_name)

        return data

# TODO: 添加对话打分，区分对话的好坏
class Statement(StatementMixin):
    """
    A statement represents a single spoken entity, sentence or
    phrase that someone can say.
    """

    __slots__ = (
        'id',
        'text',
        'search_text',
        'intent',
        'semantics',
        'conversation',
        'persona',
        'previous_id',
        'next_id',
        'created_at',
        'type_of',
        'source',
        'mark',
        'confidence',
        'storage',
        'matedata',
        'history_statements',
        'predict_statements'
    )


    def __init__(self, text, **kwargs):

        self.id = kwargs.get('id')
        self.text = kwargs.get('text',text)
        self.search_text = kwargs.get('search_text', '')
        self.conversation = kwargs.get('conversation', '')
        self.persona = kwargs.get('persona', '')
        self.next_id = kwargs.get('next_id', '')
        self.previous_id = kwargs.get('previous_id', '')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.type_of = kwargs.get('type_of', 'CHAT')
        self.source = kwargs.get('source', 'UNKNOWN')
        self.matedata = kwargs.get('matedata', '')
        self.intent = kwargs.get('intent', {})
        self.mark = kwargs.get('mark', 1)
        self.semantics = kwargs.get('semantics',[])
        if isinstance(self.intent, str):
            pass
        else:
            self.intent = json.dumps(self.intent)

        if isinstance(self.matedata, str):
            pass
        else:
            self.matedata = json.dumps(self.matedata)

        if not isinstance(self.created_at, datetime):
            self.created_at = date_parser.parse(self.created_at)

        # Set timezone to UTC if no timezone was provided
        if not self.created_at.tzinfo:
            self.created_at = self.created_at.replace(tzinfo=UTC)

        # This is the confidence with which the chat bot believes
        # this is an accurate response. This value is set when the
        # statement is returned by the chat bot.
        self.confidence = 0

        self.storage = None

        self.history_statements = []
        self.predict_statements = []

    def __str__(self):
        return self.text

    def __repr__(self):
        return '<Statement text:%s, persona:%s, type_of:%s>' % (self.text,self.persona,self.type_of)

    def save(self):
        """
        Save the statement in the database.
        """
        self.storage.update(self)
    def set_total_statements(self,total_statements):
        self.total_statements = total_statements