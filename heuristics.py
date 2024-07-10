


import pandas as pd
from collections import Counter
import numpy as np
import time
import warnings
from columnar import columnar
from copy import deepcopy
from datetime import datetime

warnings.filterwarnings('ignore')


''' Parameters for tabu search '''
iterations = 1000
k = 5


school_indices = [0,1,2,3,4,5,6,7,8,9,10]
school_names = ['Butler', 'UConn', 'Creighton', 'DePaul', 'Georgetown', 'Marquette', 'Providence', 'St. Johns', 'Seton Hall', 'Villanova', 'Xavier']
slot_indices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

#distance matrix (convert to miles)
distances = pd.read_csv('distance_matrix.csv', usecols=school_names).values.tolist()
distances = (np.array(distances)/1609.344).tolist()

#initial/actual solution: opponents
opponents_initial = [[4,6,99,99,7,1,5,8,10,3,4,9,99,2,1,6,5,2,9,8,7,3,10,99],
		    [8,7,99,99,3,0,10,4,2,9,99,10,6,7,0,4,3,5,2,9,99,8,5,6],
		    [9,99,99,5,4,6,3,7,1,8,10,3,99,0,6,10,4,0,1,7,8,5,99,9],
		    [99,9,99,99,1,4,2,9,6,0,5,2,8,10,7,99,1,6,5,4,10,0,7,8],
		    [0,5,99,99,2,3,8,1,99,10,0,6,99,5,8,1,2,9,7,3,9,10,6,7],
		    [6,4,99,2,99,8,0,99,9,7,3,8,9,4,99,7,0,1,3,10,6,2,1,10],
		    [5,0,99,99,8,2,7,10,3,99,8,4,1,9,2,0,7,3,10,99,5,9,4,1],
		    [10,1,99,99,0,9,6,2,8,5,9,99,10,1,3,5,6,8,4,2,0,99,3,4],
		    [1,10,99,99,6,5,4,0,7,2,6,5,3,99,4,9,10,7,99,0,2,1,9,3],
		    [2,3,99,99,10,7,99,3,5,1,7,0,5,6,10,8,99,4,0,1,4,6,8,2],
		    [7,8,99,99,9,99,1,6,0,4,2,1,7,3,9,2,8,99,6,5,3,4,0,5]]

#initial/actual solution: venues
venues_initial = [[0,1,-1,-1,1,0,1,0,1,0,1,0,-1,1,1,0,0,0,1,1,0,1,0,-1],
		 [1,0,-1,-1,0,1,1,0,0,1,-1,0,0,1,0,1,1,0,1,0,-1,0,1,1],
		 [0,-1,-1,1,1,0,1,0,1,1,0,0,-1,0,1,1,0,1,0,1,0,0,-1,1],
		 [-1,0,-1,-1,1,1,0,1,0,1,0,1,0,0,1,-1,0,1,1,0,1,0,0,1],
		 [1,1,-1,-1,0,0,0,1,-1,1,0,1,-1,0,1,0,1,0,0,1,1,0,0,1],
		 [1,0,-1,0,-1,1,0,-1,0,1,1,0,1,1,-1,0,1,1,0,0,0,1,0,1],
		 [0,0,-1,-1,0,1,1,0,1,-1,1,0,1,1,0,1,0,0,1,-1,1,0,1,0],
		 [0,1,-1,-1,0,1,0,1,1,0,0,-1,1,0,0,1,1,0,1,0,1,-1,1,0],
		 [0,1,-1,-1,1,0,1,1,0,0,0,1,1,-1,0,1,0,1,-1,0,1,1,0,0],
		 [1,1,-1,-1,0,0,-1,0,1,0,1,1,0,0,1,0,-1,1,0,1,0,1,1,0],
		 [1,0,-1,-1,1,-1,0,1,0,0,1,1,0,1,0,0,1,-1,0,1,0,1,1,0]]



#create function that determines total travel distance
def getDistance(distances, opponents, venues):

	#to hold 11 school travel distances
	masterDistances = []

	for i in school_indices:

		teamDistance = 0
		
		#Loop through remaining weeks. Check for certain home/away/bye patterns to determine additional distances.
		for j in slot_indices:
			
			#Initial travel distance, if applicable
			if j==0:
				currentOpp = i if opponents[i][j]==99 else opponents[i][j]
				currentVenue = 0 if venues[i][j]==-1 else venues[i][j]
				if venues[i][j]==1:
					teamDistance = teamDistance + distances[i][currentOpp]
					continue
			

			#Travel distances, weeks 1-23
			if j>0:
				currentOpp = i if opponents[i][j]==99 else opponents[i][j]
				currentVenue = 0 if venues[i][j]==-1 else venues[i][j]
			
				priorOpp = i if opponents[i][j-1]==99 else opponents[i][j-1]
				priorVenue = 0 if venues[i][j-1]==-1 else venues[i][j-1]

				if priorVenue==1 and currentVenue==0:
					teamDistance = teamDistance + distances[priorOpp][i]
				
				if priorVenue==0 and currentVenue==1:
					teamDistance = teamDistance + distances[i][currentOpp]
			
				if priorVenue==1 and currentVenue==1:
					teamDistance = teamDistance + distances[priorOpp][currentOpp]
			

			#Final return distance, if applicable
			if j==23:
				currentOpp = i if opponents[i][j]==99 else opponents[i][j]
				currentVenue = 0 if venues[i][j]==-1 else venues[i][j]
				if venues[i][j]==1:
					teamDistance = teamDistance + distances[currentOpp][i]
				
		masterDistances.append(teamDistance)
	
	totalDistance = sum(masterDistances)
	return totalDistance



