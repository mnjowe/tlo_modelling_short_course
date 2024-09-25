""" The analysis file for exploring different dynamics of the tblite module """
import time
from pathlib import Path

from pandas import DateOffset

from tlo import Simulation, Date
from tlo.methods import tblite

# outputpath = Path('./outputs')
# resources = Path('./resources')

start_date = Date(2010, 1, 1)
sim = Simulation(start_date=start_date, seed=0)
# register all required modules. We are only registering TbLite module, but we can also add demography if we have time
sim.register(tblite.TbLite())

sim.make_initial_population(n=1000)
start_time = time.time()  # start timing the simulation
# run simulation for 1 year
sim.simulate(end_date=start_date + DateOffset(months=12))
end_time = time.time() - start_time  # end timing simulation
print(f'time spent in simulation: {end_time}')  # calculate time taken
