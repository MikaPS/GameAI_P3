

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def enemy_sent_fleets(state):
  return len(state.enemy_fleets()) > 0

def owns_most_planets(state):
  return len(state.my_planets())/2 >= len(state.enemy_planets())