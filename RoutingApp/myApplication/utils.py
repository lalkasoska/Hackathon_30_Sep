import requests
API_KEY = 'UlkIw3PWQX7URU5fPZz4LhlGqYQTdSRrcdc8TZ-XeaA'
def get_time_from_a_to_b(origin,destination):
    if origin == destination:
        return 0
    #origin = '56.00328817561712,92.93167856127904'  # торговый центр
    #destination = '56.01252091368041,92.97425058276238'  # сибгу
    mode = "car"  # bicycle, bus, car, pedestrian, scooter, taxi, or truck
    url = f'https://router.hereapi.com/v8/routes?transportMode={mode}&origin={origin}&destination={destination}&return=summary&apikey={API_KEY}'
    res = -1
    while res < 0:
        response = requests.get(url)
        data = response.json()
        if 'action' not in data:
            res = data['routes'][0]['sections'][0]['summary']['duration']  # секунд
        else:
            print(response)
    return res # seconds

if __name__ == "__main__":
    print(get_time_from_a_to_b('56.00328817561712,92.93167856127904','56.01252091368041,92.97425058276238'))