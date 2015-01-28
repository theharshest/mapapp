This is a Flask app. It highlights the cities which cross the line joining start and end address or the cities which cross the driving path if driving direction option is set. It works only for United States.

Instructions:

1) Copy datafiles cb_2013_us_zcta510_500k.shp and cb_2013_us_zcta510_500k.shx in cities_pickle directory. Files can be downloaded from https://www.census.gov/geo/maps-data/data/cbf/cbf_zcta.html
2) Run cities_pickle.py in cities_pickle directory to generate cities.pickle file.
3) Copy cities.pickle to app root directory
4) Start the app by running mapapp.py