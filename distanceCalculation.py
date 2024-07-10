
'''
This file will retrieve distances that will make up the distance matrix, which helps calculate a total travel distance
for all Big East teams throughout the course of their conference seasons.
'''

import requests
import numpy as np
import pandas as pd
import re
import json

#list of school names
schools = ['Butler', 'UConn', 'Creighton', 'DePaul', 'Georgetown', 'Marquette', 'Providence', 'St. Johns', 'Seton Hall', 'Villanova', 'Xavier']

#arena addresses
addresses = ['510 W 49th St, Indianapolis, IN 46208','2098 Hillside Rd, Storrs, CT 06268','455 N 10th St, Omaha, NE 68102','200 East Cermak Road, Chicago, IL 60616','1340 West Rd, Washington, DC 20057','770 N 12th St, Milwaukee, WI 53233','1 La Salle Square, Providence, RI 02903','4 Pennsylvania Plaza, New York, NY 10001','25 Lafayette Street, Newark, NJ 07102','800 E Lancaster Ave, Villanova, PA 19085','1624 Herald Ave, Cincinnati, OH 45207']

#google distance matrix api key
google_key = 'AIzaSyCZ5C3CHIT7eEWvf0NUqJ9fVD0gq6sfiQI'

#create string to use for destinations in api call
destinations = '%7C'.join([re.sub('( |, )', '+', i) for i in addresses])

#loop over each address 
masterDistances = []
for address in addresses:
	tempDistances = []
	tempOrigin = re.sub('( |, )', '+', address)
	tempData = requests.get(f'https://maps.googleapis.com/maps/api/distancematrix/json?origins={tempOrigin}&destinations={destinations}&key={google_key}')
	parsedData = json.loads(tempData.text)
	
	#loop through parsed results to get all distances to append to row
	for j in range(len(addresses)):
		tempDistances.append(parsedData['rows'][0]['elements'][j]['distance']['value'])
	
	masterDistances.append(tempDistances)

#save out distance matrix to .csv file to use for heuristics code	
masterDistances = pd.DataFrame(masterDistances, columns=schools, index=schools)
masterDistances.to_csv('distance matrix.csv')

