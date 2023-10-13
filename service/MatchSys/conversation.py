from pytz import UTC
from datetime import datetime
from dateutil import parser as date_parser

from service.MatchSys.utils_bk import IdWorker

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
        'conversation',
        'persona',
        'tags',
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

    def get_tags(self):
        """
        Return the list of tags for this statement.
        """
        return self.tags

    def add_tags(self, *tags):
        """
        Add a list of strings to the statement as tags.
        """
        self.tags.extend(tags)

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
        'conversation',
        'persona',
        'tags',
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
        self.snowkey = kwargs.get('snowkey','')
        self.text = kwargs.get('text',text)
        self.search_text = kwargs.get('search_text', '')
        self.conversation = kwargs.get('conversation', '')
        self.persona = kwargs.get('persona', '')
        self.tags = kwargs.pop('tags', [])
        self.next_id = kwargs.get('next_id', '')
        self.previous_id = kwargs.get('previous_id', '')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.type_of = kwargs.get('type_of', 'CHAT')
        self.source = kwargs.get('source', 'UNKNOWN')
        self.matedata = kwargs.get('matedata', {})
        self.intent = kwargs.get('intent', {})
        self.mark = kwargs.get('mark', 1)

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