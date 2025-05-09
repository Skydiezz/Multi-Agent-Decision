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


            

            for i in range(len(movement_list)):
                if movement_list[i] == "TURN_LEFT":
                    movement_list[i] = "TURN_RIGHT"
                elif movement_list[i] == "TURN_RIGHT":
                    movement_list[i] = "TURN_LEFT"

            if factor < 0:
                self.factor[ant_id] = 0
            elif factor >= 0:
                self.factor[ant_id] = -1

            print(movement_list)

            if last == "FOOD":
                print("found")


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


            if last == "COLONY":
                
                movement_list.pop(-1)
                movement_list = movement_list[factor:-1]
                for i in range(4):
                    movement_list.pop(-1)
                    movement_list.insert(0, "TURN_LEFT")
                weight = len(movement_list)               
                print(f"GOING BACK TO FOOD, CURRENT PATH WEIGHT : \n" \
                f"------------------ W => {weight}" \
                "")
                self.movements[ant_id] = movement_list
            
            
            self.movements[ant_id] = movement_list


        if abs(factor) == len(movement_list) and len(movement_list) != 0:
            
            print("---------------------------" \
            "--------------------------------" \
            "\n \n"\
            "PATH OUT OF REACH, LOOKING FOR A NEW PATH"\
            "\n\n"\
            "---------------------" \
            "------------------------------"
            )
            path_found = False
            self.path_found[ant_id] = False

            
        # if a path has been found follow this path

        if path_found:
            
            print(f"ABSOLUTE VALUE : {abs(self.factor.get(ant_id))}")
            print(f"WEIGHT : {len(movement_list)}")
            actual_factor = self.factor.get(ant_id)
            print(f"Current factor : {actual_factor}")
            move = movement_list[actual_factor]

            print(f"Following path...   ->> {move}")

            if actual_factor < 0:
                self.factor[ant_id] -= 1
            elif actual_factor >= 0:
                self.factor[ant_id] += 1

            match move:
                case "MOVE_FORWARD":
                    print("------------GOING FORWARD")
                    return AntAction.MOVE_FORWARD
                case "TURN_LEFT":
                    print("------------GOING LEFT")
                    return AntAction.TURN_LEFT
                case "TURN_RIGHT":
                    print("------------GOING RIGHT")
                    return AntAction.TURN_RIGHT

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

        # Random movement if no specific goal
        movement_choice = random.random()

        if movement_choice < 0.6:  # 60% chance to move forward
            movement_list.append("MOVE_FORWARD")
            self.movements[ant_id] = movement_list
            return AntAction.MOVE_FORWARD
        elif movement_choice < 0.8:  # 20% chance to turn left
            movement_list.append("TURN_LEFT")
            self.movements[ant_id] = movement_list
            return AntAction.TURN_LEFT
        else:  # 20% chance to turn right
            movement_list.append("TURN_RIGHT")
            self.movements[ant_id] = movement_list
            return AntAction.TURN_RIGHT