'''
Performs a home-away swap for two teams. 

Ex. Team A plays team B on the road during week 3 and at home during week 10. 
A venue swap will now have team A playing team B at home during week 3 and on
the road during week 10.
'''
venueSwapHistory = []
def venueSwap(opponents, venues):
	
	#randomly select distinct teams
	team_A, team_B = np.random.choice(school_indices, size=2, replace=False)
	venueSwapHistory.append(['venue', team_A, team_B])

	#determine slots when team A and B play each other
	faceoffWeeks = [i for i, x in enumerate((opponents[team_A]==team_B).tolist()) if x]
	
	#update venues for both teams
	for i in faceoffWeeks:
		venues[team_A][i] = 1-venues[team_A][i]
		venues[team_B][i] = 1-venues[team_B][i]

	
	return opponents, venues





'''
Performs a swap between two different rounds.

Ex. Swapping rounds 2 and 6 will move round 6 games to round 2, and vice versa.
'''
roundSwapHistory = []
def roundSwap(opponents, venues):
	round_A, round_B = np.random.choice([0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], size=2, replace=False)
	roundSwapHistory.append(['round',round_A, round_B])

	tempOpponents = np.array(opponents).T.tolist()
	tempVenues = np.array(venues).T.tolist()

	tempOpponents[round_A], tempOpponents[round_B] = tempOpponents[round_B], tempOpponents[round_A]
	tempVenues[round_A], tempVenues[round_B] = tempVenues[round_B], tempVenues[round_A]

	return np.array(tempOpponents).T.T.T.tolist(), np.array(tempVenues).T.T.T.tolist()




'''
Neighborhood search organizer. Will randomly pick between 1 of 2 available swapping methods.
'''
def neighborSearch(opponents, venues):
	if np.random.random() < 0.5:
		firstOpponents, firstVenues = venueSwap(deepcopy(opponents), deepcopy(venues))
		return roundSwap(deepcopy(firstOpponents), deepcopy(firstVenues))
	else:
		firstOpponents, firstVenues = roundSwap(deepcopy(opponents), deepcopy(venues))
		return venueSwap(deepcopy(firstOpponents), deepcopy(firstVenues))




'''
Checks for feasibility of current solution. Returns True unless any checks are 
violated, in which case it'll return false.
'''
def confirmFeasibility(opponents, venues):
	
	#Constraint 1: cannot match two teams up in consecutive games
	for i in school_indices:
		for j in range(0,18):
			if list(filter((99).__ne__,opponents[i]))[j]==list(filter((99).__ne__,opponents[i]))[j+1]:
				#print("Infeasible: two teams facing each other in consecutive games.")
				return False
	
	
	
	#Constraint 2: homestand/roadtrip can not exceed 3 games
	for i in school_indices:
		
		#Initialize list to hold consecutive equal venues
		currentTrip = []
		
		#Loop through games
		for j in range(0,23):
			
			#Reset list if bye week
			if venues[i][j] == -1:
				currentTrip.clear()
				continue
				
			
			#If current venue equal to last venue, append to list of venues. Then check to see if length is >3, if so, return False
			if venues[i][j] == (currentTrip or [None])[-1]:
				currentTrip.append(venues[i][j])
				
				if len(currentTrip) > 3:
					#print("Infeasible: homestand/roadtrip exceeds 3 games.")
					return False
				

			#If current venue is different than last venue, reset currentTrip list.
			if venues[i][j] != (currentTrip or [None])[-1]:
				currentTrip.clear()
				currentTrip.append(venues[i][j])
				continue
			
			
	

	#Constraint 3: slot 2 should be all byes
	for i in school_indices:
		if opponents[i][2] != 99:
			#print("Infeasible: team(s) assigned to 2nd slot.") 
			return False
	

	#Constraint 4: 4 byes total per team. Assume True until proven otherwise.
	for i in school_indices:
		if opponents[i].count(99) != 4:
			#print("Infeasible: team(s) schedule doesn't contain exactly 4 byes.")
			return False

	
	#Constraint 5: DRR tournament format. Confirm each team plays every other team twice
	for i in school_indices:
		if list(Counter(list(filter((99).__ne__,opponents[i]))).values()) != [2]*10:
			#print("Infeasible: team(s) not playing every other team(s) exactly twice.")
			return False
	
	
	#Constraint 6: Each team plays only once per slot.
	for slot in np.array(opponents).T.tolist():
		if any(x in list(Counter(list(filter((99).__ne__,slot))).values()) for x in [2,3,4,5,6,7,8,9,10,11]):
			#print("Infeasible: team(s) scheduled against more than one team for given week.")
			return False
	

	#If team i plays team j on the road during round r, team j plays team i at home during round r
	for i in school_indices:
		for j in slot_indices:
			opp = opponents[i][j]
			ven = venues[i][j]
			if opp == 99:
				break
			else:
				if i != opponents[opp][j]:
					#print("Infeasible: new schedule does not contain two teams playing each other for at least one round.")
					return False
				if sorted([venues[opp][j], ven]) != [0,1]:
					#print("Infeasible: new schedule does not contain home/away pattern for at least one round.")
					return False
					

	
	#If passes all constraints, return True
	return True



