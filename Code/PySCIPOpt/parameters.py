Tmax  = 20
ttmax = Tmax*24
Price  = 1 
Qmax  = 2 
load_effect  = 24/(ttmax/Tmax)
d_prime = 0.95**(1/(ttmax/Tmax)) # this results in a degradation to 60% after 10y 

max_cooling_system_cooling  = 10 
max_oil_cooling  = 5 

A  = 60 
B  = 0.5 

hs  = {11:	140} 

class Component:
    def __init__(self, name, RULmax, cost, maintenance_duration):
        """
        name:                   Component name as string
        RULmax:                 Component maximum Remaining Useful Life in years
        Cost:                   Component maintenance cost in nr of years to generate component cost 
        maintenance_duration:   Component duration of maintenance in nr of years (must be an integer)
        """

        self.name = name
        self.RULmax = RULmax*ttmax/Tmax
        self.cost = cost*ttmax/Tmax

OPS             = Component("OPS", 35, 1.65, 3)
Cooling_System  = Component("Cooling_System", 25, 0.85, 2)
Oil             = Component("Oil", 12, 0.2, 1)
Winding         = Component("Winding", 50, 12.5, 4)

components = [Oil, Cooling_System, OPS, Winding]

demand = { # Using representative day for the year
    0:	1.05,
    1:	0.83,
    2:	0.75,
    3:	0.64,
    4:	0.7,
    5:	0.64,
    6:	0.7,
    7:	0.83,
    8:	1.4,
    9:	1.4,
    10:	1.36,
    11:	1.28,
    12:	1.39,
    13:	1.39,
    14:	1.25,
    15:	1.28,
    16:	1.29,
    17:	1.58,
    18:	2,
    19:	2,
    20:	2,
    21:	1.8,
    22:	1.67,
    23:	1.42 
}

default_params = [Price, Qmax, load_effect, d_prime, max_cooling_system_cooling, max_oil_cooling, A, B, demand]
for component in components:
    default_params.append(component.cost)
    default_params.append(component.RULmax)
