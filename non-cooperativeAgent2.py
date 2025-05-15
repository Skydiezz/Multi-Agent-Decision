from environment import TerrainType, AntPerception
from ant import AntAction, AntStrategy
from common import Direction

class PathMemoryStrategy(AntStrategy):
    """
    A non-cooperative ant that memorizes the path to food and retraces it to return to the colony.
    """

    def __init__(self):
        # Memory for each ant: tracks paths and state
        self.ant_memory = {}  # ant_id -> {"path": [...], "returning": bool, "pathFound": bool, "foodpos": (int, int)}


    def decide_action(self, perception: AntPerception) -> AntAction:
        
        ant_id = perception.ant_id

        # Initialize memory for new ants
        if ant_id not in self.ant_memory:
            self.ant_memory[ant_id] = {"path": [(0,0)], "returning": False, "pathFound": False, "foodpos": None, "actual_pos": (0,0), "col_pos": (0,0)}

        memory = self.ant_memory[ant_id]
        path = memory.get('path')
        # print(f"Actual path : {path}")
        # print(f"Actual direction : {perception.direction}")
        # print("---------------------------------------")
        # print(f"FOOD POSITION : {memory["foodpos"]}")
        # print(f"COLONY POSITION : {memory["col_pos"]}")
        # print(f"ACTUAL POSITION : {memory["actual_pos"]}")


        # 1. Pick up food if standing on it
        if not perception.has_food and (0, 0) in perception.visible_cells and perception.visible_cells[(0, 0)] == TerrainType.FOOD:
            
            # if memory["pathFound"]:
            #     actual_coordinates = path[0]
            #     path.pop(0)
            #     path.append(actual_coordinates)
            #     memory["path"] = path
            # else:
            #     memory["pathFound"] = True
            #     actual_coordinates = path[-1]

            memory["pathFound"] = True
            memory["foodpos"] = memory["actual_pos"]
            memory["returning"] = True  # Start retracing
            
            

            return AntAction.PICK_UP_FOOD

        # 2. Drop food if at colony
        if perception.has_food and (0, 0) in perception.visible_cells and perception.visible_cells[(0, 0)] == TerrainType.COLONY:

            # actual_coordinates = path[-1]
            # path.pop(-1)
            # path.insert(0, actual_coordinates)


            # if path[0] != (0, 0) and (0,0) in path:
            #     while path[-1] != (0,0):
            #         path.pop(-1)
            #     path.pop(-1)

            if memory["col_pos"] != memory["actual_pos"]: # updating the colony position if the current one is wrong
                memory["col_pos"] = memory["actual_pos"]

            memory["path"] = path
            memory["returning"] = False
            return AntAction.DROP_FOOD
        

        # 4. Decide movement
        if not perception.has_food:
            # Going to food: build path
            if memory["pathFound"]:
                # Check if the ant is actually on the foodpos, if that's case it means there's no more food in this place

                actual_coordinates = memory["actual_pos"]
                if actual_coordinates != memory["foodpos"]:                            
                    action = self._following_path_action(perception, memory["returning"])
                    return action
                else:
                    # print(">>> NO FOOD FOUND, LOOKING FOR ANOTHER FOOD")
                    path.pop(0)
                    path.append(actual_coordinates)
                    memory["path"] = path
                    memory["pathFound"] = False
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

        if perception.can_see_food():
            action = self._choose_surrounding_action(perception)
            return action

        if r < 0.8:
            action = self._get_new_coordinates(perception, True)
            return action
        elif r < 0.9:
            return AntAction.TURN_LEFT
        else:
            return AntAction.TURN_RIGHT
    
    def _choose_surrounding_action(self, perception: AntPerception) -> AntAction:

        """
        
            Check if there's any food in the ant's perception and if so, go towards it

        """

            
        ant_id = perception.ant_id
        memory = self.ant_memory.get(ant_id)

        direction_to_take = perception.get_food_direction()
        actual_direction = perception.direction


        if direction_to_take == actual_direction.value:
            
            action = self._get_new_coordinates(perception)
            return action

        action = self._get_turn(actual_direction, direction_to_take)
        return action



    def _following_path_action(self, perception: AntPerception, returning) -> AntAction:
  
        """
        
            Fonction to follow a path when coming back to the colony or the food
        
        """

 
        ant_id = perception.ant_id
        memory = self.ant_memory.get(ant_id)
        actual_pos = memory["actual_pos"]


        if memory["returning"]:
            target_pos = memory["col_pos"]
        else:
            target_pos = memory["foodpos"]


        path = memory.get("path")

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

            action = self._get_new_coordinates(perception)
            memory["path"] = path
            self.ant_memory[ant_id] = memory
            return action

        action = self._get_turn(actual_direction, direction_to_take)
        return action


    def _get_new_coordinates(self, perception: AntPerception, exploring=False):

        """

            function to compute the new coordinates of the ant after a forward move
        
        """

        ant_id = perception.ant_id
        ant_memory = self.ant_memory.get(ant_id)
        path = ant_memory.get("path")
        actual_coordinates =  ant_memory.get("actual_pos")
        direction = perception.direction

        delta = Direction.get_delta(direction)
        new_coordinate = tuple(x + y for x,y in zip(actual_coordinates, delta))

        # if exploring:

        #     actual_diff = self.distance_squared(actual_coordinates, ant_memory["col_pos"])
        #     new_diff = self.distance_squared(new_coordinate, ant_memory["col_pos"])
        #     if actual_diff > new_diff:

        #         return AntAction.TURN_LEFT

        # Saving the new coordinates in the memory
        if not ant_memory["pathFound"]:
            path.append(new_coordinate)

    
        ant_memory["actual_pos"] = new_coordinate
        ant_memory["path"] = path
        self.ant_memory[ant_id] = ant_memory
        return AntAction.MOVE_FORWARD

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
    def distance_squared(self, p, ref):
        return (p[0] - ref[0])**2 + (p[1] - ref[1])**2
             
        


        
        