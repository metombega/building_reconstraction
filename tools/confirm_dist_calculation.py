import random

def find_dist(width, height, num_of_values, min_prob):
    """ Given a width, height, number of points. 
    the function will find the distance needed between two rays so that there won't be two points
    at the same ray with a probability of at least min_prob.
    """
    x_prev = 0
    x_curr = 1
    found = False
    while (not found):
        if find_prob(min(width, height), num_of_values, x_curr) > min_prob:
            found = True
        else:
            tmp = x_prev
            x_curr = (x_curr + x_prev)/2
            x_prev = tmp

    return x_curr

def find_prob(min_dimention, num_of_values, max_length_between_vals):
    results = []
    for test in range(10000):
        vals = []
        for _ in range(num_of_values):
            vals.append(random.uniform(0,min_dimention))
        found_two_close_points = True
        for i in range(len(vals)-1):
            for j in range(i+1, len(vals)):
                if abs(vals[i] - vals[j]) < max_length_between_vals:
                    found_two_close_points = False
        results.append(found_two_close_points)
    print(f"Length: {max_length_between_vals}. Prob: {sum(results)/len(results)}")
    return sum(results)/len(results)

if __name__ == "__main__":
    print(find_prob(1,2,0.25))
    print(find_dist(10,8,10,0.9))

