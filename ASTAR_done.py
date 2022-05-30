"""
A star algorithm 

"""
import math as m
from queue import PriorityQueue

class node():
	def __init__(self, node_id, x, y):
		self.node_id = node_id
		self.x = x
		self.y = y
		self.edges = []
		self.neighbors = []

	def __str__(self):
		eids = [str(e.edge_id) for e in self.edges]
		return "N(" + str(self.node_id) + "," + str(self.x)  + "," + str(self.y)  + "," + "[" + ",".join(eids) + "])"

	def __repr__(self):
		eids = [str(e.edge_id) for e in self.edges]
		return "N(" + str(self.node_id) + "," + str(self.x)  + "," + str(self.y)  + "," + "[" + ",".join(eids) + "])"
		
	def coordinates(self):
		return self.x, self.y
		
	def get_neighbors(self):
		for i in self.edges:
			if self.node_id == i.start_node.node_id:
				self.neighbors.append(i.end_node.node_id)
			elif self.node_id  == i.end_node.node_id:
				self.neighbors.append(i.start_node.node_id)
		
class edge():
	def __init__(self, edge_id):
		self.edge_id = edge_id
		self.start_node = 0
		self.end_node = 0
		self.fclass = 0
		self.max_speed = 20000
 		self.oneway = 0
		self.length = 0
		self.travel_time = 0

	def __str__(self):
		return "E(" + str(self.edge_id) + "," + str(self.start_node.node_id) + "," + str(self.end_node.node_id) + ")"

	def __repr__(self):
		return "E(" + str(self.edge_id) + "," + str(self.start_node.node_id) + "," + str(self.end_node.node_id) + ")"

def node_create(id, point):
	n = node(id, point[0], point[1])
	nodes[id] = n
	node_index[point] = n

# euclidean distance
def euclidean(n1, n2):
	x1, y1 = n1.coordinates()
	x2, y2 = n2.coordinates()
	distance = m.sqrt((x1-x2)**2 + (y1-y2)**2)
	return distance 

# time cost based on euclidean and max speed 
def heuristics_time(n1, n2):
	distance = euclidean(n1, n2)
	time = distance / top_speed
	return time

def reconstruct_path(came_from, current):
	path = []
	while current in came_from:
		current = came_from[current]
		path.append(current)

def graph(layer):	
	edges={} #{edge_id, edge}
	nodes={} #{node_id, node}

	node_index={} #{coordiates, node}
	node_id=1

	cursor=arcpy.SearchCursor(layer) # arcMap layer

	def node_create(id, point):
		n = node(id, point[0], point[1])
		nodes[id] = n
		node_index[point] = n

	for row in cursor:
		# edge ID - row ID
		row_id = row.OBJECTID
		start_point = (round(row.Shape.firstPoint.X, 6), round(row.Shape.firstPoint.Y, 6))
		end_point = (round(row.Shape.lastPoint.X, 6), round(row.Shape.lastPoint.Y, 6))

		# create an edge 
		e = edge(row_id) #set other attributes
		edges[row_id] = e

		# add start point to nodes dict
		if start_point not in node_index:
			node_create(node_id, start_point)
			node_id=node_id+1

		# start point nodes to edges
		n1 = node_index[start_point]
		e.start_node = n1
		n1.edges.append(e)

		# add end point to nodes dict
		if end_point not in node_index:
			node_create(node_id, end_point)
			node_id=node_id+1

		# end point nodes to edges
		n2 = node_index[end_point]
		e.end_node = n2
		n2.edges.append(e)
		
	return nodes, edges

# actual algorithm
def algorithm(nodes, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {node:float("inf") for node in nodes}
	g_score[start] = 0
	f_score = {node:float("inf") for node in nodes}
	f_score[start] = heuristics_time(nodes[start], nodes[end])

	open_set_hash = {start}
	path = []
	
	while not open_set.empty():
		current = open_set.get()[2]
		open_set_hash.remove(current)
	
		if current in came_from.keys():
			if came_from[current] not in path:
				path.append(came_from[current])
	
		if current == end:
			path.append(end)
			return path
		
		nodes[current].get_neighbors()
		
		neigh = []
		for i in nodes[current].neighbors:
			if i not in neigh:
				neigh.append(i)

		for neighbor in neigh:
			dist = 0
			for i in edges.keys():
				if neighbor == edges[i].start_node.node_id and current == edges[i].end_node.node_id or neighbor == edges[i].end_node.node_id and current == edges[i].start_node.node_id:
					dist = edges[i].travel_time			
			temp_g_score = g_score[current] + dist

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current 
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + heuristics_time(nodes[neighbor], nodes[end])
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor],count, neighbor))
					open_set_hash.add(neighbor)	
	return False	

def main(layer, start, end, output):
	nodes, edges = graph(layer)

	path = algorithm(nodes, start, end)
	path_edges = []
	
	for j in edges.keys():
		for i in range(0,len(path)):
			if path[i] == edges[j].start_node.node_id and path[i-1] == edges[j].end_node.node_id or path[i] == edges[j].end_node.node_id and path[i-1] == edges[j].start_node.node_id:
				path_edges.append(j)

	for i in path_edges:
		query = "\"OBJECTID\"="+str(i)
		arcpy.SelectLayerByAttribute_management(layer,"ADD_TO_SELECTION",query)
		
	arcpy.CopyFeatures_management(layer, output)
	
	return path
layer = arcpy.GetParameterAsText(0)
start = int(arcpy.GetParameterAsText(1))
end = int(arcpy.GetParameterAsText(2))
output = arcpy.GetParameterAsText(3)
edges = {}
nodes = {}
path=main(layer, start, end, output)

max_speeds = {'path':500000000000, 'track':50, 'residential':40000, 'service':10000,'bridleway':100000,'unclassified':50000,'cycleway':25000,'footway':10000,'living_street':40000,'pedestrian':30000,'primary':100000,'primary_link':80000,'residential':40000,'secondary':60000,'secondary_link':60000,'service':30000,'steps':20000,'trietary':30000,'trietary_link':30000,'track_grade1':30000,'track_grade2':30000,'track_grade3':30000,'track_grade4':30000,'track_grade5':30000,'trunk':20000};
top_speed = max(max_speeds.values())