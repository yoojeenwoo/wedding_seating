import networkx
import numpy
import matplotlib
import random
import copy
import math
import csv
from itertools import combinations

fields = []
rows = []
with open("wedding_seating_arrangements.csv", 'r') as f:
	csvreader = csv.reader(f)
	fields = next(csvreader)
	
	for row in csvreader:
		rows.append(row)
	
	graph = {}
	for row in rows:
		graph[row[0]] = []
		for col in range(1,len(row)):
			if row[col]:
				graph[row[0]].append(fields[col])

g = networkx.Graph()

for k, vs in graph.items():
	for v in vs:
		g.add_edge(k, v)
		
## Preprocessing

# Compute number of neighbors per node
neighbor_dict = {}
for i in g.nodes:
	num = 0
	for j in g.neighbors(i):
		num += 1
	neighbor_dict[i] = num

# Sort by number of neighbors
neighbor_dict = dict(sorted(neighbor_dict.items(), key=lambda item: item[1]))
# for i in neighbor_dict.items():
	# print(i)

# Metric for evaluating a seating arrangement
def compute_score(g, tables):
	score = 0
	for table in tables:
		for comb in combinations(table,2):
			if g.has_edge(comb[0], comb[1]):
				score += 1
	return score

def compute_score_long(g, tables):
	score = 0
	for table in tables:
		for i in range(len(table)-1):
			if g.has_edge(table[i][0], table[i][1]):
				score += 1
			for j in range(2):
				if g.has_edge(table[i][j], table[i+1][0]):
					score += 1
				if g.has_edge(table[i][j], table[i+1][1]):
					score += 1
	return score

		

## Naive Seating Algorithm

# Seat a designated person's friends at a table
def seat_table(g, sorted_neighbors, starting_person, tables, num, table_idx): 
	seated = 0
	for i in sorted_neighbors:
		if g.has_edge(i, starting_person):
			tables[table_idx].append(i)
			sorted_neighbors.remove(i)
			seated += 1
			if seated == num:
				return seated
	return seated

def arrange_tables(max_table_size, neighbor_dict):
	table_idx = 0
	tables = [[] for i in range(math.ceil(len(neighbor_dict)/max_table_size))]
	sorted_neighbors = [i for i in neighbor_dict.keys()]

	while sorted_neighbors:
		table_size = 0
		table_alloc = min(max_table_size, len(sorted_neighbors))
		while table_size < table_alloc:
			# Seat a "starting person"
			tables[table_idx].append(sorted_neighbors[0])
			starting_person = sorted_neighbors.pop(0)
			table_size += 1

			# Seat friends, friends of friends, etc.
			for i in tables[table_idx]:
				if table_size < table_alloc:
					#print(str(i) + ' ' + str(table_idx))
					table_size += seat_table(g, sorted_neighbors, i, tables, table_alloc - table_size, table_idx)

			if table_size == table_alloc:
				table_idx += 1
	return tables
	
## Gradient Ascent Seating Algorithm

def get_table_idx(tables, name):
	for table in tables:
		if name in table:
			return (tables.index(table), table.index(name))

def get_table_idx_long(tables, name):
	for table in tables:
		for row in table:
			if name in row:
				return (tables.index(table), table.index(row), row.index(name))

def gradient_ascent(max_iter, max_table_size, g, neighbor_dict):
	# Initialize
	sorted_neighbors = [i for i in neighbor_dict.keys()]
	rand_sorted_neighbors = random.sample(sorted_neighbors, len(sorted_neighbors)) # Randomize starting state
	tables = [[rand_sorted_neighbors[i] for i in range(j, min(j+max_table_size, len(rand_sorted_neighbors)))] for j in range(0, len(rand_sorted_neighbors), max_table_size)]
	next_tables = copy.deepcopy(tables)
	current_score = compute_score(g, tables)
	
	i = 0
	while i < max_iter:
		max_improvement = 0
		for comb in combinations(rand_sorted_neighbors, 2):
			table_idx_0, seat_idx_0 = get_table_idx(tables, comb[0])
			table_idx_1, seat_idx_1 = get_table_idx(tables, comb[1])
			if (table_idx_0 != table_idx_1):
				test_tables = copy.deepcopy(tables)
				test_tables[table_idx_0][seat_idx_0], test_tables[table_idx_1][seat_idx_1] = test_tables[table_idx_1][seat_idx_1], test_tables[table_idx_0][seat_idx_0]
				temp_score = compute_score(g, test_tables) - current_score
				if temp_score > max_improvement:
					next_tables = copy.deepcopy(test_tables)
					max_improvement = temp_score
		tables = copy.deepcopy(next_tables)
		current_score += max_improvement
		i += 1
		if max_improvement == 0:
			break
	return (current_score, tables)

