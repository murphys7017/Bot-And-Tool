"""
ChatterBot utility functions
"""


def import_module(dotted_path):
    """
    Imports the specified module based on the
    dot notated import path for the module.
    """
    import importlib

    module_parts = dotted_path.split('.')
    module_path = '.'.join(module_parts[:-1])
    module = importlib.import_module(module_path)

    return getattr(module, module_parts[-1])


def initialize_class(data, *args, **kwargs):
    """
    :param data: A string or dictionary containing a import_path attribute.
    """
    if isinstance(data, dict):
        import_path = data.get('import_path')
        data.update(kwargs)
        Class = import_module(import_path)

        return Class(*args, **data)
    else:
        Class = import_module(data)

        return Class(*args, **kwargs)


def validate_adapter_class(validate_class, adapter_class):
    """
    Raises an exception if validate_class is not a
    subclass of adapter_class.

    :param validate_class: The class to be validated.
    :type validate_class: class

    :param adapter_class: The class type to check against.
    :type adapter_class: class

    :raises: Adapter.InvalidAdapterTypeException
    """
    from service.MatchSys.adapters import Adapter

    # If a dictionary was passed in, check if it has an import_path attribute
    if isinstance(validate_class, dict):

        if 'import_path' not in validate_class:
            raise Adapter.InvalidAdapterTypeException(
                'The dictionary {} must contain a value for "import_path"'.format(
                    str(validate_class)
                )
            )

        # Set the class to the import path for the next check
        validate_class = validate_class.get('import_path')

    if not issubclass(import_module(validate_class), adapter_class):
        raise Adapter.InvalidAdapterTypeException(
            '{} must be a subclass of {}'.format(
                validate_class,
                adapter_class.__name__
            )
        )


def get_response_time(chatbot, statement='Hello'):
    """
    Returns the amount of time taken for a given
    chat bot to return a response.

    :param chatbot: A chat bot instance.
    :type chatbot: ChatBot

    :returns: The response time in seconds.
    :rtype: float
    """
    import time

    start_time = time.time()

    chatbot.get_response(statement)

    return time.time() - start_time


def print_progress_bar(description, iteration_counter, total_items, progress_bar_length=20):
    """
    Print progress bar
    :param description: Training description
    :type description: str

    :param iteration_counter: Incremental counter
    :type iteration_counter: int

    :param total_items: total number items
    :type total_items: int

    :param progress_bar_length: Progress bar length
    :type progress_bar_length: int

    :returns: void
    :rtype: void
    """
    import sys

    percent = float(iteration_counter) / total_items
    hashes = '#' * int(round(percent * progress_bar_length))
    spaces = ' ' * (progress_bar_length - len(hashes))
    sys.stdout.write('\r{0}: [{1}] {2}%'.format(description, hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    if total_items == iteration_counter:
        print('\r')


"""
Response selection methods determines which response should be used in
the event that multiple responses are generated within a logic adapter.
"""
import logging


def get_most_frequent_response(input_statement, response_list, storage=None):
    """
    :param input_statement: A statement, that closely matches an input to the chat bot.
    :type input_statement: Statement

    :param response_list: A list of statement options to choose a response from.
    :type response_list: list

    :param storage: An instance of a storage adapter to allow the response selection
                    method to access other statements if needed.
    :type storage: StorageAdapter

    :return: The response statement with the greatest number of occurrences.
    :rtype: Statement
    """
    matching_response = None
    occurrence_count = -1

    logger = logging.getLogger(__name__)
    logger.info('Selecting response with greatest number of occurrences.')

    for statement in response_list:
        count = len(list(storage.filter(
            text=statement.text,
            in_response_to=input_statement.text)
        ))

        # Keep the more common statement
        if count >= occurrence_count:
            matching_response = statement
            occurrence_count = count

    # Choose the most commonly occuring matching response
    return matching_response


def get_first_response(input_statement, response_list, storage=None):
    """
    :param input_statement: A statement, that closely matches an input to the chat bot.
    :type input_statement: Statement

    :param response_list: A list of statement options to choose a response from.
    :type response_list: list

    :param storage: An instance of a storage adapter to allow the response selection
                    method to access other statements if needed.
    :type storage: StorageAdapter

    :return: Return the first statement in the response list.
    :rtype: Statement
    """
    logger = logging.getLogger(__name__)
    logger.info('Selecting first response from list of {} options.'.format(
        len(response_list)
    ))
    return response_list[0]



"""
filters
"""


def get_recent_repeated_responses(chatbot, conversation, sample=10, threshold=3, quantity=3):
    """
    A filter that eliminates possibly repetitive responses to prevent
    a chat bot from repeating statements that it has recently said.
    """
    from collections import Counter

    # Get the most recent statements from the conversation
    conversation_statements = list(chatbot.storage.filter(
        conversation=conversation,
        order_by=['id']
    ))[sample * -1:]

    text_of_recent_responses = [
        statement.text for statement in conversation_statements
    ]

    counter = Counter(text_of_recent_responses)

    # Find the n most common responses from the conversation
    most_common = counter.most_common(quantity)

    return [
        counted[0] for counted in most_common
        if counted[1] >= threshold
    ]



"""
Match Core
"""
class Doc2VecTool(object):
    model = None
  
    def __init__(self,storage):
        import os
        from service import config
        from gensim.models import Doc2Vec

        self.storage = storage
        self.parrot_similarity_rate = config.parrot_similarity_rate
        if os.path.exists(os.path.abspath(config.parrot_model_path)):
            self.model = Doc2Vec.load(os.path.abspath(config.parrot_model_path))
            print("Parrot started")

    def remove_stopwords(self,str1):
        import jieba
        # return remove_stopwords(jieba.lcut(str1))
        return jieba.lcut_for_search(str1)
    def train(self,statements):
        if self.model is not None:
            self.update_model(statements)
        else:
            self.train_model(statements)

    def build_tokenzied(self,statements):
        from gensim.models.doc2vec import TaggedDocument
        from service.MatchSys.conversation import Statement

        tokenized = []
        for statement in statements:
            statement_data = statement.serialize()
            statement_model_object = Statement(**statement_data)
            if statement_model_object.snowkey > 0:
                tokenized.append(TaggedDocument(statement_model_object.search_text.split(' '),tags=[statement_model_object.snowkey]))
        return tokenized
    
    def train_model(self, statements):
        from gensim.models import Doc2Vec

        tokenized = self.build_tokenzied(statements)

        self.model = Doc2Vec(tokenized,min_count=1,window=4,sample=1e-3,negative=5,workers=4)
        self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=100)
    
    def save_model(self,save_path):
        import os
        self.model.save(os.path.join(save_path,'model.pkl'))
        
    def inferred2string(self,msg):
        inferred_vector = self.model.infer_vector(doc_words=self.remove_stopwords(msg))
        
        sims = self.model.dv.most_similar([inferred_vector],topn=20)
        res = []
        for sim in sims:
            if sim[1] >= self.parrot_similarity_rate:
                res.append( self.storage.get_statement_by_snowkey(sim[0]))
        return res
    
    def update_model(self,statements):
        tokenized = self.build_tokenzied(statements)

        if len(tokenized) > 0:
            self.model.build_vocab(tokenized,update=True) #注意update = True 这个参数很重要
            self.model.train(tokenized,total_examples=self.model.corpus_count,epochs=100)