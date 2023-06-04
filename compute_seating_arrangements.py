import networkx
import numpy
import matplotlib
import random
import copy
import math
import csv
from itertools import combinations
from naive_seating import *
from gradient_ascent_seating import gradient_ascent

def main():

    ##
    ## CSV Import and Preprocessing
    ##

    fields = []
    rows = []
    with open("wedding_seating_arrangements.csv", 'r') as f:
        csvreader = csv.reader(f)
        fields = next(csvreader)
        
        for row in csvreader:
            rows.append(row)
        
        graph = {}
        weights = {}
        for row in rows:
            graph[row[0]] = []
            for col in range(1,len(row)):
                if row[col]:
                    graph[row[0]].append(fields[col])
                    weights[tuple(sorted((row[0], fields[col])))] = int(row[col])

    g = networkx.Graph()

    for k, vs in graph.items():
        for v in vs:
            g.add_edge(k, v, weight=weights[tuple(sorted((k,v)))])

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

    ##
    ## Evaluate algorithms
    ##
    
    # print("Evaluating naive algorithm...")
    # best_tables = []
    # best_score = 0
    # for table_sz in range(1,10):
        # best_tables_temp = arrange_tables(g, table_sz, neighbor_dict)
        # best_score_temp = compute_score(g, best_tables_temp)
        # print("Table Size " + str(table_sz) + ':   ' + str(compute_score(g, arrange_tables(g, table_sz, neighbor_dict))))
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
            # score, tables = gradient_ascent(50, 0, i, g, neighbor_dict, 0)
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
    for i in range(1):
        score, tables = gradient_ascent(200, 2, 26, g, neighbor_dict, 1)
        if score > best_score:
            best_tables = tables
            best_score = score
        print("Run " + str(i) + ", Score: " + str(score))

    print("Final Score: " + str(best_score))
    print(best_tables)

if __name__ == "__main__":
    main()