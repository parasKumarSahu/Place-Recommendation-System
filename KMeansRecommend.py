import matplotlib.pyplot as plt
import random as rnd
import math 
from collections import defaultdict
from collections import OrderedDict
import operator
import webbrowser

readCluster = False

Mat = []

#List of user ids
User_ids = []
#List of latitudes
Latitudes = []
#List of longitudes
Longitudes = []
#Location ids
Location_ids = []

#Load data for a given id, sampling = 0 for no loss
#Sampling used only in Task-6
def load_data(id, sampling):
	User_ids.clear()
	Latitudes.clear()
	Longitudes.clear()
	print("Reading data, please wait...")
	f = open("Brightkite_totalCheckins.txt")
	for i in f:
		l = i.split()
		if len(l)>3 and (id == -1 or  id == int(l[0])) and int(l[0])%sampling == 0:
			User_ids.append(int(l[0]))
			Latitudes.append(float(l[2]))		
			Longitudes.append(float(l[3]))	
			Location_ids.append(l[4])	
	print(len(User_ids), "entries read from the file Brightkite_totalCheckins.txt")	

def plot_graph(title, x, y, lab):
	plt.title(title)
	plt.scatter(x, y, label=lab)
	plt.xlabel("Latitudes")
	plt.ylabel("Longitudes")
	plt.ylim(-150, 150)
	plt.xlim(-50, 50)
	plt.gca().set_aspect('equal', adjustable='box')
	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

#Used by K-means()
def centroid(Cluster):
	x = 0
	y = 0
	for i in Cluster:
		x += Latitudes[i]
		y += Longitudes[i]
	return x/len(Cluster), y/len(Cluster)	  

def Kmeans(k):
	print("Running K-means with k =", k)
	centroids_lat = []
	centroids_long = []
	clusters = []
	dist_from_clusters = []

	for i in range(k):
		clusters.append([])
		rn = rnd.randint(int(len(User_ids)*i/k), int(len(User_ids)*(i+1)/k))
		centroids_lat.append(Latitudes[rn])
		centroids_long.append(Longitudes[rn])
		dist_from_clusters.append(9999.9999)

	for it in range(5):
		for i in range(k):
			clusters[i].clear()
		for i in range(len(User_ids)):
			for j in range(k):
				dist_from_clusters[j] = math.sqrt( (centroids_lat[j]-Latitudes[i])**2 
					+ (centroids_long[j]-Longitudes[i])**2)
			min_index = dist_from_clusters.index(min(dist_from_clusters))
			clusters[min_index].append(i)	
		for i in range(k):
			if len(clusters[i]) > 0:
				centroids_lat[i], centroids_long[i] = centroid(clusters[i])
	return clusters

def square_rooted(x): 
    return round(math.sqrt(sum([a*a for a in x])),3)
 
def cosine_similarity(x, y): 
   numerator = sum(a*b for a,b in zip(x,y))
   denominator = square_rooted(x)*square_rooted(y)
   return numerator/float(denominator)

def getSimilarity(user_id, i):
	return cosine_similarity(Mat[user_id], Mat[i])

def getMaxRowNumber(similarity):
	max_ind = 0
	max_val = 0
	for i in range(len(similarity)):
		if max_val < similarity[i]:
			max_val = similarity[i]
			max_ind = i
	return max_ind

def getIndexOf(_id, users_ordered):
	for i in range(len(users_ordered)):
		if users_ordered[i] == _id:
			return i
	return -1

def most_frequent(List): 
    return max(set(List), key = List.count)

def recommendationSystem(_id, users_ordered, no_of_clusters, clusters):
	no_of_top_users = 10
	_id = getIndexOf(_id, users_ordered)
	similarity = [0 for k in range(len(Mat))]
	for i in range(len(Mat)):
		if i != _id:
			similarity[i] = getSimilarity(_id, i)

	top_similar = []
	for i in range(no_of_top_users):
		row_no = getMaxRowNumber(similarity)
		print("id", users_ordered[row_no], "similarity", similarity[row_no])
		similarity[row_no] = 0
		top_similar.append(row_no)

	resultant = [0 for k in range(no_of_clusters)]

	for i in range(no_of_clusters):
		for j in range(len(top_similar)):
			resultant[i] += Mat[top_similar[j]][i]

	max_ind = 0
	max_cluster = 0
	for i in range(len(resultant)):
		if max_cluster < resultant[i]:
			max_cluster = resultant[i]
			max_ind = i

	recommended_cluster = clusters[max_ind]

	recommended_lats = [Latitudes[ind] for ind in recommended_cluster]
	recommended_longs = [Longitudes[ind] for ind in recommended_cluster]

	load_data(users_ordered[_id], 1)
	plt.figure(3)
	plot_graph("Selected User", Latitudes, Longitudes, "Entered User")
	plt.show(block=False)
	plt.figure(4)
	for i in range(no_of_top_users):
		load_data(users_ordered[top_similar[i]], 1)
		plot_graph("Selected Users", Latitudes, Longitudes, "Similar User "+str(i+1))
	plt.show(block=False)

	return most_frequent(recommended_lats), most_frequent(recommended_longs)

def writeInFile(clusters, filename):
	with open(filename, "w") as f:
		for cluster in clusters:
			for item in cluster:
				f.write(str(item) + "\t")
			f.write("\n")


def readFromFile(filename):
	clusters = []
	with open(filename) as f:
		for line in f:
			arr = line.split("\t")[:-1]
			#print(arr)
			for i in range(len(arr)):
				arr[i] = int(arr[i].strip())
			clusters.append(arr)
	return clusters


##############################################################################
#Main function
readCluster = input("Press 1 to cluster or 2 to run Recommendation System: ")

k = 30
sampling = 1

if readCluster == "1":
	load_data(-1, sampling)
	clusters = Kmeans(k)
	writeInFile(clusters, 'cluster.txt')
else:
	_id = int(input("Enter user id: "))
	load_data(-1, sampling)
#	plt.figure(1)
#	plot_graph("Input Data", Latitudes, Longitudes, "All data points")
#	plt.show(block=False)
	clusters = readFromFile('cluster.txt')
	plt.figure(2)
	for i in range(k):		
		plot_graph("K-means "+"K = "+str(k), 
			[Latitudes[k] for k in clusters[i]],
			[Longitudes[k] for k in clusters[i]], "cluster "+str(i+1))
	plt.show(block=False)

	set_cluster_user = []
	for i in range(len(clusters)):
		tmp = set()
		for j in clusters[i]:
			tmp.add(User_ids[j])
		set_cluster_user.append(tmp)	

	users_ordered = list(set(User_ids))
	for i in users_ordered:
		tmp = []
		for j in range(len(clusters)):
			if i in set_cluster_user[j]:
				tmp.append(1)
			else:
				tmp.append(0)	
		Mat.append(tmp)

	print(len(Mat))

	result = recommendationSystem(_id, users_ordered, len(clusters), clusters)
	show_option = input("Open location in browser?(y/n): ")
	if show_option == "y":
		webbrowser.open_new_tab("https://www.google.com/maps/place/"+
			str(result[0])+","+str(result[1]))