## Gradient Ascent Seating Algorithm (Long Tables)

def gradient_ascent_long(max_iter, num_tables, max_table_size, g, neighbor_dict):
	# Initialize
	sorted_neighbors = [i for i in neighbor_dict.keys()]
	rand_sorted_neighbors = random.sample(sorted_neighbors, len(sorted_neighbors))
	tables = [[] for i in range(num_tables)]
	for i in range(0, len(sorted_neighbors), 2):
		tables[(i//2) % num_tables].append([rand_sorted_neighbors[i], rand_sorted_neighbors[i+1]])
	next_tables = copy.deepcopy(tables)
	current_score = compute_score_long(g, tables)

	i = 0
	while i < max_iter:
		max_improvement = 0
		for comb in combinations(rand_sorted_neighbors, 2):
			table_idx_0, row_idx_0, seat_idx_0 = get_table_idx_long(tables, comb[0])
			table_idx_1, row_idx_1, seat_idx_1 = get_table_idx_long(tables, comb[1])
			if (seat_idx_0 != seat_idx_1) or (table_idx_0 != table_idx_1):
				test_tables = copy.deepcopy(tables)
				test_tables[table_idx_0][row_idx_0][seat_idx_0], test_tables[table_idx_1][row_idx_1][seat_idx_1] = test_tables[table_idx_1][row_idx_1][seat_idx_1], test_tables[table_idx_0][row_idx_0][seat_idx_0]
				temp_score = compute_score_long(g, test_tables) - current_score
				if temp_score > max_improvement:
					next_tables = copy.deepcopy(test_tables)
					max_improvement = temp_score
		tables = copy.deepcopy(next_tables)
		current_score += max_improvement
		i += 1
		if max_improvement == 0:
			break
	return (current_score, tables)

def main():
	
	# print("Evaluating naive algorithm...")
	# best_tables = []
	# best_score = 0
	# for table_sz in range(1,10):
		# best_tables_temp = arrange_tables(table_sz, neighbor_dict)
		# best_score_temp = compute_score(g, best_tables_temp)
		# print("Table Size " + str(table_sz) + ':   ' + str(compute_score(g, arrange_tables(table_sz, neighbor_dict))))
		# if best_score_temp > best_score:
			# best_tables = best_tables_temp
			# best_score = best_score_temp
	# print("Final Score: " + str(best_score))
	# print(best_tables)
	
	# print("Evaluating gradient ascent algorithm...")
	# best_tables = []
	# best_score = 0
	# for i in range(6,11):
		# best_tables_temp = []
		# best_score_temp = 0
		# for j in range(20):
			# score, tables = gradient_ascent(50, i, g, neighbor_dict)
			# if score > best_score_temp:
				# best_tables_temp = tables
				# best_score_temp = score
		# print("Table Size " + str(i) + ':   ' + str(best_score_temp))
		# if best_score_temp > best_score:
			# best_tables = best_tables_temp
			# best_score = best_score_temp
# 
	# print("Final Score: " + str(best_score))
	# print(best_tables)
	
	print("Evaluating gradient ascent algorithm for long tables...")
	best_tables = []
	best_score = 0
	for i in range(20):
		score, tables = gradient_ascent_long(100, 2, 18, g, neighbor_dict)
		if score > best_score:
			best_tables = tables
			best_score = score
		print("Iteration " + str(i) + ", Score: " + str(score))

	print("Final Score: " + str(best_score))
	print(best_tables)

if __name__ == "__main__":
	main()