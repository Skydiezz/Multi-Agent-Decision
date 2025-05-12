import random
from environment import TerrainType, AntPerception
from ant import AntAction, AntStrategy


class NonCooperativeAgent(AntStrategy):
    """
    A simple non-cooperative agent



    """

    def __init__(self):
        """Initialize the strategy with last action tracking"""
        
        self.movements = {}  # ant_id -> [action1, action2, ...]
        self.path_found = {} # ant_id -> True | False
        self.factor = {} # ant_id -> ..., -2, -1, 0, 1, 2, ...
        self.returning = {} # ant_id -> True | False

    def decide_action(self, perception: AntPerception) -> AntAction:
        """Decide an action based on current perception"""

    
        # Get ant's ID to track its actions
        ant_id = perception.ant_id
        movement_list = self.movements.get(ant_id, []) 
        

        # Priority 1: Pick up food if standing on it
        if (
            not perception.has_food
            and (0, 0) in perception.visible_cells
            and perception.visible_cells[(0, 0)] == TerrainType.FOOD
        ):
            movement_list.append("FOOD")
            self.movements[ant_id] = movement_list
            return AntAction.PICK_UP_FOOD

        # Priority 2: Drop food if at colony and carrying food
        if (
            perception.has_food
            and TerrainType.COLONY in perception.visible_cells.values()
        ):
            for pos, terrain in perception.visible_cells.items():
                if terrain == TerrainType.COLONY:
                    if pos == (0, 0):  # Directly on colony
                        movement_list.append("COLONY")
                        self.movements[ant_id] = movement_list
                        return AntAction.DROP_FOOD

        # Otherwise, perform movement
        action = self._decide_movement(perception)
        return action
    
    def _random_move(self, ant_id, movement_list, perception):
        movement_choice = random.random()
        

        if (0,1) in perception.visible_cells:

            front_cell = perception.visible_cells[(0,1)]
        elif (1,0) in perception.visible_cells:
            front_cell = perception.visible_cells[(1,0)]
        elif (-1,0) in perception.visible_cells:
            front_cell = perception.visible_cells[(-1,0)]
        elif (0,-1) in perception.visible_cells:
            front_cell = perception.visible_cells[(0,-1)]
        else:
            front_cell = None

        # print(f"SURROUNDINGS : {perception.visible_cells}")
        # print(f"FRONT : {front_cell}")
        if front_cell == TerrainType.WALL or len(perception.visible_cells) == 1 or len(perception.visible_cells) == 4:
            if movement_choice > 0.5:
                movement_list.append("TURN RIGHT")
                self.movements[ant_id] = movement_list
                return AntAction.TURN_RIGHT
            elif movement_choice <= 0.5:
                movement_list.append("TURN_LEFT")
                self.movements[ant_id] = movement_list
                return AntAction.TURN_LEFT
        else:
            if movement_choice < 0.6:
                movement_list.append("MOVE_FORWARD")
                self.movements[ant_id] = movement_list
                return AntAction.MOVE_FORWARD
            elif movement_choice < 0.8:
                movement_list.append("TURN_LEFT")
                self.movements[ant_id] = movement_list
                return AntAction.TURN_LEFT
            else:
                movement_list.append("TURN_RIGHT")
                self.movements[ant_id] = movement_list
                return AntAction.TURN_RIGHT

    def _decide_movement(self, perception: AntPerception) -> AntAction:
        """Decide which direction to move based on current state"""
        
        print("------------------------------------------------------NEW STEP")
        ant_id = perception.ant_id
        movement_list = self.movements.get(ant_id, [])
        path_found = self.path_found.get(ant_id, False)
        factor = self.factor.get(ant_id, 0)
        

        if movement_list:
            last = movement_list[-1]
        else:
            last = None


        # if the ant is on the colony or food it'll just go back to the last food
        if last == "COLONY" or last == "FOOD":


            if last == "FOOD":
                print("Food Found")

                self.factor[ant_id] = -1
                movement_list.pop(-1)
                if path_found:
                    for i in range(4):
                        movement_list.pop(0)
                        
                for i in range(4):
                    movement_list.append("TURN_LEFT")

                weight = len(movement_list)
                print(f"GOING BACK TO COLONY, CURRENT PATH WEIGHT : \n" \
                f"------------------ W => {weight}" \
                "")
                self.path_found[ant_id] = True
                path_found = True
                self.returning[ant_id] = True


            if last == "COLONY":
                self.factor[ant_id] = 0
                print("Got back to colony")
                movement_list.pop(-1)
                self.returning[ant_id] = False

                print("Avant :", movement_list)
                if self.path_found[ant_id] == True:
                    for i in range(4):
                        movement_list.pop(-1)

                if factor < len(movement_list):
                    movement_list = movement_list[factor+1:] if factor < -1 else movement_list[:-1]
                else:
                    movement_list = []


                for i in range(4):
                    movement_list.insert(0, "TURN_LEFT")
                print("Après :", movement_list)



                print(movement_list) 
                weight = len(movement_list)               
                print(f"GOING BACK TO FOOD, CURRENT PATH WEIGHT : \n" \
                f"------------------ W => {weight}" \
                "")
                self.movements[ant_id] = movement_list
                self.path_found[ant_id] = True
                path_found = True
            
            print(f"PATH FOUND ? ----> {path_found}")
            self.movements[ant_id] = movement_list
            
        # if a path has been found follow this path
        returning = self.returning.get(ant_id, False)
        actual_factor = self.factor.get(ant_id, 0)
        if abs(actual_factor) < len(movement_list) and actual_factor >= 0 or abs(actual_factor) <= len(movement_list) and actual_factor < 0:
            move = movement_list[actual_factor]
        elif actual_factor != 0:
            print(">>> PATH END REACHED OR INVALID FACTOR, RESETTING")
            self.path_found[ant_id] = False
            self.factor[ant_id] = 0
            if actual_factor < 0:
                for i in range(4):
                    movement_list.pop(-1)
            else:
                for i in range(4):
                    movement_list.pop(0)
            self.movements[ant_id] = movement_list
        else:
            self.path_found[ant_id] = False
            self.factor[ant_id] = 0            


        if self.path_found[ant_id] :
            
            print(f"ABSOLUTE VALUE : {abs(self.factor.get(ant_id))}")
            print(f"WEIGHT : {len(movement_list)}")
            print(f"Current factor : {actual_factor}")
            print(f"Ant ID : {ant_id}")
            

            if actual_factor < 0:
                self.factor[ant_id] -= 1
            elif actual_factor >= 0:
                self.factor[ant_id] += 1

            print(f"Following path...   ->> {move}")
            match move:
                case "MOVE_FORWARD" | "MOVE FORWARD":
                    return AntAction.MOVE_FORWARD
                case "TURN_LEFT" | "TURN LEFT":
      
                    if returning:
                        return AntAction.TURN_RIGHT
                    else:
                        return AntAction.TURN_LEFT
                case "TURN_RIGHT" | "TURN RIGHT":

                    if returning:
                        return AntAction.TURN_LEFT
                    else:
                        return AntAction.TURN_RIGHT
                case _:

                    print(f"/\ WARNING ------> the move, {move} doens't match")
        print("Not currently following any path...")

        # If has food, try to move toward colony if visible
        if perception.has_food:
            for pos, terrain in perception.visible_cells.items():
                if terrain == TerrainType.COLONY:
                    if pos[1] > 0:
                          # Colony is ahead in some direction
                        movement_list.append("MOVE_FORWARD")
                        self.movements[ant_id] = movement_list
                        return AntAction.MOVE_FORWARD

        # If doesn't have food, try to move toward food if visible
        else:
            for pos, terrain in perception.visible_cells.items():
                if terrain == TerrainType.FOOD:
                    if pos[1] > 0:  # Food is ahead in some direction

                        movement_list.append("MOVE_FORWARD")
                        self.movements[ant_id] = movement_list
                        return AntAction.MOVE_FORWARD

        move = self._random_move(ant_id, movement_list, perception)
        return move


