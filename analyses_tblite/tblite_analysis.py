""" The analysis file for exploring different dynamics of the tblite module """
import time

from pandas import DateOffset

from tlo import Simulation, Date
from tlo.methods import tblite

start_date = Date(2010, 1, 1)

start_time = time.time()  # start timing the simulation


def simulation_object() -> Simulation:
    # create a simulation object.
    sim = Simulation(start_date=start_date, seed=0, show_progress_bar=True)
    # register all required modules. We are only registering TbLite module, but we can also add demography if we have
    # time
    sim.register(tblite.TbLite())
    return sim


def run_with_default_parameters() -> None:
    """ run simulation with default parameters """
    sim = simulation_object()
    sim.make_initial_population(n=1000)
    # run simulation for 1 year
    sim.simulate(end_date=start_date + DateOffset(months=12))


def run_with_increased_infection_probability() -> None:
    """ increase the tb infection probability to 0.5(50%) and re-run the model """
    sim = simulation_object()
    sim.make_initial_population(n=1000)
    sim.modules['TbLite'].parameters['p_infection'] = 0.5
    # run simulation for 1 year
    sim.simulate(end_date=start_date + DateOffset(months=12))


if __name__ == '__main__':
    """ run simulation with different values for tb infection probability """
    run_with_default_parameters()
    run_with_increased_infection_probability()
