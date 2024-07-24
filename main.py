import simpy
import random

# Constants
AVG_ARRIVAL_TIME = 5 * 60  # Average time between vessel arrivals in minutes
CONTAINERS_PER_VESSEL = 150
CRANE_MOVE_TIME = 3  # Time for a crane to move one container in minutes
TRUCK_MOVE_TIME = 6  # Time for a truck to transport a container and return in minutes
SIMULATION_TIME = 24 * 60  # Total simulation time in minutes

class ContainerTerminal:
    def __init__(self, env):
        self.env = env
        self.berths = simpy.Resource(env, capacity=2)
        self.cranes = simpy.Resource(env, capacity=2)
        self.trucks = simpy.Resource(env, capacity=3)

    def berth_vessel(self, vessel):
        yield self.env.timeout(random.expovariate(1 / AVG_ARRIVAL_TIME))
        print(f"Vessel {vessel} arrives at time {self.env.now}")
        with self.berths.request() as request:
            yield request
            print(f"Vessel {vessel} berths at time {self.env.now}")
            yield self.env.process(self.unload_vessel(vessel))

    def unload_vessel(self, vessel):
        with self.cranes.request() as crane_request:
            yield crane_request
            for i in range(CONTAINERS_PER_VESSEL):
                with self.trucks.request() as truck_request:
                    yield truck_request
                    print(f"Crane starts unloading container {i+1} from vessel {vessel} at time {self.env.now}")
                    yield self.env.timeout(CRANE_MOVE_TIME)
                    self.env.process(self.move_container(vessel, i+1))
            print(f"Vessel {vessel} finished unloading at time {self.env.now}")

    def move_container(self, vessel, container):
        yield self.env.timeout(TRUCK_MOVE_TIME)
        print(f"Truck delivered container {container} from vessel {vessel} at time {self.env.now}")

def vessel_generator(env, terminal):
    vessel_count = 0
    while True:
        vessel_count += 1
        env.process(terminal.berth_vessel(vessel_count))
        yield env.timeout(random.expovariate(1 / AVG_ARRIVAL_TIME))

# Setup and start the simulation
print("Starting container terminal simulation")
env = simpy.Environment()
terminal = ContainerTerminal(env)
env.process(vessel_generator(env, terminal))

# Execute the simulation
env.run(until=SIMULATION_TIME)
print("Simulation finished")
