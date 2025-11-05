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

def calculate_dist(width, height, num_of_values, prob=0.9):
    # Area between two array is smaller than the area of the main diagonal.
    # Area of main diagonal is the dist between rays * length of the diagonal
    # Length of the diagonal = (width**2 + height**2)**0.5
    # probability to get a point in this diagonal is the Area of the diagonal/total area
    # The probability to get two points on the same diagonal is (n choose 2) * the last probability
    # we want this probability to be lower than 1 - prob

    # 1 - ((x * (width**2 + height**2)**0.5) / width*height ) * ((num_of_values * (num_of_values - 1)) / 2) = prob
    # isolating x will give us:
    # x = (1 - prob) * width * height / diagonal length * num of values choose 2
    rectangle_area = width*height
    n_choose_two = num_of_values * (num_of_values - 1) / 2
    diagonal_length =  (width**2 + height**2)**0.5
    dist_between_rays = ((1 - prob) * rectangle_area) / (diagonal_length * n_choose_two)
    return dist_between_rays


if __name__ == "__main__":
    # print(find_prob(1,2,0.25))
    # print(find_dist(10,8,10,0.99))
    print(calculate_dist(10,8,10,0.99))
