import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging

def defense(state):
    pass

def best_send(state,destination,enemy):
    costs = dict()
    enemy_distance = enemy.turns_remaining
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    for planet in my_planets: 
        # not enough ships to win over the planet
        if planet.num_ships < 3:
            continue

        my_distance = state.distance(planet.ID, destination.ID)
        difference_distance = my_distance - enemy_distance
        if difference_distance < 1:
            # logging.info("here")
            continue
            # cost = enemy.num_ships + (difference_distance-1) * destination.growth_rate + 1
        else:
            cost = enemy.num_ships - destination.num_ships + (difference_distance) * destination.growth_rate + 1 
        
        costs[planet] = cost

    if costs:
        smallest_planet = min(costs, key=costs.get)
        return smallest_planet, costs[smallest_planet]

    return -1, -1

def best_desend(state,destination,enemy):
    costs = dict()
    enemy_distance = enemy.turns_remaining

    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    for planet in my_planets: 
        # not enough ships to win over the planet
        if planet.num_ships < 3:
            continue

        my_distance = state.distance(planet.ID, destination.ID)
        difference_distance = my_distance - enemy_distance
        if destination.num_ships + destination.growth_rate * enemy_distance <= enemy.num_ships:
            if difference_distance < 1: # < 1 so we get there a turn after # we are closer to the opponent
                cost = enemy.num_ships - destination.num_ships - destination.growth_rate * enemy_distance + 1
            else:
                # num of attacking ships - num of defending ships
                num_defend = destination.num_ships + destination.growth_rate * enemy_distance
                num_offense = enemy.num_ships + difference_distance * destination.growth_rate
                cost = num_offense - num_defend + 1

        else:
            continue
        costs[planet] = cost

    if costs:
        smallest_planet = min(costs, key=costs.get)
        return smallest_planet, costs[smallest_planet]

    return -1, -1
    

    
def steal(state):
    #get all fleets
    enemy_fleets = state.enemy_fleets()
    #sort by smallest
    if len(enemy_fleets) <= 0:
        return False

    my_planets = state.my_planets()#iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    # enemy_planets = state.enemy_planets()
    neutral_planets = state.neutral_planets() #iter(sorted(state.neutral_planets(), key=lambda p: p.num_ships, reverse=True))

    for enemy_fleet in enemy_fleets:
        my_planet = -1
        already_sent_ship = False
        destination = state.planets[enemy_fleet.destination_planet]  
        if destination in my_planets:
            my_planet, required_ships = best_desend(state, destination, enemy_fleet)
        elif destination in neutral_planets:
            my_planet, required_ships = best_send(state, destination, enemy_fleet)
        
        if my_planet != -1:
            for fleet in state.my_fleets():
                if fleet.destination_planet == destination.ID:
                    already_sent_ship = True
                    break
            if already_sent_ship == False:
                issue_order(state, my_planet.ID, destination.ID, required_ships)
    return False

            # if destination in my_planets:
            #     if my_planet.num_ships > ():
            #         issue_order(state, my_planet.ID, destination.ID, 2)
            #     pass
            # elif destination in neutral_planets:
            #     if difference_distance < 0:
            #         pass
            #     else:
            #         required_ships = difference_distance * destination.growth_rate + 1
            #         issue_order(state, my_planet.ID, destination.ID, required_ships)
            #         pass

            # if my_planet.num_ships > required_ships:
            #     issue_order(state, my_planet.ID, target_planet.ID, required_ships)
            #     my_planet = next(my_planets)
            #     target_planet = next(target_planets)
            # else:
            #     my_planet = next(my_planets)


    
    
def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
