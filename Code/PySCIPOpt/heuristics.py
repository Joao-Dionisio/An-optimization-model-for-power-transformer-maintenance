from parameters import *
from pyscipopt import Model, SCIP_PARAMSETTING
import math
from time import time
from create_model import create_model


def iterative_refinement(max_iterations=50,time_limit=10000, n_years=20, verbose=True, full_log=False, new_params = []):
    """
    Iteratively increases the number of maintenance variables around the time periods where maintenance was scheduled in the previous iteration.
    Stops when improvement is less than 1%.
    """

    # Initializing the maintenance periods
    local_ttmax = n_years*ttmax/Tmax
    
    maintenance_periods = {}
    if n_years <= 3:
        for k in components:
            maintenance_periods[k.name]=[0]
    else:
        for k in components:
            maintenance_periods[k.name] = [(local_ttmax/n_years)*(j*(n_years//4)) for j in range(1,4)]

    best_sol = None
    best_model = None
    best_obj = -float("inf")
    gap_limit = 0.0

    s = time()
    cur_iteration = 0
    with open("./Results/iterative_refinement_all_iterations.txt", "a+") as file:

        while time() - s <= time_limit and cur_iteration < max_iterations: # Main loop
            cur_iteration += 1

            current_model = create_model(maintenance_periods = maintenance_periods, n_years=n_years, new_params=new_params) 
            current_model.setParam("numerics/epsilon", 10**(-5))
            
            current_model.setParam("limits/gap", gap_limit)
            if not full_log:
                current_model.hideOutput()

            current_model.setParam("limits/time", time_limit-(time()-s))
                
            if best_sol: # giving a jumpstart to get the best solution of previous iteration
                best_model_treated_vars = {}
                for var in best_model.getVars():
                    best_model_treated_vars[var.name] = best_model.getVal(var)

                sol = current_model.createSol()
                for var in current_model.getVars():
                    if var.name in best_model_treated_vars:
                        current_model.setSolVal(sol,var,best_model_treated_vars[var.name])
                    else:
                        current_model.setSolVal(sol,var,0) # the only added variables are maintenance variables. To preserve the previous solution, they are set to 0 

                current_model.addSol(sol)

            current_model.hideOutput(False)
            current_model.optimize()

            vars = [] # scheduled maintenance. Need to be careful with infeasible models
            if current_model.getNSols() > 0:
                if current_model.getObjVal() >= best_obj:
                    if (current_model.getObjVal() - best_obj)/best_obj <= 0.01: # if we don't improve 1%, get optimal solution and exit
                        gap_limit = 0
                    best_obj = current_model.getObjVal()
                    best_sol = current_model.getBestSol()
                    best_model = current_model

                if n_years <= 3: # we are assuming that no maintenance is required for these years
                    if not verbose: 
                        return [best_model, cur_iteration]
                    return best_model 

                vars = [var for var in current_model.getVars() if "chi" in var.name and current_model.getVal(var) == 1]
                        
            if vars == []: # if no maintenance was scheduled, add more possibilities. Same if model is infeasible
                vars = [var for var in current_model.getVars() if "chi" in var.name]

            added = False # to see current iteration added maintenance possibilities that the previous did not have
            for var in vars: 
                # increase maintenance periods. Different periods may increase differently
                var_split = var.name.split(",") # var.name == "chi[1,"OPS",2]", for example
                var_name = var_split[0].split("[")[1]
                var_time = int(var_split[1][:-1])

                var_index = maintenance_periods[var_name].index(var_time) # these indices will be short, no need to worry 
                
                if var_index == 0:
                    left_midpoint = maintenance_periods[var_name][0]//2
                    right_midpoint = (maintenance_periods[var_name][0]+maintenance_periods[var_name][1])//2
                elif var_index == len(maintenance_periods[var_name]) - 1: 
                    left_midpoint = (maintenance_periods[var_name][var_index-1]+maintenance_periods[var_name][var_index])//2
                    right_midpoint = (local_ttmax+maintenance_periods[var_name][var_index])//2
                else:
                    left_midpoint = (maintenance_periods[var_name][var_index-1]+maintenance_periods[var_name][var_index])//2
                    right_midpoint = (maintenance_periods[var_name][var_index+1]+maintenance_periods[var_name][var_index])//2
              
                left_midpoint = (local_ttmax/n_years)*(left_midpoint//(local_ttmax/n_years)) # converting the added maintenance to the first period of each year
                right_midpoint = (local_ttmax/n_years)*(right_midpoint//(local_ttmax/n_years)) # in accordance to the original model

                # checking if these possibilities weren't already found in previous iterations, to prevent unnecessary looping
                if left_midpoint not in maintenance_periods[var_name] or right_midpoint not in maintenance_periods[var_name]:
                    added = True
                maintenance_periods[var_name].extend([left_midpoint,right_midpoint])
                
                # adding maintenance dependencies
                if "OPS" in var_name:
                    maintenance_periods["Oil"].extend([left_midpoint,right_midpoint]) 
                if "Winding" in var_name:
                    for j in components:
                        maintenance_periods[j.name].extend([left_midpoint,right_midpoint])

                # to get proper midpoints in subsequent iterations
                maintenance_periods[var_name] = list(set(maintenance_periods[var_name]))
                maintenance_periods[var_name].sort() # they are small, no need to worry
            if not added:
                if not verbose: 
                    return [best_model, cur_iteration]
                return best_model 

        if not verbose: # this is for testing with multiple instances, where we will average over all of them
            return [best_model, cur_iteration]
        return best_model # not current model, but best model. the final iteration may not be solved to optimality



if __name__ == "__main__":
    iterative_refinement(n_years=10)