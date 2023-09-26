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