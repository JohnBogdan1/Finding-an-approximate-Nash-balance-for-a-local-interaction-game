import random
from functools import reduce


class Builder:
    def __init__(self, builder_id):
        self.builder_id = builder_id
        self.neighbours = []
        self.p_distribution = ()
        self.new_strategy = ()
        self.gain = 0


def print_builders(builders):
    for builder in builders:
        print(builder.builder_id, end=": ")
        for neighbour in builder.neighbours:
            print(neighbour.builder_id, end=' ')
        print("->", builder.p_distribution)


def generate_random_distribution(p_distributions):
    return p_distributions[random.randint(0, len(p_distributions) - 1)]


def my_float(v):
    return float("{:.2f}".format(v))


def distributions(delta):
    i, j = 0, 0
    p_distributions = []
    while i < 1:
        while j <= 1 - i:
            p_distributions.append((my_float(i), my_float(j), my_float(1 - i - j)))
            j += delta
        j = 0
        i += delta

    return p_distributions

# Generate problem instance
def generate_instance(road_length, delta=0.1):
    west_builders, east_builders = [Builder(i + 1) for i in range(road_length)], [Builder(i + 1) for i in
                                                                                  range(road_length, 2 * road_length)]

    p_distributions = distributions(delta)
    for i in range(road_length):
        if i > 0:
            west_builders[i].neighbours.append(west_builders[i - 1])
            east_builders[i].neighbours.append(east_builders[i - 1])

        if i < road_length - 1:
            west_builders[i].neighbours.append(west_builders[i + 1])
            east_builders[i].neighbours.append(east_builders[i + 1])

        west_builders[i].neighbours.append(east_builders[i])
        east_builders[i].neighbours.append(west_builders[i])

        west_builders[i].p_distribution = generate_random_distribution(p_distributions)
        east_builders[i].p_distribution = generate_random_distribution(p_distributions)

    print_builders(west_builders + east_builders)

    return west_builders + east_builders


def utility(builder, new_strategy=None):
    if not new_strategy:
        p_house, p_store, p_park = builder.p_distribution[0], builder.p_distribution[1], builder.p_distribution[2]
    else:
        p_house, p_store, p_park = new_strategy[0], new_strategy[1], new_strategy[2]

    p_house_sum = reduce((lambda x, y: my_float(x + y)),
                         [neighbour.p_distribution[0] for neighbour in builder.neighbours])
    p_store_sum = reduce((lambda x, y: my_float(x + y)),
                         [neighbour.p_distribution[1] for neighbour in builder.neighbours])
    p_park_sum = reduce((lambda x, y: my_float(x + y)),
                        [neighbour.p_distribution[2] for neighbour in builder.neighbours])

    u_house = my_float((1 / (1 + max(1, p_house_sum) - min(1, p_house_sum))) + (p_park_sum / 2.0))
    u_store = my_float((p_house_sum / 3.0) + (1 / (1 + p_store_sum)))
    u_park = my_float(p_house_sum / 3.0)

    return my_float(p_house * u_house + p_store * u_store + p_park * u_park)


def regret(builder, new_strategy=None):
    u = utility(builder)
    new_u = utility(builder, new_strategy)
    return my_float(new_u - u)


def find_biggest_regret(builder, delta):
    i, j = 0, 0
    max_regret = float("-inf")
    strategy = ()

    while i < 1:
        while j <= 1 - i:
            new_p_regret = regret(builder, (my_float(i), my_float(j), my_float(1 - i - j)))

            if new_p_regret > max_regret:
                max_regret = new_p_regret
                strategy = (my_float(i), my_float(j), my_float(1 - i - j))
            j += delta
        j = 0
        i += delta

    builder.new_strategy = strategy

    return max_regret


def find_nash_balance(builders, delta):
    while True:
        total_score = 0
        for builder in builders:
            total_score += find_biggest_regret(builder, delta)

        print(total_score)

        biggest_gain = float("-inf")
        chosen_builder = None
        for builder in builders:
            updated_total_score = 0

            builder_strategy = builder.p_distribution
            builder.p_distribution = builder.new_strategy

            for builder1 in builders:
                updated_total_score += regret(builder1, builder1.new_strategy)

            builder.gain = my_float(total_score - updated_total_score)

            builder.p_distribution = builder_strategy

            if builder.gain > biggest_gain:
                biggest_gain = builder.gain
                chosen_builder = builder

        if biggest_gain > 0.:
            chosen_builder.p_distribution = chosen_builder.new_strategy
        else:
            break

    print_builders(builders)


if __name__ == '__main__':
    delta = 0.1
    builders = generate_instance(5, delta)
    find_nash_balance(builders, delta)
