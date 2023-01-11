from parameters import *
from pyscipopt import SCIP_PARAMSETTING
from time import time
from create_model import create_model



def iterative_refinement(max_iterations=50,time_limit=10000, n_years=20, verbose=True, full_log=False, new_params = []):
    """
    Iteratively increases the number of maintenance variables around the time periods where maintenance was scheduled in the previous iteration.
    Stops when improvement is less than 1%.
    """

    # Initializing the maintenance periods
    local_ttmax = n_years*ttmax/Tmax
    oil_periodicity = 9
    cs_periodicity = 12
    ops_periodicity = 16
    winding_periodicity = 30

    winding_periods = [t*local_ttmax/n_years*winding_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*winding_periodicity <= local_ttmax] + [float("inf")] 
    ops_periods = [t*local_ttmax/n_years*ops_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*ops_periodicity <= local_ttmax] + winding_periods 
    oil_periods = [t*local_ttmax/n_years*oil_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*oil_periodicity <= local_ttmax] + winding_periods +  ops_periods
    cs_periods = [t*local_ttmax/n_years*cs_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*cs_periodicity <= local_ttmax] + winding_periods 
    maintenance_periods = {}
    for i in PTs:
        maintenance_periods[i] = [oil_periods, cs_periods, ops_periods, winding_periods]

    best_sol = None
    best_model = None
    best_obj = -float("inf")
    gap_limit = 0.05

    s = time()
    cur_iteration = 0
    with open("./Results/iterative_refinement_all_iterations.txt", "a+") as file:
        #file.write("Iteration | Objective Value | Dual Bound | Time | Gap\n")

        while time() - s <= time_limit and cur_iteration < max_iterations: # Main loop
            print(cur_iteration)
            cur_iteration += 1
            for pt in PTs:
                for i in range(len(maintenance_periods[pt])):
                    if maintenance_periods[pt][i] == []:
                        maintenance_periods[pt][i] = [n_years+1]
                    maintenance_periods[pt][i] = sorted(list(set(maintenance_periods[pt][i])))

            current_model = create_model(maintenance_periods = maintenance_periods, n_years=n_years, new_params=new_params) 
            current_model.setParam("numerics/epsilon", 10**(-5))
            
            #print(gap_limit)
            current_model.setParam("limits/gap", gap_limit)
            if not full_log:
                current_model.hideOutput()
                current_model.setPresolve(SCIP_PARAMSETTING.OFF)
            #if best_sol:
            #    current_model.addSol(best_sol) # this is breaking the loop, for some reason
            current_model.setParam("limits/time", time_limit-(time()-s))

                
            if best_sol: # giving a jumpstart to get the best solution of previous iteration
                best_model_treated_vars = {}
                for var in best_model.getVars():
                    best_model_treated_vars[var.name] = best_model.getVal(var)

                sol = current_model.createSol()#createPartialSol()
                for var in current_model.getVars():
                    if var.name in best_model_treated_vars:
                        current_model.setSolVal(sol,var,best_model_treated_vars[var.name])
                    else:
                        current_model.setSolVal(sol,var,0) # defaulting untreated maintenance to 0
                """
                for var in best_model.getVars():
                    if True:#"chi" not in var.name: # the indices in chi might create infeasible problems. we need to figure out how to deal with this
                        if "chi" in var.name:
                            # you need to do something with added maintenance
                            var_pt = int(var.name.split(",")[0].split("[")[1])
                            var_time = var.name.split(",")[2][:-1]
                            if (var_pt, var_time) in added_maintenance:
                                current_model.setSolVal(sol,var,best_model.getVal(var))
                            else:
                                current_model.setSolVal(sol,var,0) #  maybe we shouldn't do this
                        else:
                            current_model.setSolVal(sol,var,best_model.getVal(var))
                """
                current_model.addSol(sol)
            current_model.optimize()

            if current_model.getNSols() > 0:
                objective = current_model.getObjVal()
                dual = current_model.getDualbound() 
                gap = current_model.getGap()
                if verbose:
                    print("N. Years %i| Iteration %i | Incumbent %.3f | Time %.3f" % (n_years, cur_iteration, current_model.getObjVal(), time() - s)) # this will give us problems if the model is infeasible, or if it can't find a feasible solution in time
                    #file.write("N. Years %i, Iteration %i | Incumbent %.3f | Time %.3f\n" % (n_years, cur_iteration, current_model.getObjVal(), time() - s))#model.getSolvingTime(), gap))
                    file.write("%i| %i | %.3f | %.3f\n" % (n_years, cur_iteration, current_model.getObjVal(), time() - s))#model.getSolvingTime(), gap))
                    file.flush()
            if gap_limit == 0: # if we are solving the model to optimallity, we are accepting to not increase the maintenance actions
                if not verbose:
                    return [current_model, cur_iteration]
                return current_model
            #best_sol = current_model.getBestSol()
            if current_model.getNSols() == 0:
                print("Infeasible")
                #return False, cur_iteration # we are doing this to save time

                
                if len(winding_periods) >= n_years:
                        return [False, cur_iteration]

                if verbose:
                    print("Need to refine further, it's infeasible.")
                vars = [var for var in current_model.getVars() if "chi" in var.name] # doubling the maintenance possibilities. probably too much           
                
                oil_periodicity = max(1,oil_periodicity//2)
                cs_periodicity = max(1,cs_periodicity//2)
                ops_periodicity = max(1,ops_periodicity//2)
                winding_periodicity = max(1,winding_periodicity//2)

                winding_periods = [t*local_ttmax/n_years*winding_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*winding_periodicity <= local_ttmax] + [float("inf")] 
                ops_periods = [t*local_ttmax/n_years*ops_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*ops_periodicity <= local_ttmax] + winding_periods 
                oil_periods = [t*local_ttmax/n_years*oil_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*oil_periodicity <= local_ttmax] + winding_periods +  ops_periods
                cs_periods = [t*local_ttmax/n_years*cs_periodicity for t in range(1,n_years+1) if t*local_ttmax/n_years*cs_periodicity <= local_ttmax] + winding_periods 
                
                maintenance_periods = {}
                for i in PTs:
                    maintenance_periods[i] = [oil_periods, cs_periods, ops_periods, winding_periods]
                continue
                
            else:
                if current_model.getObjVal() >= best_obj:
                    if (current_model.getObjVal() - best_obj)/best_obj <= 0.01: # if we don't improve 1%, get optimal solution and exit
                        gap_limit = 0
                    best_obj = current_model.getObjVal()
                    best_sol = current_model.getBestSol()
                    best_model = current_model
                else:
                    if time() - s <= time_limit: # if we had a worsening solution and there is still time, it's because we terminated too early due to the gap limit
                        gap_limit = round(gap_limit - 0.01)

                vars = [var for var in current_model.getVars() if "chi" in var.name and current_model.getVal(var) == 1]
                if vars == []: # we should be adding even if maintenance, maybe 
                    break

            added_maintenance = {}
            for var_pt in PTs:
                for i in range(4):
                    added_maintenance[var_pt,components[i].name] = []

            for var in vars: 
                # increase maintenance periods. Different periods may increase differently
                if "Oil" in var.name:
                    i = 0
                elif "Cooling_System" in var.name:
                    i = 1
                elif "OPS" in var.name:
                    i = 2
                else:
                    i = 3

                var_split = var.name.split(",")
                var_pt = int(var_split[0].split("[")[1])
                var_time = int(var_split[2][:-1])

                var_index = maintenance_periods[var_pt][i].index(var_time) # these indices will be short, no need to worry about this
                
                if var_index == len(maintenance_periods[var_pt][i]) - 2: # because of the infinite we have
                    left_midpoint = (maintenance_periods[var_pt][i][var_index-1]+maintenance_periods[var_pt][i][var_index])//2
                    right_midpoint = (local_ttmax+maintenance_periods[var_pt][i][var_index])//2
                else:
                    left_midpoint = (maintenance_periods[var_pt][i][var_index-1]+maintenance_periods[var_pt][i][var_index])//2
                    right_midpoint = (maintenance_periods[var_pt][i][var_index+1]+maintenance_periods[var_pt][i][var_index])//2
        
                if var_index == 0:
                    left_midpoint = (0+maintenance_periods[var_pt][i][var_index])//2 # we need the midpoints to match up with the operational variables, but I think they do
                    right_midpoint = (local_ttmax+maintenance_periods[var_pt][i][var_index])//2
                elif var_index != len(maintenance_periods[var_pt][i]) - 2:
                    right_midpoint = (local_ttmax+maintenance_periods[var_pt][i][var_index])//2

                maintenance_periods[var_pt][i].extend([left_midpoint,right_midpoint])
                added_maintenance[var_pt,components[i].name].extend([left_midpoint,right_midpoint])
                if i == 2:
                    maintenance_periods[var_pt][0].extend([left_midpoint,right_midpoint]) # oil has to be maintained if OPS is
                    added_maintenance[var_pt,components[0].name].extend([left_midpoint,right_midpoint])
                if i == 3:
                    for j in range(3):
                        maintenance_periods[var_pt][j].extend([left_midpoint,right_midpoint])
                        added_maintenance[var_pt,components[j].name].extend([left_midpoint,right_midpoint])
                maintenance_periods[var_pt][i].sort() # they are small, no need to worry
            

        if not verbose: # this is for testing with multiple instances, where we will average over all of them
            return [best_model, cur_iteration]
        return best_model # not current model, but best model. the final iteration may not be solved to optimality


if __name__ == "__main__":
    iterative_refinement(n_years=11, full_log=True)