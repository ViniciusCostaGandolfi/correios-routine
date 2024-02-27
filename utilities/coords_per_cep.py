import brazilcep
from geopy.geocoders import Nominatim

# R. Dragão do Mar, 81 - Praia de Iracema, Fortaleza - CE, 60060-390
def get_coords_per_cep(cep: str):
    address = brazilcep.get_address_from_cep(cep)
    geolocator = Nominatim(user_agent="test_app")
    location = geolocator.geocode(f"{address['street']} - {address['district']}, {address['city']} - {address['uf']}, {address['cep']}")

    return [location.latitude, location.longitude]