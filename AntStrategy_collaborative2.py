import random
from environment import TerrainType, AntPerception
from ant import AntAction, AntStrategy
from common import Direction


class Collaborative(AntStrategy):
    """
    A simple random strategy for ants.

    This strategy has minimal intelligence:
    - Picks up food when it sees it
    - Drops food at the colony
    - Tries to move towards food/colony when visible
    - Otherwise moves randomly
    - Always deposits pheromones after each step (home when searching, food when returning)
    """

    def __init__(self):
        """Initialize the strategy with last action tracking"""
        # Track the last action to alternate between movement and pheromone deposit
        self.ants_last_action = {}  # ant_id -> last_action


    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""

        # Get ant's ID to track its actions
        ant_id = perception.ant_id
        last_action = self.ants_last_action.get(ant_id, None)


        # Priority 1: Pick up food if standing on it
        if (
            not perception.has_food
            and (0, 0) in perception.visible_cells
            and perception.visible_cells[(0, 0)] == TerrainType.FOOD
        ):
            self.ants_last_action[ant_id] = AntAction.PICK_UP_FOOD

            return AntAction.PICK_UP_FOOD

        # Priority 2: Drop food if at colony and carrying food
        if (
            perception.has_food
            and TerrainType.COLONY in perception.visible_cells.values()
        ):
            for pos, terrain in perception.visible_cells.items():
                if terrain == TerrainType.COLONY:
                    if pos == (0, 0):  # Directly on colony
                        self.ants_last_action[ant_id] = AntAction.DROP_FOOD
                        return AntAction.DROP_FOOD

        # Deposit Food pheromone if just picked it
        if last_action == AntAction.PICK_UP_FOOD:
            self.ants_last_action[ant_id] = AntAction.DEPOSIT_FOOD_PHEROMONE
            return AntAction.DEPOSIT_FOOD_PHEROMONE
        
        # Deposit Home pheromone
        if last_action == AntAction.DROP_FOOD:
            self.ants_last_action[ant_id] = AntAction.DEPOSIT_HOME_PHEROMONE
            return AntAction.DEPOSIT_HOME_PHEROMONE
        
        # Drop home pheronome when spawning
        if last_action == None:
            self.ants_last_action[ant_id] = AntAction.DEPOSIT_HOME_PHEROMONE
            return AntAction.DEPOSIT_HOME_PHEROMONE



        # Otherwise, perform movement
        action = self._choose_exploration_action(perception)
        self.ants_last_action[ant_id] = action
        return action
        
    def _choose_exploration_action(self, perception: AntPerception) -> AntAction:
        """Basic exploration behavior to reach food (simple forward-biased random walk)"""

        r = random.random()
        ant_id = perception.ant_id
        if len(perception.visible_cells) == 1 or len(perception.visible_cells) == 4:
            if r > 0.5:
                return AntAction.TURN_RIGHT
            elif r <= 0.5:
                return AntAction.TURN_LEFT

        if perception.can_see_food():

            if self.ants_last_action.get(ant_id, None) != AntAction.DEPOSIT_FOOD_PHEROMONE:
                action = AntAction.DEPOSIT_FOOD_PHEROMONE
                return action
            else:
                if not perception.has_food:
                    action = self._choose_surrounding_action(perception, False)
                    return action
        
        if perception.can_see_colony():

            if self.ants_last_action.get(ant_id, None) != AntAction.DEPOSIT_HOME_PHEROMONE:
                action = AntAction.DEPOSIT_HOME_PHEROMONE
                return action
            elif perception.has_food:
                action = self._choose_surrounding_action(perception, True)
                return action
        if perception.has_food:
            sorted_pheromones = dict(
                sorted(
                    perception.home_pheromone.items(),
                    key=lambda item: (item[1] <= 0, item[1])
                )
            )
            first = list(sorted_pheromones.items())[0]
            if first[1] > 0 and self.ants_last_action.get(ant_id, None) != AntAction.DEPOSIT_HOME_PHEROMONE:
                action = AntAction.DEPOSIT_HOME_PHEROMONE
                return action         

        else:
            sorted_pheromones = dict(
                sorted(
                    perception.food_pheromone.items(),
                    key=lambda item: (item[1] <= 0, item[1])
                )
            )
            first = list(sorted_pheromones.items())[0]
            if first[1] > 0 and self.ants_last_action.get(ant_id, None) != AntAction.DEPOSIT_FOOD_PHEROMONE:
                action = AntAction.DEPOSIT_FOOD_PHEROMONE
                return action


        if first[1] > 0:
            action = self._follow_pheromone(perception, first[0])
            return action
        if r < 0.8:
            return AntAction.MOVE_FORWARD
        elif r < 0.9:
            return AntAction.TURN_LEFT
        else:
            return AntAction.TURN_RIGHT
    
    def _choose_surrounding_action(self, perception: AntPerception, go_to_colony: False) -> AntAction:

        """
        
            Check if there's any food in the ant's perception and if so, go towards it

        """

        if go_to_colony:
            direction_to_take = perception.get_colony_direction()
        else:
            direction_to_take = perception.get_food_direction()
        actual_direction = perception.direction


        if direction_to_take == actual_direction.value:
            
            return AntAction.MOVE_FORWARD   

        action = self._get_turn(actual_direction, direction_to_take)
        return action
    
    def _follow_pheromone(self, perception: AntPerception, target_pos):

        actual_direction = perception.direction
        direction_to_take = perception._get_direction_from_delta(target_pos[0], target_pos[1])
        if direction_to_take == actual_direction.value:
            
            return AntAction.MOVE_FORWARD

        action = self._get_turn(actual_direction, direction_to_take)
        return action

    def _get_turn(self, actual_direction, direction_to_take):
        
        """
            Get the turn to make to go the right direction
        """

        match actual_direction:
            case Direction.NORTH:
                if direction_to_take > 4:
                    return AntAction.TURN_LEFT
                else:
                    return AntAction.TURN_RIGHT
            case Direction.NORTHWEST:
                if direction_to_take < 4:
                    return AntAction.TURN_RIGHT
                else:
                    return AntAction.TURN_LEFT
            case _:
                if direction_to_take > actual_direction.value:
                    return AntAction.TURN_RIGHT
                else:
                    return AntAction.TURN_LEFT