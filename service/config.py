import yaml



class ServiceConfig(object):
    bot_name = None
    data_path = './data/'
    go_cqhttp_http = None
    go_cqhttp_websocket = None
    parrot_model_path = './data/ParrotModel/'

    he_feng_key = None

    activate_rasa = True
    rasa_url = 'http://localhost:5005/webhooks/rest/webhook'

    if_start_rasa=True
    command_similarity_rate=0.8
    parrot_similarity_rate=0.92

global SERVICE_CONFIG
SERVICE_CONFIG = ServiceConfig()

def init():
    with open('./config.yml',encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

        SERVICE_CONFIG.bot_name = data['assistant_id']

        if data['go_cqhttp_http'].endswith('/'):
            SERVICE_CONFIG.go_cqhttp_http = data['go_cqhttp_http']
        else:
            SERVICE_CONFIG.go_cqhttp_http = data['go_cqhttp_http'] + '/'

        if data['go_cqhttp_websocket'].endswith('/'):
            SERVICE_CONFIG.go_cqhttp_websocket = data['go_cqhttp_websocket']
        else:
            SERVICE_CONFIG.go_cqhttp_websocket = data['go_cqhttp_websocket'] + '/'
        
        if 'he_feng_key' in data:
            SERVICE_CONFIG.he_feng_key = data['he_feng_key']
        

        SERVICE_CONFIG.if_start_rasa = data['if_start_rasa']
        SERVICE_CONFIG.command_similarity_rate = data['command_similarity_rate']
        SERVICE_CONFIG.parrot_similarity_rate = data['parrot_similarity_rate']
        print(SERVICE_CONFIG.if_start_rasa)

def initialize():
    global bot_name
    global data_path
    global go_cqhttp_http
    global go_cqhttp_websocket
    global parrot_model_path

    global he_feng_key

    global activate_rasa
    global rasa_url

    global if_start_rasa
    global command_similarity_rate
    global parrot_similarity_rate
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

    rasa_url = 'http://localhost:5005/webhooks/rest/webhook'

    if_start_rasa=True
    command_similarity_rate=0.8
    parrot_similarity_rate=0.92
    with open('./config.yml',encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

        bot_name = data['assistant_id']

        if data['go_cqhttp_http'].endswith('/'):
            go_cqhttp_http = data['go_cqhttp_http']
        else:
            go_cqhttp_http = data['go_cqhttp_http'] + '/'

        if data['go_cqhttp_websocket'].endswith('/'):
            go_cqhttp_websocket = data['go_cqhttp_websocket']
        else:
            go_cqhttp_websocket = data['go_cqhttp_websocket'] + '/'
        
        if 'he_feng_key' in data:
            he_feng_key = data['he_feng_key']
        

        if_start_rasa = data['if_start_rasa']
        command_similarity_rate = data['command_similarity_rate']
        parrot_similarity_rate = data['parrot_similarity_rate']

        text_vec_model_path = data['text_vec_model_path']

        STATEMENT_TEXT_MAX_LENGTH = data['STATEMENT_TEXT_MAX_LENGTH']
        CONVERSATION_LABEL_MAX_LENGTH = data['CONVERSATION_LABEL_MAX_LENGTH']
        PERSONA_MAX_LENGTH = data['PERSONA_MAX_LENGTH']
        TAG_NAME_MAX_LENGTH = data['TAG_NAME_MAX_LENGTH']
        TAG_TYPE_MAX_LENGTH = data['TAG_NAME_MAX_LENGTH']

        STOP_WORDS_PATH = data['stop_words_path']