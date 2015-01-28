import pickle
import fiona
from shapely.geometry import shape

with fiona.collection("cb_2013_us_zcta510_500k.shp") as features:
    cities = [shape(f['geometry']) for f in features]

cities_pickle = open('cities.pickle', 'wb')
pickle.dump(cities, cities_pickle)
cities_pickle.close()