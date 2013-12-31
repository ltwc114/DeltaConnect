import os, sys, re, mmap, numpy as np
from datetime import datetime

flightNumberPattern = re.compile('Flight#\s\d{4}\s\(\s\w{3}\s-\s\w{3}\)') 
revPattern = re.compile('REV = &nbsp;\d*')
nonRevPattern = re.compile('NONREV = &nbsp;\d*')
firstBusinessPattern = re.compile('FIRST/BUSINESS = &nbsp;\d*')
coachPattern = re.compile('COACH = &nbsp;\d*')
timeStampPattern = re.compile('\d{2}-\d{2}-\d{2}')


prioritiesDict = {}

prioritiesDict["S1A"] = 1
prioritiesDict["S2"] = 2
prioritiesDict["S3"] = 3
prioritiesDict["S3B"] = 4
prioritiesDict["S3C"] = 5
prioritiesDict["S4"] = 6



def to24(hour12, isPm):
    return (hour12 % 12) + (12 if isPm else 0)

def prioritiesOrder(standbyCode1, standbyCode2):

		if (prioritiesDict[standbyCode1] < prioritiesDict[standbyCode2]):
			return 1
		elif (prioritiesDict[standbyCode1] > prioritiesDict[standbyCode2]):
			return 0
		else:
			return -1

#f = open('allFlights.txt')
#g = open('mainFlightPage.txt')

f = open(sys.argv[1])
g = open(sys.argv[2])

timePattern = re.compile('>\d{2}:\d{2}(?:AM|PM)')
iataPattern = re.compile('<td>[A-Z]{3}</td>')
fnPattern = re.compile('>\d{4}<')

data = mmap.mmap(g.fileno(), 0, prot=mmap.PROT_READ)
times = timePattern.findall(data)
iata = iataPattern.findall(data)
fn = fnPattern.findall(data)

newIata = []
newTimes = []

for i in iata:
	if (i != '<td>CRJ</td>'):
		newIata.append(i)


departTimeForFN = {}
arriveTimeForFN = {}

finalFlightDict = {}

finalSortedProbFlights = []
finalProbFlights = []

fnIndex = 0

#print len(newIata)
#print len(times)

for i in range (0, len(newIata), 2):
		
		if (i < len(times)):
			newTimes.append(times[i])
			newTimes.append(times[i+1])
			
			flightNum = fn[fnIndex][1:5]

			departTimeForFN[flightNum] = times[i][1:]

			arriveTimeForFN[flightNum] = times[i+1][1:]

		fnIndex += 1

myStandbyCode = sys.argv[3]
myTimeStamp = sys.argv[4]
leaveTimeAndDate = sys.argv[5]
#myStandbyCode = "S2"
#myTimeStamp = "02-10-10"

myDateStamp = datetime.strptime(myTimeStamp, "%m-%d-%y")

timeIndex = 0

finalFlights = []

