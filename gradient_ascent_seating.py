import random
import copy
from itertools import combinations

# Objective function to maximize (metric for evaluating a seating arrangement)
def compute_score(g, tables, arrangement):

    score = 0

    if arrangement == 0:
        for table in tables:
            for comb in combinations(table,2):
                if g.has_edge(comb[0], comb[1]):
                    score += 1
    elif arrangement == 1:
        for table in tables:
            for i in range(len(table)-1):
                if g.has_edge(table[i][0], table[i][1]):
                    score += 1
                if g.has_edge(table[i][0], table[i+1][0]):
                    score += 2
                if g.has_edge(table[i][0], table[i+1][1]):
                    score += 1
                if g.has_edge(table[i][1], table[i+1][0]):
                    score += 1
                if g.has_edge(table[i][1], table[i+1][1]):
                    score += 2

    return score

# Limited version of objective function. Computes local score
# This function is faster and can be used to evaluate the effect of swapping 2 guests
def compute_local_score(g, tables, tdx, rdx, arrangement):
    score = 0

    if arrangement == 0:
        for comb in combinations(tables[tdx], 2):
            if g.has_edge(comb[0], comb[1]):
                score += 1
    elif arrangement == 1:
        if g.has_edge(tables[tdx][rdx][0], tables[tdx][rdx][1]):
            score += 1
        if rdx < len(tables[tdx])-1:
            if g.has_edge(tables[tdx][rdx][0], tables[tdx][rdx+1][0]):
                score += 2
            if g.has_edge(tables[tdx][rdx][0], tables[tdx][rdx+1][1]):
                score += 1
            if g.has_edge(tables[tdx][rdx][1], tables[tdx][rdx+1][0]):
                score += 1
            if g.has_edge(tables[tdx][rdx][1], tables[tdx][rdx+1][1]):
                score += 2
        if rdx > 0:
            if g.has_edge(tables[tdx][rdx][0], tables[tdx][rdx-1][0]):
                score += 2
            if g.has_edge(tables[tdx][rdx][0], tables[tdx][rdx-1][1]):
                score += 1
            if g.has_edge(tables[tdx][rdx][1], tables[tdx][rdx-1][0]):
                score += 1
            if g.has_edge(tables[tdx][rdx][1], tables[tdx][rdx-1][1]):
                score += 2

    return score

# Initialize tables based on randomized list
def init_tables(rand_list, max_table_size, num_tables, arrangement):
    if arrangement == 0:
        tables = [[rand_list[i] for i in range(j, min(j+max_table_size, len(rand_list)))] for j in range (0, len(rand_list), max_table_size)]
    elif arrangement == 1:
        tables = [[] for i in range(num_tables)]
        for i in range(0, len(rand_list), 2):
            tables[(i//2) % num_tables].append([rand_list[i], rand_list[i+1]])
    return tables

# Get table indices by name of guest
def get_table_idx(tables, name, arrangement):
    if arrangement == 0:
        for table in tables:
            if name in table:
                return (tables.index(table), 0, table.index(name))
    elif arrangement == 1:
        for table in tables:
            for row in table:
                if name in row:
                    return (tables.index(table), table.index(row), row.index(name))

# INPUTS
# max_iter       : Maximum number of iterations for algorithm
# num_tables     : Number of long tables (only used for arrangement 1)
# max_table_size : Maximum table size
# g              : Graph with relationship information
# neighbor_dict  : Dictionary with relationship information
# arrangement    : Type of table arrangement (0 is separate tables, 1 is long tables)
# OUTPUTS
# current_score  : Score of arrangement, determined by objective function
# tables         : List containing arrangement

def gradient_ascent(max_iter, num_tables, max_table_size, g, neighbor_dict, arrangement):
    # Initialize
    sorted_neighbors = [i for i in neighbor_dict.keys()]
    rand_sorted_neighbors = random.sample(sorted_neighbors, len(sorted_neighbors))
    tables = init_tables(rand_sorted_neighbors, max_table_size, num_tables, arrangement)
    next_tables = copy.deepcopy(tables)
    current_score = compute_score(g, tables, arrangement)
    
    i = 0

    while i < max_iter:

        max_improvement = 0

        for comb in combinations(rand_sorted_neighbors, 2):

            # Get table, row (only relevant for long tables), and seat indices of two guests
            tdx_0, rdx_0, sdx_0 = get_table_idx(tables, comb[0], arrangement)
            tdx_1, rdx_1, sdx_1 = get_table_idx(tables, comb[1], arrangement)

            # If guests aren't already seated together, swap them and check for improvement in objective function
            if (tdx_0 != tdx_1) or ((arrangement == 1) and (sdx_0 != sdx_1)):

                test_tables = copy.deepcopy(tables)
                if arrangement == 0:
                    test_tables[tdx_0][sdx_0], test_tables[tdx_1][sdx_1] = test_tables[tdx_1][sdx_1], test_tables[tdx_0][sdx_0]
                elif arrangement == 1:
                    test_tables[tdx_0][rdx_0][sdx_0], test_tables[tdx_1][rdx_1][sdx_1] = test_tables[tdx_1][rdx_1][sdx_1], test_tables[tdx_0][rdx_0][sdx_0]

                # temp_score = compute_score(g, test_tables, arrangement) - current_score
                curr_score_0 = compute_local_score(g, tables, tdx_0, rdx_0, arrangement)
                curr_score_1 = compute_local_score(g, tables, tdx_1, rdx_1, arrangement)
                new_score_0 = compute_local_score(g, test_tables, tdx_0, rdx_0, arrangement)
                new_score_1 = compute_local_score(g, test_tables, tdx_1, rdx_1, arrangement)
                curr_score = curr_score_0 + curr_score_1
                new_score = new_score_0 + new_score_1

                # if temp_score > max_improvement:
                if (new_score) > (curr_score):
                    next_tables = copy.deepcopy(test_tables)
                    max_improvement = new_score - curr_score

        tables = copy.deepcopy(next_tables)
        current_score += max_improvement
        print("Iteration " + str(i) + " Score " + str(current_score))
        i += 1

        if max_improvement == 0:
            break

    return (current_score, tables)
