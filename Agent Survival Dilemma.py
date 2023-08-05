import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import random
import numpy as np

#dimention (width, height) and choose dots per inch
figure(figsize=(8, 6), dpi=80)

N = 4  # number of agents (Constant during problem)
L = 8  # number of foods (Constant during problem)
M = 100  # number of levels


class Direction:
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"
    ALL = [EAST, NORTH, SOUTH, WEST]
    GUIDE = {
            NORTH: [0, 1],
            SOUTH: [0, -1],
            EAST: [1, 0],
            WEST: [-1, 0],
        }

class Entity:
    FOOD = "food"
    AGENT = "agent"
    NOTHING = "nothing"

class Decision:
    def __init__(self, attack, direction):
        self.attack = attack
        self.direction = direction

class Game:
    def __init__(self, jungle):
        """initializes a game with the current agents present in the jungle

        Args:
            agents (Agent): _description_
        """
        self.jungle = jungle
        self.rewards = [{agent: agent.reward for agent in jungle.agents}]
        self.decisions = list()
    
    def level_up(self):
        # self.decisions.append({agent: agent.decision() for agent in self.jungle.agents})
        self.decisions.append(dict())
        agents = self.jungle.agents[:]
        for i in range(len(self.jungle.agents)):
            agent = random.choice(agents)
            self.decisions[-1][agent] = agent.decision()
            agent.move(self.decisions[-1][agent])
            agents.remove(agent)

        self.rewards.append({agent: agent.reward for agent in self.jungle.agents})

    def plot_rewards_average_in_each_level(self):
        average_rewards = [np.mean([reward[agent] for reward in self.rewards]) for agent in self.jungle.agents]
        x_axis = range(len(self.jungle.agents))
        _, ax = plt.subplots(1)
        print(average_rewards)
        ax.bar(x_axis, average_rewards)
        ax.set_xticks(x_axis)
        ax.set_xticklabels(self.jungle.agents)
        plt.show()

class Food:
    def __init__(self, position):
        self.entity = Entity.FOOD
        self.position = position
    
    def __str__(self):
        return "Food at (%d, %d)" % (self.position[0], self.position[1])

class Agent:
    def __init__(self, position, number, jungle):
        """initializes the agent entity

        Args:
            position (tuple): tuple of agent position
            number (int): A uniqe number given to each agent to distinguish them from eachother
            jungle (Jungle): the jungle in which the agent is operating
        """
        self.entity = Entity.AGENT
        self.number = number
        self.reward = 0  # increases when 1. eats food 2. attack another agent(has more reward than 1th one)
        self.position = position
        self.jungle = jungle

    def __str__(self):
        #return "Agent No. %d" % (self.number)
        return "Agent No. %d at (%d, %d)\n" \
        "Current reward: %d" % (self.number, self.position[0], self.position[1], self.reward)

    def neighbours(self):
        """Specify neighbours

        Returns:
            list: Returns a list of lists [i, j] of neighbours
        """
        row_neighbours = range(self.position[0]-1, self.position[0]+2)
        column_neighbours = range(self.position[1]-1, self.position[1]+2)
        return [
            [i, j]
            for i in row_neighbours  if 1 <= i <= self.jungle.environment_size[0]
            for j in column_neighbours  if 1 <= j <= self.jungle.environment_size[1]
        ]
    def eat_food(self):
        self.reward += 1

    def attack(self, vacant):
        if vacant:
            self.reward -= 1
        else:
            self.reward += 2

    def defeated(self):
        self.reward -= 4

    def move(self, decision):
        """Moves the agent one tile in the direction indicated

        Raises:
            Exception("Wrong direction."): in case the specified direction is invalid

        Args:
            direction (Direction): Can be one of NORTH, EAST, SOUTH or WEST of the class Direction.
        """

        new_position = list(np.add(self.position, Direction.GUIDE[decision.direction]))
        operator = self.jungle.entity(new_position)

        if operator == Entity.NOTHING:
            if decision.attack:
                self.attack(vacant=True)
            self.jungle.ocuppied_cells.remove(self.position)
            self.position = new_position
            self.jungle.ocuppied_cells.append(self.position)
        else:
            if operator.entity == Entity.AGENT:
                agent = operator
                if decision.attack:
                    agent.defeated()
                    self.attack(vacant=False)
            elif operator.entity == Entity.FOOD:
                self.eat_food()
                if decision.attack:
                    self.attack(vacant=True)
    
    def decision(self):
        """agent must pick a specific strategy and improve it level by level. 
        And finaly learning how to make a decision based on:
                1. Its current observations and
                2. The result of previous strategies on the currrent reward
        that maximizes the reward(by Reinforcement learning)

        Returns:
            Decision: returns a Decision (which the agent thinks 
            that decision would benefit him the most. And benefit means higher reward.)
        """
        attack = random.choice([True] + [False]*20)
        neighbours = self.neighbours()
        available_directions = [direction for direction in Direction.ALL 
            if list(np.add(self.position, Direction.GUIDE[direction])) in neighbours]
        for direction, position in Direction.GUIDE.items():
            operator = self.jungle.entity(self.position+position)
            if operator != Entity.NOTHING:
                if operator.entity == Entity.FOOD and direction in available_directions:
                    available_directions += [direction]*5
        direction = random.choice(available_directions)
        return Decision(attack, direction)

class Jungle():
    def __init__(self):
        """initializes the jungle and the entities within the jungle
        """

        self.environment_size = (20, 20)
        self.agents_no = N
        self.foods_no = L
        self.ocuppied_cells = []
        self.agents = []
        self.foods = []
        self.populate_env()
    
    def populate_env(self):
        """Populates the jungle with agents and foods, choosing randomly the respective positions
        """

        for i in range(self.agents_no):
            while True:
                random_position = [random.randint(1, self.environment_size[j]) for j in range(2)]
                if random_position not in self.ocuppied_cells:
                    break
            self.agents.append(Agent(random_position, i+1, self))
            self.ocuppied_cells.append(random_position)
        for i in range(self.foods_no):
            while True:
                random_position = [random.randint(1, self.environment_size[i]) for i in range(2)]
                if random_position not in self.ocuppied_cells:
                    break
            self.foods.append(Food(random_position))
            self.ocuppied_cells.append(random_position)
    
    def entity(self, position):
        """Finds the entity at the specified position

        Args:
            position (tuple): (i, j) of the position being queried

        Returns:
            Agent or Food or Entity: returns the presenting agent or food, otherwise an Entity
        """
        for agent in self.agents:
            if agent.position == position:
                return agent
        for food in self.foods:
            if food.position == position:
                return food
        return Entity.NOTHING

if __name__=='__main__':
    jungle = Jungle()
    game = Game(jungle)
    for _ in range(M):
        game.level_up()
        for agent in jungle.agents:
            print(agent)
        print("Processing ...")
    game.plot_rewards_average_in_each_level()