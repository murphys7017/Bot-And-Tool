from .message_adapter import MessageAdapter

class TextMessageAdapter(MessageAdapter):
    """
    This is an abstract class that represents the interface
    that all message adapters should implement.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def process(self, message, **kwargs):
        # read the message

        # Get Text message
        input_statement = self.text_process(text=message,**kwargs)

        # Add Other Info

        # 获取Statement
        return input_statement
    def process_list(self, message_list, **kwargs):
        # read the message

        # Get Text message
        input_statements = self.text_process_list(message_list,**kwargs)

        # Add Other Info

        # 获取Statement
        return input_statements