import os
import random
import sys
import math

# Declaring Globals here
n = 32
m = 15000
num_resources = 4
max_iterations = 1

potential = 'delta'
g = 0.8

p_max = 1
p_min = 0
v_min = -1
v_max = 1
c1 = 2
c2 = 2
wi = 1

pred_list = []
succ_list = []
duration = []
res_req_list = []
max_resources = []

# Global bests
gBest_pos = [0 for x in range(0, n)]
gBest_vel = [0 for x in range(0, n)]
gBest_cost = sys.maxsize
best_solution = []

for i in range(0, n):
    pred_list.append([])
    succ_list.append([])
    res_req_list.append([])
    duration.append(0)


class Particles:
    def __init__(self):
        self.pos = [0 for x in range(0, n)]
        self.best_pos = [0 for x in range(0, n)]
        self.best_cost = sys.maxsize


# Earlier called Schedule
class Activity:
    def __init__(self):
        self.activity_id = 0
        self.start_time = 0
        self.duration = 0
        self.f_time = 0


# Creating m particles
particles = [Particles() for x in range(0, m)]


# Globals end here -----

def initialize_particles():  # O(n)
    for i in range(0, m):
        particles[i].pos = [random.uniform(p_min, p_max) for x in range(0, n)]
        # particles[i].vel = [random.uniform(v_min, v_max) for x in range(0, n)]

        particles[i].best_pos = particles[i].pos
        particles[i].best_cost = sys.maxsize


# File reader and list creator //TESTED : Perfect!
def read_file(filename):
    f = open(filename, 'r')

    i = 0
    for line in f:
        i += 1

        if i in range(19, n + 19):
            numbers = list(map(int, line.split()))
            activity_id = numbers[0] - 1
            successors = numbers[2]

            # Updating successor list
            for x in numbers[3:]:
                succ_list[activity_id].append(x - 1)

            # Updating predecessor list
            for x in numbers[3:]:
                pred_list[x - 1].append(activity_id)

        # Updating duration and resource list
        if i in range(n + 19 + 4, n + 19 + 4 + n):
            numbers = list(map(int, line.split()))
            activity_id = numbers[0] - 1
            duration[activity_id] = numbers[2]
            for x in numbers[3:]:
                res_req_list[activity_id].append(x)

        # Storing maximum resources available
        if i == 2 * n + 19 + 4 + 3:
            global max_resources
            max_resources = list(map(int, line.split()))


def get_feasible_activities2(finished, scheduled, completed_preds):  # O(n)
    feasible_activities = []
    for x in range(0, n):
        if completed_preds[x] == len(pred_list[x]):
            if not scheduled[x]:
                feasible_activities.append(x)
    return feasible_activities


def execute_on_file(filename, g):
    read_file(filename)
    initialize_particles()
    iterations = 0
    while iterations < max_iterations:

        mbest = [0 for x in range(0, n)]

        for i in range(0, n):
            mbest[i] = 0
            for j in range(0, m):
                mbest[i] = mbest[i] + particles[j].best_pos[i]

        # for i in range(0,m) :
        # mbest = [ x+y for x,y in zip(mbest,particles[i].best_pos) ]

        mbest = [x / m for x in mbest]

        for i in range(0, m):
            perform_ops_on_particle(i, g, mbest)

        best_solution.append(gBest_cost)
        iterations += 1

    # print best_solution
    print
    gBest_cost
    return gBest_cost


