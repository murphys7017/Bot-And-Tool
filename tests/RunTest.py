import sys
sys.path.append(r"C:\Users\Administrator\Documents\GitHub\QQ-Bot-And-Tool") 
from MatchSys import config


from MatchSys import MatchSys
ms = MatchSys(
        name='teat_sys',
        ltp_model_path=r'C:\Users\Administrator\Documents\GitHub\QQ-Bot-And-Tool\data\LtpModel',
        database_uri='sqlite:///data/db.sqlite3',
        text_vec_model_path=r'C:\Users\Administrator\Documents\GitHub\QQ-Bot-And-Tool\data\model.pkl',
        vector_similarity_rate=0.7,
        most_similar_number=10,
        vector_match_times=5,

    )

@ms.handle_function_declaration(commands = ['天气怎么样'])
def get_weather_abstract_by_hefeng(input_statement):
    import requests
    from bs4 import BeautifulSoup
    get_location_url = 'https://geoapi.qweather.com/v2/city/lookup'
    address = input_statement.text.split('天气怎么样')[0]
    get_loction_params = {
        'key': config,
        'location': address
    }
    location_data = requests.get(get_location_url,get_loction_params).json()
    print(location_data)
    location_data = location_data['location'][0]
    page = requests.get(location_data['fxLink'])
    soup = BeautifulSoup(page.text, 'html.parser')
    abstract = soup.find_all('div', class_='current-abstract')[0]
    return abstract.text.strip() + '\n 详细信息：'+location_data['fxLink']

while True:
    message = input('>')
    if message == 'exit':
        break
    else:
        print(ms.get_response(message))