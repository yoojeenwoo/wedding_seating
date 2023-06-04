import math

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

def arrange_tables(g, max_table_size, neighbor_dict):
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