#Define and set best (initial) distance, opponents, venues
bestDistance = getDistance(distances, opponents_initial, venues_initial)
bestOpponents, bestVenues = opponents_initial, venues_initial
print(bestDistance)


#Define tabu to hold feasible solutions
tabu = []
tabu.append([bestDistance, bestOpponents, bestVenues])


bestUpdatedCount = 0
numFeasibleSolutions = 0

cpu_start = time.process_time()
real_start = time.time()

#Loop over each iteration to run a local neighborhood search
count=0
while count < iterations:

	#Get new distances, opponents, venues from neighborhood search on most recent tabu entry
	tempOpponents, tempVenues = neighborSearch(deepcopy(tabu[-1][1]), deepcopy(tabu[-1][2]))	
	tempDistance = getDistance(distances, tempOpponents, tempVenues)

	'''
	If new solution is feasible and doesn't already exist in tabu, proceed to add to tabu.
	'''	
	if (confirmFeasibility(tempOpponents, tempVenues) is True) and ([tempDistance, tempOpponents, tempVenues] not in tabu):
		numFeasibleSolutions = numFeasibleSolutions + 1
		
		#Append new solution to tabu
		tabu.append([tempDistance, tempOpponents, tempVenues])

		#Update best objective/solution if current is better than best
		if tempDistance < bestDistance:
			bestUpdatedCount = bestUpdatedCount + 1
			bestDistance = tempDistance
			bestOpponents = tempOpponents
			bestVenues = tempVenues

		#Remove oldest tabu entry (if tabu is long enough)
		if len(tabu) > k:
			tabu.pop(0)
	
	count = count + 1

#for heuristic time measurements
cpu_total = (time.process_time() - cpu_start)
real_total = (time.time() - real_start)


#loop through best solution and save to CSV
masterSched = []
for i in school_indices:
	teamSched = []
	for j in slot_indices:
		if bestVenues[i][j] == -1:
			teamSched.append("--BYE--")
		if bestVenues[i][j] == 0:
			teamSched.append(school_names[bestOpponents[i][j]])
		if bestVenues[i][j] == 1:
			teamSched.append(f"@{school_names[bestOpponents[i][j]]}")
	masterSched.append(teamSched)

masterSched = pd.DataFrame(masterSched, columns=slot_indices, index=school_names)
masterSched.to_csv('OptimalBESchedule.csv')
	

#save other useful model pieces to txt file
f = open("scheduling_tabu_info.txt", "w")
f.write(f"Tabu search creation date: {datetime.now()}\n\n")
f.write(f"Final optimal Big East basketball schedule saved into 'OptimalBESchedule.csv'. Minimized total conference travel distance: {bestDistance} miles.\n")
f.write(f"Total iterations: {iterations}\n")
f.write(f"Total heuristic runtime: {cpu_total} sec (CPU), {real_total} sec (actual)\n")
f.write(f"Total feasible solutions: {numFeasibleSolutions}\n")
f.write(f"Total times best solution was updated: {bestUpdatedCount}\n\n")
f.write("Swap history...\n")
for iter in range(iterations):
	f.write(f"Iteration {iter+1}: swapped home/away between {venueSwapHistory[iter][1]} & {venueSwapHistory[iter][2]}, swapped rounds {roundSwapHistory[iter][1]} & {roundSwapHistory[iter][2]}\n")


#print command line output
print(f"\n\nFinal optimal Big East basketball schedule saved into 'OptimalBESchedule.csv'. Minimized total conference travel distance: {round(bestDistance,3)} miles.\n\n")
print(f"\tTotal iterations: {iterations}")
print(f"\tTotal heuristic runtime: {round(cpu_total,3)} sec (CPU), {round(real_total,3)} sec (actual)")
print(f"\tTabu length: {k}")
print(f"\tTotal feasible solutions: {numFeasibleSolutions}")
print(f"\tTotal times best solution was updated: {bestUpdatedCount}\n")
print(f"**This information, along with neighborhood swaps for all {iterations} iterations, can be found in 'scheduling_tabu_info.txt'**\n\n")

