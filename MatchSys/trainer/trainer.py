import os

class Trainer(object):
    """
    训练器基类

    :param boolean show_training_progress: Show progress indicators for the
           trainer. The environment variable ``CHATTERBOT_SHOW_TRAINING_PROGRESS``
           can also be set to control this. ``show_training_progress`` will override
           the environment variable if it is set.
    """

    def __init__(self, matchsys, **kwargs):
        self.matchsys = matchsys

        environment_default = os.getenv('CHATTERBOT_SHOW_TRAINING_PROGRESS', True)
        self.show_training_progress = kwargs.get(
            'show_training_progress',
            environment_default
        )

    def get_preprocessed_statement(self, input_statement):
        """
        Preprocess the input statement.
        """
        for preprocessor in self.matchsys.preprocessors:
            input_statement = preprocessor(input_statement)

        return input_statement

    def train(self, *args, **kwargs):
        """
        This method must be overridden by a child class.
        """
        raise self.TrainerInitializationException()
    def save(self, *args, **kwargs):
        pass
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
