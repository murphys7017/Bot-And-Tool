from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr, declarative_base

from ..object_definition import StatementMixin,SemanticBase
# TODO: 修改config引入来源
from MatchSys import config
config.initialize(**{})

print("Starting initialization of ModelBase")

class ModelBase(object):
    """
    An augmented base class for SqlAlchemy models.
    """

    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase class name as the name of the table.
        """
        return cls.__name__.lower()

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )


Base = declarative_base(cls=ModelBase)

semantic_association_table = Table(
    'semantic_association',
    Base.metadata,
    Column('semantic_id', Integer, ForeignKey('semantic.id')),
    Column('statement_id', Integer, ForeignKey('statement.id'))
)

class Semantic(Base, SemanticBase):
    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase class name as the name of the table.
        """
        return cls.__name__.lower()
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    predicate = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    A0 = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    A1 = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    A2 = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    A3 = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    A4 = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    ADV = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    BNF = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    CND = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    CRD = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    DGR = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    DIR = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    DIS = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    EXT = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    FRQ = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    LOC = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    MNR = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    PRP = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    QTY = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    TMP = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    TPC = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    PRD = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    PSR = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    PSE = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )



class Statement(Base, StatementMixin):
    """
    A Statement represents a sentence or phrase.
    """

    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase class name as the name of the table.
        """
        return cls.__name__.lower()

    id = Column(
        Integer,
        primary_key=True
    )

    previous_id = Column(
        Integer
    )
    next_id = Column(
        Integer
    )

    text = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )

    search_text = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH),
        nullable=False,
        server_default=''
    )
    # TODO: delete
    intent = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH),
        server_default=''
    )
    

    conversation = Column(
        String(config.CONVERSATION_LABEL_MAX_LENGTH),
        nullable=False,
        server_default=''
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    type_of = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    source = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    matedata = Column(
        String(config.STATEMENT_TEXT_MAX_LENGTH)
    )
    mark = Column(
        Integer
    )

    semantics = relationship(
        'Semantic',
        secondary=lambda: semantic_association_table,
        backref='statement'
    )

    persona = Column(
        String(config.PERSONA_MAX_LENGTH),
        nullable=False,
        server_default=''
    )

