from flask import Flask, render_template, request, make_response
from shapely.geometry import shape, LineString, Point
from descartes import PolygonPatch
import fiona, pylab
from pygeocoder import Geocoder
import pickle
import StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from googlemaps import Client
import sys

app = Flask(__name__)

def get_map_image(start_location, end_location, directions):
	'''
	Generates map using shapefile and address locations
	'''

	# Line(s) connecting the two locations or driving path
	lines = []

	# Minimum and maximum longitude and latitude values 
	minlon = sys.maxint
	minlat = sys.maxint
	maxlat = -sys.maxint - 1

	if directions:
		# Get line for each step
		for step in directions:
			start_lon = step[0][0]
			start_lat = step[0][1]
			end_lon = step[1][0]
			end_lat = step[1][1]
			line = LineString([(start_lon, start_lat), (end_lon, end_lat)])
			lines.append(line)
			minlon = min(minlon, start_lon, end_lon)
			minlat = min(minlat, start_lat, end_lat)
			maxlat = max(maxlat, start_lat, end_lon)
	else:
		start_lat, start_lon = start_location[0].coordinates
		end_lat, end_lon = end_location[0].coordinates
		minlon = min(float(start_lon), float(end_lon))
		minlat = min(float(start_lat), float(end_lat))
		maxlat = max(float(start_lat), float(end_lat))
		line = LineString([(start_lon, start_lat), (end_lon, end_lat)])
		lines.append(line)

	# Get list of cities geometry extacted from shapefile
	city_pickle = open('cities.pickle')
	cities = pickle.load(city_pickle)
	city_pickle.close()

	# Initialize Pylab figure
	pylab.axis('equal')
	fig = pylab.figure(figsize=(200, 100), dpi=50, facecolor="white")

	# Draw all the cities that intersect with lines
	for city in cities:
		city = [city]

		for poly in city:
			for line in lines:
				if line.intersects(poly):
					try:
						poly_patch = PolygonPatch(poly, fc="#0000AA", \
							ec="#0000DD", alpha=0.5)
						fig.gca().add_patch(poly_patch)
					except:
						pass

	# Draw the connecting lines
	for line in lines:
		fig.gca().plot(*line.xy, color='#FF0000')

	# Keeping a pad of 0.1
	minlon -= 0.1
	minlat -= 0.1
	maxlat += 0.1

	# Maintain aspect ratio to avoid distorted images
	maxlon = 2.4*(maxlat-minlat) + minlon

	fig.gca().axis([minlon, maxlon, minlat, maxlat])
	fig.gca().axis('off')

	# Preparing image response
	canvas = FigureCanvas(fig)
	output = StringIO.StringIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

def coordinates((start_address, end_address)):
	'''
	Calculates coordinates from start and destination addresses
	'''
	try:
		start_location = Geocoder.geocode(start_address)
		end_location = Geocoder.geocode(end_address)
	except:
		start_location = False
		end_location = False

	return start_location, end_location

def get_driving_directions(start_address, end_address, api_key):
	'''
	Get driving direction steps from start and destination address
	'''
	result = []
	gmaps = Client(api_key)
	directions = gmaps.directions(start_address, end_address)
	for step in directions[0]['legs'][0]['steps']:
		start = step['start_location']
		end = step['end_location']
		direction = [(start['lng'], start['lat']), (end['lng'], end['lat'])]
		result.append(direction)

	return result

@app.route('/', methods=['GET', 'POST'])
def input():
	error = None

	if request.method == 'POST':
		# Get all input values
		start_address = request.form['start_address']
		end_address = request.form['end_address']
		api_key = request.form['api_key']
		start_location, end_location = coordinates((start_address, end_address))

		driving = True if len(request.form.getlist('driving_dir'))>0 else False

		if start_location == False or end_location == False:
			error = "One (or both) of the addresses are invalid."
		elif len(start_location)>1 and len(end_location)>1:
			error = "Both the addresses are ambiguous, please enter more \
			precise addresses."
		elif len(start_location)>1:
			error = "Start error is ambiguous, please enter a more precise \
			address."
		elif len(end_location)>1:
			error = "End error is ambiguous, please enter a more precise \
			address."
		elif driving and not api_key:
			error = "Please enter Google Directions API key."

		try:
			directions = get_driving_directions(start_address, end_address, \
				api_key) if api_key else None
		except:
			error = "Invalid API key."

		if not error:
			return get_map_image(start_location, end_location, directions)
			
	return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)