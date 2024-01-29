import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
import logging

def best_send(state,destination,enemy):
    costs = dict()
    enemy_distance = enemy.turns_remaining
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    # checks if we are under attack
    planets_under_attack = []
    for fleet in state.enemy_fleets():
        planets_under_attack.append(fleet.destination_planet)
    
    for planet in my_planets: 
        # not enough ships to win over the planet
        if planet.num_ships < 3:
            continue
        
        if planet.ID in planets_under_attack:
            continue

        my_distance = state.distance(planet.ID, destination.ID)
        difference_distance = my_distance - enemy_distance
        if difference_distance < 1:
            continue
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
    # checks if we are under attack
    planets_under_attack = []
    for fleet in state.enemy_fleets():
        planets_under_attack.append(fleet.destination_planet)

    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    for planet in my_planets: 
        if planet.ID in planets_under_attack:
            continue
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
    # get all fleets
    enemy_fleets = state.enemy_fleets()
    neutral_planets = state.neutral_planets()

    for enemy_fleet in enemy_fleets:
        my_planet = -1
        already_sent_ship = False
        destination = state.planets[enemy_fleet.destination_planet]  
        if destination in neutral_planets:
            costs = dict()
            enemy_distance = enemy_fleet.turns_remaining
            my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
            # checks if we are under attack
            planets_under_attack = []
            for fleet in state.enemy_fleets():
                planets_under_attack.append(fleet.destination_planet)
            
            for planet in my_planets: 
                # not enough ships to win over the planet
                if planet.num_ships < 3:
                    continue
                # don't send fleets from planets who are under attack
                if planet.ID in planets_under_attack:
                    continue

                my_distance = state.distance(planet.ID, destination.ID)
                difference_distance = my_distance - enemy_distance
                if difference_distance < 1:
                    continue
                else:
                    cost = enemy_fleet.num_ships - destination.num_ships + (difference_distance) * destination.growth_rate + 1 
                
                costs[planet] = cost

            if costs:
                smallest_planet = min(costs, key=costs.get)
                my_planet, required_ships = smallest_planet, costs[smallest_planet]
            else:
                my_planet, required_ships = -1, -1
            # my_planet, required_ships = best_send(state, destination, enemy_fleet)
        
        if my_planet != -1:
            for fleet in state.my_fleets():
                if fleet.destination_planet == destination.ID:
                    already_sent_ship = True
                    break
            if already_sent_ship == False:
                issue_order(state, my_planet.ID, destination.ID, required_ships)
    return True

    

def steal_defend(state):
    #get all fleets
    enemy_fleets = state.enemy_fleets()
    my_planets = state.my_planets()

    for enemy_fleet in enemy_fleets:
        my_planet = -1
        already_sent_ship = False
        destination = state.planets[enemy_fleet.destination_planet]  
        if destination in my_planets:
            costs = dict()
            enemy_distance = enemy_fleet.turns_remaining
            # checks if we are under attack
            planets_under_attack = []
            for fleet in state.enemy_fleets():
                planets_under_attack.append(fleet.destination_planet)

            sorted_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
            for planet in sorted_planets: 
                if planet.ID in planets_under_attack:
                    continue
                # not enough ships to win over the planet
                if planet.num_ships < 3:
                    continue

                my_distance = state.distance(planet.ID, destination.ID)
                difference_distance = my_distance - enemy_distance
                if destination.num_ships + destination.growth_rate * enemy_distance <= enemy_fleet.num_ships:
                    if difference_distance < 1: # < 1 so we get there a turn after # we are closer to the opponent
                        cost = enemy_fleet.num_ships - destination.num_ships - destination.growth_rate * enemy_distance + 1
                    else:
                        # num of attacking ships - num of defending ships
                        num_defend = destination.num_ships + destination.growth_rate * enemy_distance 
                        num_offense = enemy_fleet.num_ships + difference_distance * destination.growth_rate 
                        cost = num_offense - num_defend + 1
                else:
                    continue
                costs[planet] = cost

            if costs:
                smallest_planet = min(costs, key=costs.get)
                my_planet, required_ships = smallest_planet, costs[smallest_planet]
            else:
                my_planet, required_ships = -1, -1
            # my_planet, required_ships = best_desend(state, destination, enemy_fleet)
        
        if my_planet != -1:
            for fleet in state.my_fleets():
                if fleet.destination_planet == destination.ID:
                    already_sent_ship = True
                    break
            if already_sent_ship == False:
                issue_order(state, my_planet.ID, destination.ID, required_ships)
    return True

def attack_weakest_enemy_planet(state):
    # (1) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (2) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (3) Send half the ships from my strongest planet to the weakest enemy planet.
        distance = state.distance(strongest_planet.ID, weakest_planet.ID)
        cost = weakest_planet.num_ships + weakest_planet.growth_rate * distance + 1
        issue_order(state, strongest_planet.ID, weakest_planet.ID, cost)
    return True


def have_most_troops(state):
    # attack both the stongest and weakest planets
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
    # remaining_planets = [planet for planet in state.enemy_planets() if planet != weakest_planet]
    # Find the second weakest planet
    strongest_enemy_planet = max(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet or not strongest_enemy_planet: 
        # No legal source or destination
        return False
    else:
        distance = state.distance(strongest_planet.ID, weakest_planet.ID)
        cost = weakest_planet.num_ships + weakest_planet.growth_rate * distance + 1
        issue_order(state, strongest_planet.ID, weakest_planet.ID, cost)
        distance = state.distance(strongest_planet.ID, strongest_enemy_planet.ID)
        cost = strongest_enemy_planet.num_ships + strongest_enemy_planet.growth_rate * distance + 1
        issue_order(state, strongest_planet.ID, strongest_enemy_planet.ID, cost)
    return True




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