def perform_ops_on_particle(i, g, mbest):
    global gBest_cost, gBest_pos

    # Equations for Quantum PSO
    c1 = random.uniform(0, 1)
    c2 = random.uniform(0, 1)
    P = (w + u for w, u in zip([c1 * x for x in particles[i].best_pos], [c2 * y for y in gBest_pos]))
    P = [x / (c1 + c2) for x in P]

    u = random.uniform(0, 1)

    up = 0

    diff = [x - y for x, y in zip(mbest, particles[i].pos)]
    diff = [abs(x) for x in diff]

    print("======Diff:\n\n\n", diff)
    temp = [g * x * math.log(1 / u) for x in diff]
    print("temp: ")
    print(temp)
    print("\n")
    if random.uniform(0, 1) < 0.5:
        particles[i].pos = [abs(x - y) for x, y in zip(P, temp)]
    else:
        particles[i].pos = [x + y for x, y in zip(P, temp)]

    print("x+y: ")
    print( x+y for x,y in zip(P, temp))




    # print "Particle no:%d" % i
    print("Pos: ", particles[i].pos)
    print("\n")
    # print "Vel: ", particles[i].vel

    # """ Evaluating the schedule """

    scheduled = [False for x in range(0, n)]
    finished = [False for x in range(0, n)]
    scheduleList = []
    time = 0

    a0 = Activity()
    a0.activity_id = 0
    a0.start_time = 0
    a0.duration = 0

    # Adding the activity to the schedule list
    scheduleList.append(a0)
    scheduled[0] = True

    finished_activity = 0
    resources_left = max_resources
    completed_preds = [0 for x in range(n)]

    while 1:
        # print "Activity %d finished." % finished_activity
        # Take the resources back
        if not finished[finished_activity]:
            resources_left = [x + y for x, y in zip(resources_left, res_req_list[finished_activity])]
            finished[finished_activity] = True
            for x in succ_list[finished_activity]:
                completed_preds[x] = completed_preds[x] + 1

        if len(scheduleList) >= n:
            break

        # Finding all the activities for which precedence constraints are satisfied.
        # feasible_activities = get_feasible_activities(finished, scheduled)
        feasible_activities = get_feasible_activities2(finished, scheduled, completed_preds)

        # Sort the feasible_activities in descending order
        def priority(activity_id):
            return particles[i].pos[activity_id]

        feasible_activities = sorted(feasible_activities, key=priority, reverse=True)

        # print "Time: %d  Feasible Activities are: " % time,
        # for j in feasible_activities:
        #     print j,
        # print ''

        # Checking feasible activities for resource constraints.
        for activity in feasible_activities:
            flag_new = 0
            for x, y in zip(resources_left, res_req_list[activity]):
                if x < y:
                    flag_new = 1  # Resource requirement not satisfied.

            if flag_new == 0:
                # This activity can be scheduled.
                # Add it to the schedule and to the schedule list.
                a1 = Activity()
                a1.activity_id = activity
                a1.start_time = time
                a1.duration = duration[activity]
                a1.f_time = a1.start_time + a1.duration
                scheduleList.append(a1)
                scheduled[activity] = True

                # Update resources
                resources_left = [w - z for w, z in zip(resources_left, res_req_list[activity])]

        # Earliest finish time of the scheduled activities is stored in finish_time
        def finishTime(a):
            if not finished[a.activity_id]:
                return a.f_time
            return sys.maxsize

        activity_with_min_finish_time = min(scheduleList, key=finishTime)
        finish_time = activity_with_min_finish_time.f_time

        if finish_time != sys.maxsize and finished_activity != activity_with_min_finish_time:
            time = finish_time
            finished_activity = activity_with_min_finish_time.activity_id

    # Now, the parallel schedule has been formed for this particle
    # So, comparing it with other's now.

    # print "Activities | StartTime"
    cost = 0
    for activity in scheduleList:
        # print activity.activity_id, activity.start_time
        cost = max(cost, activity.f_time)
    print("Total cost: ", cost)

    # Update local best
    if cost < particles[i].best_cost:
        particles[i].best_pos = particles[i].pos
        particles[i].best_cost = cost

    # update global best
    if cost < gBest_cost:
        gBest_pos = particles[i].pos
        gBest_cost = cost

    si = random.uniform(0, 1)
    particles[i].best_pos = [si * x + (1 - si) * y for x, y in zip(particles[i].best_pos, gBest_pos)]


if __name__ == '__main__':
    execute_on_file("Dataset/j302_10.sm", .51)