for line in f:

 	if len(flightNumberPattern.findall(line)) > 1:

		flight =  flightNumberPattern.findall(line)[0:len(flightNumberPattern.findall(line)) / 2]
		flightHeader = []
		flightNumPositions = []
		standbySearchString = ""

		for fn in flight:
			flightHeader.append(fn)
			airportList = "airportList" + fn[8:12]		#fn[8:12] is the 4 digit flight number
			flightNumPositions.append(airportList)

		flightsProbs = []
		fbProbs = []

		flightNumsInLeg = []
	
		count = 0

		for i in range(len(flightNumPositions)):
			
			standbysAheadOfYou = 0

			if (i != len(flightNumPositions) - 1):
				##print("Flight pos: ", flightNumPositions[i], " index: ", line.index(flightNumPositions[i]))
				firstSearch =  line.index(flightNumPositions[i])
				secondSearch =  line.index(flightNumPositions[i+1])
				standbySearchString = line[firstSearch:secondSearch]
				hkCount = standbySearchString.count(">HK")
				upCount = standbySearchString.count(">UP")
				psupCount = standbySearchString.count(">PSUP")
				s1aCount = standbySearchString.count(">S1A")
				s2Count = standbySearchString.count(">S2")
				s3Count = standbySearchString.count(">S3<")
				s3bCount = standbySearchString.count(">S3B<")
				s3cCount = standbySearchString.count(">S3C<")
				s4Count = standbySearchString.count(">S4")
				timeStampList = timeStampPattern.findall(standbySearchString)

				#print(flightHeader[i], "HK: ", hkCount, " UP: ", upCount, " PSUP: ", psupCount, " S1A: ", s1aCount, " S2: ", s2Count, " S3: ", s3Count, " S3B: ", s3bCount, " S3C: ", s3cCount, " S4: ", s4Count)


				for j in range(0, psupCount):
					psup = timeStampList.pop(0)
					#print ("PSUP: ", psup) 
					if (myStandbyCode is "PSUP"):
						nonRevDateStamp = datetime.strptime(psup, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 

				for j in range(0, s1aCount):
					s1a = timeStampList.pop(0)
					#print ("S1A: ", s1a)
					#print ("Priorities order", prioritiesOrder("S1A", myStandbyCode))
					if ( (prioritiesOrder("S1A", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s1a, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S1A", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s1a, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 

				for j in range(0, s2Count):
					s2 = timeStampList.pop(0)
					#print ("S2: ", s2)
					#print ("Priorities order", prioritiesOrder("S2", myStandbyCode))
					if ( (prioritiesOrder("S2", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s2, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S2", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s2, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
				
				for j in range(0, s3Count):
					s3 = timeStampList.pop(0)
					#print ("S3: ", s3)
					#print ("Priorities order", prioritiesOrder("S3", myStandbyCode))
					if ( (prioritiesOrder("S3", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s3, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S3", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s3, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s3bCount):
					s3b = timeStampList.pop(0)
					#print ("S3B: ", s3b)
					#print ("Priorities order", prioritiesOrder("S3B", myStandbyCode))
					if ( (prioritiesOrder("S3B", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s3b, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S3B", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s3b, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s3cCount):
					s3c = timeStampList.pop(0)
					#print ("S3C: ", s3c)
					#print ("Priorities order", prioritiesOrder("S3C", myStandbyCode))
					if ( (prioritiesOrder("S3C", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s3c, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S3C", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s3c, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s4Count):
					s4 = timeStampList.pop(0)
					#print ("S4: ", s4)
					#print ("Priorities order", prioritiesOrder("S4", myStandbyCode))
					if ( (prioritiesOrder("S4", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s4, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S4", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s4, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				#print(timeStampList)
			else:
				##print("Single flight pos: ", flightNumPositions[i], " index: ", line.index(flightNumPositions[i]))
				firstSearch =  line.index(flightNumPositions[i])
				standbySearchString = line[firstSearch:]
				hkCount = standbySearchString.count(">HK")
				upCount = standbySearchString.count(">UP")
				psupCount = standbySearchString.count(">PSUP")
				s1aCount = standbySearchString.count(">S1A")
				s2Count = standbySearchString.count(">S2")
				s3Count = standbySearchString.count(">S3<")
				s3bCount = standbySearchString.count(">S3B<")
				s3cCount = standbySearchString.count(">S3C<")
				s4Count = standbySearchString.count(">S4")
				timeStampList = timeStampPattern.findall(standbySearchString)
				#print(flightHeader[i], "HK: ", hkCount, " UP: ", upCount, " PSUP: ", psupCount, " S1A: ", s1aCount, " S2: ", s2Count, " S3: ", s3Count, " S3B: ", s3bCount, " S3C: ", s3cCount, " S4: ", s4Count)


				for j in range(0, psupCount):
					psup = timeStampList.pop(0)
					#print ("PSUP: ", psup) 
					if (myStandbyCode is "PSUP"):
						nonRevDateStamp = datetime.strptime(psup, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 

				for j in range(0, s1aCount):
					s1a = timeStampList.pop(0)
					#print ("S1A: ", s1a)
					#print ("Priorities order", prioritiesOrder("S1A", myStandbyCode))
					if ( (prioritiesOrder("S1A", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s1a, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S1A", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s1a, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s2Count):
					s2 = timeStampList.pop(0)
					#print ("S2: ", s2)
					#print ("Priorities order", prioritiesOrder("S2", myStandbyCode))
					if ( (prioritiesOrder("S2", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s2, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S2", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s2, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s3Count):
					s3 = timeStampList.pop(0)
					#print ("S3: ", s3)
					#print ("Priorities order", prioritiesOrder("S3", myStandbyCode))
					if ( (prioritiesOrder("S3", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s3, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S3", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s3, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s3bCount):
					s3b = timeStampList.pop(0)
					#print ("S3B: ", s3b)
					#print ("Priorities order", prioritiesOrder("S3B", myStandbyCode))
					if ( (prioritiesOrder("S3B", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s3b, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S3B", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s3b, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s3cCount):
					s3c = timeStampList.pop(0)
					#print ("S3C: ", s3c)
					#print ("Priorities order", prioritiesOrder("S3C", myStandbyCode))
					if ( (prioritiesOrder("S3C", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s3c, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S3C", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s3c, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 


				for j in range(0, s4Count):
					s4 = timeStampList.pop(0)
					#print ("S4: ", s4)
					#print ("Priorities order", prioritiesOrder("S4", myStandbyCode))
					if ( (prioritiesOrder("S4", myStandbyCode) == 1 )):
						standbysAheadOfYou += 1
						nonRevDateStamp = datetime.strptime(s4, "%m-%d-%y")
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 
					if ( (prioritiesOrder("S4", myStandbyCode) == -1 )):
						nonRevDateStamp = datetime.strptime(s4, "%m-%d-%y")
						if (myDateStamp > nonRevDateStamp):
							standbysAheadOfYou += 1
						#print ("My date is: ", myTimeStamp, " and it is before?: ", myDateStamp < nonRevDateStamp, " standbysAheadOfYou: ", standbysAheadOfYou) 

	

				#print(timeStampList)

			revList = revPattern.findall(line)[0::2]
			nonRevList = nonRevPattern.findall(line)
			firstBusinessList = firstBusinessPattern.findall(line)
			coachPatternList = coachPattern.findall(line)


			##print("REV: ", int(re.findall('\d+', revList[i])[0]))


			seatsAfterFb = int(re.findall('\d+' , firstBusinessList[i])[0]) - upCount - psupCount

			#print("F/B remaining after UP/PSUP: ", seatsAfterFb)
			##print("F/B: ", int(re.findall('\d+' , firstBusinessList[i])[0]))
			
			digit_re = re.compile('\d+')
			match = digit_re.search(coachPatternList[i])


			seatsAfterHk = 0

			if match:
				seatsAfterHk =  int(re.findall('\d+', coachPatternList[i])[0]) - hkCount
				#print("Coach remaining after HK: ", seatsAfterHk)
				
			
			finalSeatsLeft = seatsAfterHk - standbysAheadOfYou
	
			if (seatsAfterFb > 0):				#Having first class seats open helps you!
				finalSeatsLeft += seatsAfterFb

			#print("All all in all, there are", standbysAheadOfYou , " passengers ahead of you!")
			seatsRemaining = seatsAfterHk - standbysAheadOfYou
			#print("Grand total seats left after all calculations:", seatsRemaining)

			seatProbability = 1337
			fbSeatProbability = 9000

			if (seatsRemaining < 0):
				seatProbability = -1.0 / seatsRemaining
			else :
				seatProbability = 1
	
			if (seatsAfterFb < 0):
				fbSeatProbability = -1.0 / seatsAfterFb
			else:
				fbSeatProbability = 1


			flightN = flightHeader[i][8:12]
			firstDepartTime = flightHeader[0][8:12]
			#print("Depart: ",  departTimeForFN[flightN], "Arrive: ", arriveTimeForFN[flightN], timeIndex)
			#print("Flight # to be mapped: ", flightHeader[i][8:12])

			##print("Probability of making leg:", seatProbability, "Probability of making first class:", fbSeatProbability)

			#print( "---ENDLEG---\n")
			timeIndex += 2

			#finalFlightDict[flightN] = flightHeader[i] + " Probability of making leg->" + str(seatProbability) + " Probability of making first class-> " + str(fbSeatProbability) + " Depart-> " + str(departTimeForFN[flightN]) + " Arrive-> " +  str(arriveTimeForFN[flightN])
			finalFlightDict[flightN] = flightHeader[i] + "," + str(seatProbability) + "," + str(fbSeatProbability) + "," + str(departTimeForFN[flightN]) + "," +  str(arriveTimeForFN[flightN])
			#print finalFlightDict[flightN]

			flightsProbs.append(seatProbability)
			fbProbs.append(fbSeatProbability)
			flightNumsInLeg.append(flightN)
			
		if (count % 2 == 0):
			flightNumsInLeg.append(departTimeForFN[firstDepartTime])
		
		count += 1

		flightNumsInLeg.append(arriveTimeForFN[flightNumsInLeg[-2]])

		totalTripProb = reduce(lambda x, y: x*y, flightsProbs)
		totalFbTripProb = reduce(lambda x, y: x+y, fbProbs)
		#print("Total prob for trip:", totalTripProb, "Total FB probs: ", totalFbTripProb, "Flight Nums: ", flightNumsInLeg)
		#print("--------------END TRIP-------------\n\n")

		flightNumsInLeg.append(totalTripProb)

		finalSortedProbFlights.append(flightNumsInLeg)
	
		finalProbFlights.append(totalTripProb)
			

	#	#print nonRevPattern.findall(line)
	#	#print firstBusinessPattern.findall(line)
		##print coachPattern.findall(line)


count_array = np.array(finalProbFlights, dtype = np.object)
final_count_array = np.array(finalSortedProbFlights, dtype = np.object)

idx = np.argsort(count_array)

mostProbableFlights = []

#print(final_count_array[idx])

#print("Max is : ", max(finalProbFlights))

for f in final_count_array[idx]:
	if (f[-1] == max(finalProbFlights)):
		mostProbableFlights.append(f)

for f in mostProbableFlights:
	f.append(len(f))


sortedFlights = sorted(mostProbableFlights, key=lambda k : k[-1])

for s in sortedFlights:
	departTime = s[-4][:5]
	amPM = s[-4][-2:]
	departHour = 1337

	if (amPM == 'PM'):
		departHour = to24(int(departTime[0:2]),1)
	else:
		departHour = to24(int(departTime[0:2]),0)

	departMinute = departTime[3:5]
	#timeNowObject = datetime.now()
	#timeNowObject = datetime.strptime('Dec 12 2013 7:30pm', '%b %d %Y %I:%M%p')
	timeNowObject = datetime.strptime(leaveTimeAndDate, '%m/%d/%Y %I:%M%p')
	departTimeObject = timeNowObject.replace(hour=departHour, minute=int(departMinute), second=0, microsecond=0)
	#print(timeNowObject , departTimeObject)
	if (timeNowObject < departTimeObject):
		#print(s)
		for i in range(0, s[-1] - 3):
			print(finalFlightDict[s[i]])
		break


filelist = [ f for f in os.listdir(".") if f.endswith(".txt") ]		#remove .txt files

#for f in filelist:
#    os.remove(f)

