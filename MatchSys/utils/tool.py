import requests

# def get_weather_abstract_by_hefeng(address):
#     get_location_url = 'https://geoapi.qweather.com/v2/city/lookup'
#     get_loction_params = {
#         'key': config.SERVICE_CONFIG.he_feng_key,
#         'location': address
#     }
#     location_data = requests.get(get_location_url,get_loction_params).json()['location'][0]
#     page = requests.get(location_data['fxLink'])
#     soup = BeautifulSoup(page.text, 'html.parser')
#     abstract = soup.find_all('div', class_='current-abstract')[0]
#     return abstract.text.strip() + '\n 详细信息：'+location_data['fxLink']





def get_ghs_picture(tags=[]):

    if len(tags) > 0:
        params = {
                        'r18':0,
                        'num': 1,
                        'tag': tags
                }
        response = requests.get('https://api.lolicon.app/setu/v2', params=params).json()['data'][0]['urls']['original']
        return response
