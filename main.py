import csv
import requests
import math
from abc import ABC, abstractmethod

# Método para leer el archivo CSV y obtener las coordenadas
class CSVService:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.cities = self.load_csv()
        
    def load_csv(self):
        cities = {}
        with open(self.csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                city = row['city'].lower()
                country = row['country'].lower()
                key = f"{city},{country}"
                cities[key] = (float(row['lat']), float(row['lng']))
        return cities
    
    def get_coordinates(self, city, country):
        key = f"{city.lower()},{country.lower()}"
        return self.cities.get(key, None)

# Método para obtener las coordenadas usando la API de Nominatim
class APIService:
    def get_coordinates(self, city, country):
        url = f"https://nominatim.openstreetmap.org/search?q={city},{country}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return (float(data[0]['lat']), float(data[0]['lon']))
        return None

# Método Mock que devuelve valores fijos
class MockService:
    def get_coordinates(self, city, country):
        return (0.0, 0.0)  # Coordenadas fijas de ejemplo

# Interfaz para cambiar entre diferentes servicios
class CoordinateService(ABC):
    @abstractmethod
    def get_coordinates(self, city, country):
        pass

class CityCoordinateService(CoordinateService):
    def __init__(self, method):
        self.method = method
        
    def get_coordinates(self, city, country):
        return self.method.get_coordinates(city, country)

# Método para calcular la distancia entre dos coordenadas usando la fórmula de Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

# Función principal para obtener la distancia entre dos ciudades
def main():
    csv_service = CSVService('worldcities.csv')
    api_service = APIService()
    mock_service = MockService()

    city_service_csv = CityCoordinateService(csv_service)
    city_service_api = CityCoordinateService(api_service)
    city_service_mock = CityCoordinateService(mock_service)

    city1 = "Chicago"
    country1 = "United States"
    city2 = "Santiago"
    country2 = "Chile"

    # Usando CSV
    lat_lon1_csv = city_service_csv.get_coordinates(city1, country1)
    lat_lon2_csv = city_service_csv.get_coordinates(city2, country2)

    if lat_lon1_csv and lat_lon2_csv:
        distance_csv = haversine(lat_lon1_csv[0], lat_lon1_csv[1], lat_lon2_csv[0], lat_lon2_csv[1])
        print(f"(CSV) Distancia entre {city1}, {country1} y {city2}, {country2} es: {distance_csv} km")
    else:
        print("(CSV) No se pudo obtener las coordenadas de alguna de las ciudades.")

    # Usando API
    lat_lon1_api = city_service_api.get_coordinates(city1, country1)
    lat_lon2_api = city_service_api.get_coordinates(city2, country2)

    if lat_lon1_api and lat_lon2_api:
        distance_api = haversine(lat_lon1_api[0], lat_lon1_api[1], lat_lon2_api[0], lat_lon2_api[1])
        print(f"(API) Distancia entre {city1}, {country1} y {city2}, {country2} es: {distance_api} km")
    else:
        print("(API) No se pudo obtener las coordenadas de alguna de las ciudades.")

if __name__ == "__main__":
    main()
