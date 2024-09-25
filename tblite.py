"""This is a demo module for the modelling short course. It seeks to demonstrate the concept od individual based
modelling """
from pathlib import Path

import pandas as pd

from tlo import Module, Simulation, Parameter, Types, Property, Population
from tlo.events import RegularEvent, PopulationScopeEventMixin


class TbLite(Module):
    """ This is Tb Lite module. It seeks to cover the very basics of individual based modelling. """

    # define a dictionary of parameters this module will use
    PARAMETERS = {
        'p_infection': Parameter(Types.REAL, 'Probability that an uninfected individual becomes infected'),
        'p_cure': Parameter(Types.REAL, 'Probability that an infected individual is cured'),
    }

    # define a dictionary of properties this module will use
    PROPERTIES = {
        'tbl_is_infected': Property(Types.BOOL, 'Current tb status. whether infected or not'),
        'tbl_date_infected': Property(Types.DATE, 'Date of latest tb infection'),
        'tbl_date_cure': Property(Types.DATE, 'Date an infected individual was cured'),
    }

    def __init__(self):
        # this method is included to define all things that should be initialised first
        super().__init__()
        self.incidence_tb = {}
        self.prevalence_tb = {}

    def read_parameters(self, data_folder: str | Path) -> None:
        """ initialise module parameters. Here we are assigning values to all parameters defined at the beginning of
        this module. For this demo module, we will manually assign values to parameters but in the
        Thanzi model we do this by reading from an Excel file containing parameter names and values

        :param data_folder: Path to the folder containing parameter values

        """

        tblite_parameters = self.parameters
        tblite_parameters['p_infection'] = 0.1
        tblite_parameters['p_cure'] = 0.15

    def initialise_population(self, population: Population) -> None:
        """ set the initial state of the population. The state will be update over time

        :param population: all individuals in the model

        """
        df = population.props
        df['tbl_is_infected'] = False
        df['tbl_date_infected'] = pd.NaT
        df['tbl_date_cure'] = pd.NaT

    def initialise_simulation(self, sim: Simulation) -> None:
        """ This is where you should include all things you want to be happening during simulation

        :param sim: simulation object

        """
        # schedule an event to infect people with tb
        sim.schedule_event(TblInfectionEvent(self), date=sim.date + pd.DateOffset(months=1))
        # schedule an event to cure people from tb
        sim.schedule_event(TblCureEvent(self), date=sim.date + pd.DateOffset(months=2))

    def on_birth(self, mother_id: int, child_id: int) -> None:
        """ set properties of a child when they are born. we will do nothing here since we have not included
        labour modules """
        pass

    def on_simulation_end(self) -> None:
        tb_inc_and_prev = pd.DataFrame(index=list(self.incidence_tb.keys()),
                                       data={'incidence': self.incidence_tb.values(),
                                             'prevalence': self.prevalence_tb.values(),
                                             'total_pop': len(self.sim.population.props)})
        print(f'the tb inc and prev is {tb_inc_and_prev}')


class TblInfectionEvent(RegularEvent, PopulationScopeEventMixin):
    """ cause individuals to be infected by Tb. This event will run every month """

    def __init__(self, module: Module) -> None:
        self.repeat = 1
        super().__init__(module, frequency=pd.DateOffset(months=self.repeat))

    def apply(self, population: Population) -> None:
        """ actions that should be applied to the population when this event is triggered """
        df = population.props

        # select individuals to infect. should be those without tb at the present time
        individuals_to_infect = ~df['tbl_is_infected']
        random_selection = self.module.rng.choice([True, False], size=len(individuals_to_infect),
                                                  p=[self.module.parameters['p_infection'],
                                                     1 - self.module.parameters['p_infection']])

        # update the properties of individuals that have been selected for tb infection
        idx_individuals_to_infect = individuals_to_infect.index[random_selection]
        df.loc[idx_individuals_to_infect, 'tbl_is_infected'] = True
        df.loc[idx_individuals_to_infect, 'tbl_date_infected'] = self.sim.date

        # incidence of Tb
        self.module.incidence_tb.update({self.sim.date: len(idx_individuals_to_infect)})
        self.module.prevalence_tb.update({self.sim.date: df.tbl_is_infected.sum()})


class TblCureEvent(RegularEvent, PopulationScopeEventMixin):
    """ cause individuals to recover from Tb. This event will run every month """

    def __init__(self, module: Module) -> None:
        self.repeat = 1
        super().__init__(module, frequency=pd.DateOffset(months=self.repeat))
        self.module = module

    def apply(self, population: Population) -> None:
        """ actions that should be applied to the population when this event is triggered """
        df = population.props

        # select individuals to recover. should be those with tb and infected not less than a month ago
        individuals_to_recover = df.loc[df.tbl_is_infected &
                                        (self.sim.date - pd.DateOffset(months=1) > df.tbl_date_infected)]

        random_selection = self.module.rng.choice([True, False], size=len(individuals_to_recover),
                                                  p=[self.module.parameters['p_cure'],
                                                     1 - self.module.parameters['p_cure']])

        # update the properties of individuals that have been selected for tb cure.
        # they should be well and have a date of recovery
        idx_individuals_to_recover = individuals_to_recover.index[random_selection]
        df.loc[idx_individuals_to_recover, 'tbl_is_infected'] = False
        df.loc[idx_individuals_to_recover, 'tbl_date_cure'] = self.sim.date
