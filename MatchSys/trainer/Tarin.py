
import os

from MatchSys.utils import print_progress_bar


class Training(object):
    """Class of training
    """
    def __init__(self, matchsys, **kwargs):
        self.matchsys = matchsys

        environment_default = os.getenv('CHATTERBOT_SHOW_TRAINING_PROGRESS', True)
        self.show_training_progress = kwargs.get(
            'show_training_progress',
            environment_default
        )
    def build_line_relations(self, statements):
        raise self.TrainerInitializationException()
        # statements[0].next_id = statements[1].id
        # for i in range(1,len(statements)-1):
        #     statements[i].previous_id = statements[i-1].id
        #     statements[i].next_id = statements[i+1].id
        # statements[len(statements)-1].previous_id = statements[len(statements)-2].id
        # return statements

    def preprocessed(self,conversation,**kwargs):
        """
        type_of: string 
            type of conversation : CHAT QA COMMAND MISSION
        persona: string
            *[all] botName[指定bot] userName[指定user]
        [[],[],...]
        preproces data to statements[Statement]
        """
        message_adapter = self.matchsys.get_message_adapter(conversation[0][0])
        statements_to_create = []
        for index,chain in enumerate(conversation):
            statements = message_adapter.process_list(chain,**kwargs)
            print_progress_bar(
                'Chat Trainer',
                index + 1, len(conversation)
            )
            statements_to_create = statements_to_create + self.build_line_relations(statements)
        return statements_to_create
    def add_to_db(self,data):
        self.matchsys.storage.create_many(data)

    def add_to_search(self,data,**kwargs):
        for search_adapter in self.matchsys.search_adapters:
            if search_adapter.need_train:
                try:
                    search_adapter.train(statements=data)
                except Exception as e:
                    print(e)
    def train(self, data,**kwargs):
        statements = self.preprocessed(data,**kwargs)
        self.add_to_db(statements)
        self.add_to_search(statements)

    def _generate_export_data(self):
        result = []
        for statement in self.matchsys.storage.filter():
            if statement.in_response_to:
                result.append([statement.in_response_to, statement.text])

        return result

    def export_for_training(self, file_path='./export.json'):
        """
        Create a file from the database that can be used to
        train other chat bots.
        """
        import json
        export = {'conversations': self._generate_export_data()}
        with open(file_path, 'w+', encoding='utf8') as jsonfile:
            json.dump(export, jsonfile, ensure_ascii=False)
    


    class TrainerInitializationException(Exception):
        """
        Exception raised when a base class has not overridden
        the required methods on the Trainer base class.
        """

        def __init__(self, message=None):
            default = (
                'A training class must be specified before calling train(). '
                'See http://chatterbot.readthedocs.io/en/stable/training.html'
            )
            super().__init__(message or default)