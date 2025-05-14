from environment import TerrainType, AntPerception
from ant import AntAction, AntStrategy
from common import Direction

class PathMemoryStrategy(AntStrategy):
    """
    A non-cooperative ant that memorizes the path to food and retraces it to return to the colony.
    """

    def __init__(self):
        # Memory for each ant: tracks paths and state
        self.ant_memory = {}  # ant_id -> {"path": [...], "returning": bool, "pathFound": bool}


    def decide_action(self, perception: AntPerception) -> AntAction:
        
        ant_id = perception.ant_id

        # Initialize memory for new ants
        if ant_id not in self.ant_memory:
            self.ant_memory[ant_id] = {"path": [(0,0)], "returning": False, "pathFound": False}

        memory = self.ant_memory[ant_id]
        path = memory.get('path')
        print(f"Actual path : {path}")
        print(f"Actual direction : {perception.direction}")

        # 1. Pick up food if standing on it
        if not perception.has_food and (0, 0) in perception.visible_cells and perception.visible_cells[(0, 0)] == TerrainType.FOOD:
            memory["returning"] = True  # Start retracing
            memory["pathFound"] = True 
            return AntAction.PICK_UP_FOOD

        # 2. Drop food if at colony
        if perception.has_food and (0, 0) in perception.visible_cells and perception.visible_cells[(0, 0)] == TerrainType.COLONY:
            memory["returning"] = False
            return AntAction.DROP_FOOD
        

        # 4. Decide movement
        if not perception.has_food:
            # Going to food: build path
            if memory["pathFound"]:
                action = self._following_path_action(perception, memory["returning"])
                return action
            action = self._choose_exploration_action(perception)
            return action
        else:
            # Returning to colony: follow path in reverse
            if memory["path"]:
                action = self._following_path_action(perception, memory["returning"])
                return action
            else:
                action = self._choose_exploration_action(perception)
                return action # Fallback

    def _choose_exploration_action(self, perception: AntPerception) -> AntAction:
        """Basic exploration behavior to reach food (simple forward-biased random walk)"""
        import random
        r = random.random()

        if len(perception.visible_cells) == 1 or len(perception.visible_cells) == 4:
            if r > 0.5:
                return AntAction.TURN_RIGHT
            elif r <= 0.5:
                return AntAction.TURN_LEFT


        if r < 0.6:
            self._get_new_coordinates(perception)
            return AntAction.MOVE_FORWARD
        elif r < 0.8:
            print("GOING LEFT")
            return AntAction.TURN_LEFT
        else:
            print("GOING RIGHT")
            return AntAction.TURN_RIGHT
        
    def _following_path_action(self, perception: AntPerception, returning) -> AntAction:
        
        """
        
            Fonction to follow a path when coming back to the colony or the food
        
        """

        ant_id = perception.ant_id
        memory = self.ant_memory.get(ant_id)
        path = memory.get("path")

        if returning:
            actual_pos = path[-1]
            target_pos = path[-2]
        else:
            actual_pos = path[0]
            target_pos = path[1]

        delta = tuple(x - y for x,y in zip(target_pos, actual_pos))

        direction_to_take = perception._get_direction_from_delta(delta[0], delta[1])
        actual_direction = perception.direction

        if direction_to_take == actual_direction.value:
            
            if returning:
                path.pop(-1)
                path.insert(0, actual_pos)
            else:
                path.pop(0)
                path.append(actual_pos)

            memory["path"] = path
            self.ant_memory[ant_id] = memory
            return AntAction.MOVE_FORWARD

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


    def _get_new_coordinates(self, perception: AntPerception):

        """

            function to compute the new coordinates of the ant after a forward move
        
        """

        ant_id = perception.ant_id
        ant_memory = self.ant_memory.get(ant_id)
        path = ant_memory.get("path")
        actual_coordinates =  path[-1]
        direction = perception.direction

        delta = Direction.get_delta(direction)
        new_coordinate = tuple(x + y for x,y in zip(actual_coordinates, delta))

        print(f"GOING TO THE COORDINATES : {new_coordinate}")

        # Saving the new coordinates in the memory

        path.append(new_coordinate)
        ant_memory["path"] = path
        self.ant_memory[ant_id] = ant_memory
        