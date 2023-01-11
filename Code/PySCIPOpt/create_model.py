# Translating AMPL model into pySCIPOpt

from pyscipopt import Model, quicksum, exp, log
from parameters import *

def create_model(n_years = Tmax, new_params = None, maintenance_periods = False, total_maintenance=0):

    Tmax = n_years
    ttmax = Tmax*24
    
    model = Model("one_day_non_linear")    
    if new_params:
        # this is needed because we will be changing the parameters from one instance to the next
        global Price
        global Qmax   
        global load_effect
        global d_prime
        global max_cooling_system_cooling
        global max_oil_cooling
        global A
        global B
        global demand
        global Oil
        global Cooling_System
        global OPS
        global Winding
        
        Price, Qmax, load_effect, d_prime, max_cooling_system_cooling, max_oil_cooling, A, B, demand, Oil.cost, Oil.RULmax, Cooling_System.cost, Cooling_System.RULmax, OPS.cost, OPS.RULmax, Winding.cost, Winding.RULmax = new_params

    if not maintenance_periods:
        maintenance_periods = {}
        maintenance_periods = [[i*ttmax//n_years for i in range(1,n_years+1)]]*len(components)

    #### Variable Declaration
    q = {}    
    for i in range(1,ttmax+1):
        q[i] = model.addVar("q[%i]"%i,ub=Qmax, lb=0) 

    real_temp = {} 
    for i in range(1,ttmax+1):
        real_temp[i] = model.addVar("real_temp[%i]"%i, lb=0)
          

    rul = {}
    for component in components:
        for t in range(0,ttmax+1):
            rul[component.name,t] = model.addVar("rul[%s,%i]"%(component.name,t),lb=0,ub=component.RULmax)

    chi = {}
    for index, component in enumerate(components):
        for t in maintenance_periods[index]:
            if t != float("inf"):
                chi[component.name,t] = model.addVar("chi[%s,%i]"%(component.name,t),vtype="B")

    x = {}
    y = {}
    z = {}
    for t in range(Tmax+1):
        x[t] = model.addVar("x[%i]"%(t),vtype="BINARY")
        y[t] = model.addVar("y[%i]"%(t),vtype="BINARY")
        z[t] = model.addVar("z[%i]"%(t),vtype="BINARY")

    #### Objective
    maintenance_cost = model.addVar("obj", lb=0)
    #total_maintenance = 0
    
    for i, k in enumerate(components):
        for t in maintenance_periods[i]:
            if t != float("inf"):
                total_maintenance += k.cost*chi[k.name,t] 

    model.addCons(maintenance_cost >= total_maintenance)
    model.setObjective(quicksum(Price*q[t] for t in range(1,ttmax+1)) - maintenance_cost, "maximize")
   
    ###############
    # Constraints #
    ###############
    
    #### RUL Constraints
    for k in components:
        model.addCons(rul[k.name,0] == k.RULmax)


    oil_index     = 0
    cs_index      = 0
    ops_index     = 0
    winding_index = 0
    for t in range(1,ttmax+1):            
        # This here is to try to only use the maintenance variables on the first period of each year. 
        if t != maintenance_periods[0][oil_index]:
            model.addCons(rul["Oil",t] <= rul["Oil",t-1]*d_prime - real_temp[t]/hs[11])
        else:
            oil_index+=1
            model.addCons(rul["Oil",t] <= rul["Oil",t-1]*d_prime - real_temp[t]/hs[11] + 4*Oil.RULmax*chi["Oil",t])

        if t != maintenance_periods[1][cs_index]:
            model.addCons(rul["Cooling_System",t] <= rul["Cooling_System",t-1]*d_prime - load_effect*q[t]/Qmax)
        else:
            cs_index+=1
            model.addCons(rul["Cooling_System",t] <= rul["Cooling_System",t-1]*d_prime - load_effect*q[t]/Qmax + 3*Cooling_System.RULmax*chi["Cooling_System",t])

        if t != maintenance_periods[2][ops_index]:
            model.addCons(rul["OPS",t] <= rul["OPS",t-1]*d_prime - load_effect*q[t]/Qmax)
        else:
            ops_index+=1
            model.addCons(rul["OPS",t] <= rul["OPS",t-1]*d_prime - load_effect*q[t]/Qmax + 2*OPS.RULmax*chi["OPS",t])

        if t != maintenance_periods[3][winding_index]:
            model.addCons(rul["Winding",t] <= rul["Winding",t-1] - exp(((real_temp[t]-98)/6)*log(2)))
            model.addCons(rul["Winding",t] <= rul["Winding",t-1] - 3.66*exp(((real_temp[t]-98)/6)*log(2)) + y[t//(ttmax/Tmax)]*Winding.RULmax*10)
            model.addCons(rul["Winding",t] <= rul["Winding",t-1] - 10.976*exp(((real_temp[t]-98)/6)*log(2)) + x[t//(ttmax/Tmax)]*Winding.RULmax*10)
        else:
            winding_index+=1
            model.addCons(rul["Winding",t] <= rul["Winding",t-1] - exp(((real_temp[t]-98)/6)*log(2)) + 5*Winding.RULmax*chi["Winding",t])
            model.addCons(rul["Winding",t] <= rul["Winding",t-1] - 3.66*exp(((real_temp[t]-98)/6)*log(2)) + y[t//(ttmax/Tmax)]*Winding.RULmax*10 + 5*Winding.RULmax*chi["Winding",t])
            model.addCons(rul["Winding",t] <= rul["Winding",t-1] - 10.976*exp(((real_temp[t]-98)/6)*log(2)) + x[t//(ttmax/Tmax)]*Winding.RULmax*10 + 5*Winding.RULmax*chi["Winding",t])

                            
    #### Temperature
    for t in range(1,ttmax+1):
        model.addCons(real_temp[t] >= A*exp(B*q[t]) - max_cooling_system_cooling*rul["Cooling_System",t]/Cooling_System.RULmax - max_oil_cooling*rul["Oil",t]/Oil.RULmax) # the oil has a relationship with the temperature that is making the model harder
    
    #### Load Limitations
    for t in range(1,ttmax+1):
        for k in components:
            model.addCons(q[t] <= Qmax*rul[k.name,t]/k.RULmax)

    
    # if False: # with this SCIP still does not detect symmetry 
    for t in range(1,ttmax+1):
        model.addCons(q[t] <= demand[t%(ttmax/Tmax)])

    #### Maintenance Dependencies
    if maintenance_periods[2] != [0]: # If OPS has no maintenance, Winding can't have maintenance, no need for two checks        
        for t in maintenance_periods[2]:
            if t != float("inf"):
                model.addCons(chi["OPS",t] <= chi["Oil",t])   
    
        for t in maintenance_periods[3]:
            for k in components:
                if t != float("inf"):
                    model.addCons(chi["Winding",t] <= chi[k.name,t])

    ops_index = 0
    #### Moisture
    for t in range(0,Tmax+1):
        alpha = rul["OPS",t*(ttmax/Tmax)]/OPS.RULmax
        model.addCons(x[t] >= y[t])
        model.addCons(3*alpha >= y[t] + x[t])    

    return model

if __name__ == "__main__":
    from time import time
    model = create_model(n_years=10)
    model.optimize()
    
    