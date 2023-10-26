import yaml

def initialize(**kwargs):
    # bot名称 同时也是识别id
    global BOT_NAME
    # max_time_between_conversations 超过这个时常就判断为两个对话
    global MAX_TIME_BETWEEN_CONVERSATION
    global LTP_MODEL_PATH
    global MESSAGE_ADAPTERS
    global STORAGE_ADAPTER
    global LOGIC_ADAPTERS
    global LEARNING_ADAPTERS
    global VECTOR_SIMILARITY_RATE

    global data_path
    global parrot_model_path
    global he_feng_key
    global activate_rasa
    global rasa_url
    global if_start_rasa
    global command_similarity_rate

    global text_vec_model_path
    global STOP_WORDS_PATH
    global STATEMENT_TEXT_MAX_LENGTH
    global CONVERSATION_LABEL_MAX_LENGTH
    global PERSONA_MAX_LENGTH
    global TAG_NAME_MAX_LENGTH
    global TAG_TYPE_MAX_LENGTH

    data_path = './data/'
    # './data/ParrotModel/'
    # D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\service\MatchSys\Data
    parrot_model_path = r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\service\MatchSys\Data'

    if_start_rasa=True
    command_similarity_rate=0.8
    config_file = open('./config.yml', encoding='utf-8')
    yml_config = yaml.load(config_file, Loader=yaml.FullLoader)

    BOT_NAME = kwargs.get('bot_name', yml_config['bot_name'])
    MAX_TIME_BETWEEN_CONVERSATION = kwargs.get('max_time_between_conversation',yml_config['max_time_between_conversation'])
    LTP_MODEL_PATH = kwargs.get('ltp_model_path',yml_config['ltp_model_path'])
    MESSAGE_ADAPTERS = kwargs.get('message_adapters',yml_config['message_adapter'])
    STORAGE_ADAPTER = kwargs.get('storage_adapter',yml_config['storage_adapter'])
    LOGIC_ADAPTERS = kwargs.get('logic_adapters',yml_config['logic_adapter'])
    LEARNING_ADAPTERS = kwargs.get('learing_adapters',yml_config['learing_adapter'])
    VECTOR_SIMILARITY_RATE = kwargs.get('vector_simility_rate',yml_config['vector_simility_rate'])

    with open('./config.yml',encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)


        
        command_similarity_rate = data['command_similarity_rate']
        vector_similarity_rate = data['vector_similarity_rate']

        text_vec_model_path = data['text_vec_model_path']

        STATEMENT_TEXT_MAX_LENGTH = data['STATEMENT_TEXT_MAX_LENGTH']
        CONVERSATION_LABEL_MAX_LENGTH = data['CONVERSATION_LABEL_MAX_LENGTH']
        PERSONA_MAX_LENGTH = data['PERSONA_MAX_LENGTH']
        TAG_NAME_MAX_LENGTH = data['TAG_NAME_MAX_LENGTH']
        TAG_TYPE_MAX_LENGTH = data['TAG_NAME_MAX_LENGTH']

        STOP_WORDS_PATH = data['stop_words_path']