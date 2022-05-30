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

def main(layer):
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

		######
		#if row_id == 7:
		#	print("####", row.Shape.firstPoint, row.Shape.lastPoint)


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


layer = "roads_smol_92"

nodes, edges = main(layer)