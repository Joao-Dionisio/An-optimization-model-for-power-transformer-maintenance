"""
Bunch of scripts for testing the methods for a varying number of years, with multiple instances
"""

from parameters import *
from time import time as clock
import heuristics
from create_model import create_model
import random


def test_original_model():
    seeds = [2,3,5,7,11,13,17,19,23,29]#,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    all_params = [get_random_parameters(seed=i) for i in seeds]

    with open("./Results/multiple_instances_create_model.txt", "w+") as file:
        file.write("N Years | Objective Value | Time | Gap | Infeasible \n")
        print("N Years | Objective Value | Time | Gap | Infeasible")
        all_values = []
        for cur_year in [2]:#list(range(1, 21)) + [50,100]:
            infeasible_instances = 0
            total_obj = 0
            total_gap = 0
            total_time = 0
            t = 0
            for i in range(len(all_params)):
                new_params = all_params[i]
                model = create_model(n_years=cur_year, new_params=new_params)
                model.setParam("limits/time", 7200)
                model.hideOutput(False)
                model.optimize()
                if model.getNSols() == 0:
                    infeasible_instances+=1
                    continue

                obj = model.getObjVal() # be careful with this
                #dual = model.getDualbound()
                gap = model.getGap()
                time = model.getSolvingTime()
                dual = model.getDualbound()
                
                total_obj+=obj
                total_gap+=gap
                total_time+=time
                all_values.append([obj,gap,time,dual])

            valid_instances = len(seeds)-infeasible_instances
            mean_obj = total_obj/valid_instances
            mean_gap = total_gap/valid_instances
            mean_time = total_time/valid_instances
            print("%i   |   %.3f     | %.3f | %.3f | %i\n" % (cur_year, mean_obj, mean_time, mean_gap, infeasible_instances))
            file.write("%i  |  %.3f     | %.3f | %.3f | %i\n" % ( cur_year, mean_obj, mean_time, mean_gap, infeasible_instances))
            file.flush()   
        print(all_values)
               




def test_iterative_refinement_heuristic():
    seeds = [2,3,5,7,11,13,17,19,23,29]#,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    all_params = [get_random_parameters(seed=i) for i in seeds]
    all_values = []
    with open("./Results/multiple_instances_iterative_refinement.txt", "w+") as file:
        file.write("N Years | Objective Value | Time | Gap | Iterations | Infeasible \n")
        print("N Years | Objective Value | Time | Gap | Iterations | Infeasible")

        for cur_year in list(range(1, 21)) + [50,100]:
            infeasible_instances = 0
            total_obj = 0
            total_gap = 0
            total_time = 0
            total_iterations = 0
            for i in range(len(all_params)):
                new_params = all_params[i]
            

                start = clock()
                model, n_iterations = heuristics.iterative_refinement(new_params=new_params, max_iterations=20, full_log=False, verbose=False, time_limit=7200, n_years=cur_year)

                if not model or model.getNSols() == 0:
                    infeasible_instances+=1
                    continue

                obj = model.getObjVal() # be careful with this
                gap = model.getGap()
                time = clock() - start
                dual = model.getDualbound()
                                
                total_obj+=obj
                total_gap+=gap
                total_time+=time
                total_iterations+=n_iterations
                all_values.append([obj,gap,time,dual])

            valid_instances = len(seeds)-infeasible_instances
            mean_obj = total_obj/valid_instances
            mean_gap = total_gap/valid_instances
            mean_time = total_time/valid_instances
            mean_iterations = total_iterations/valid_instances
            
            print("%i   |   %.3f     | %.3f | %.3f | %.3f | %i\n" % (cur_year, mean_obj, mean_time, mean_gap, mean_iterations, infeasible_instances))
            file.write("%i  |  %.3f     | %.3f | %.3f | %.3f | %i\n" % ( cur_year, mean_obj, mean_time, mean_gap, mean_iterations, infeasible_instances))
            file.flush()  
        print(all_values)
        


def get_random_parameters(seed = 1000000000000066600000000000001):
    """
    Randomizes every parameter in the model. Needs a seed for randomness
    """

    random.seed(seed)
    new_params = [Price, Qmax, load_effect, d_prime, max_cooling_system_cooling, max_oil_cooling, A, B]
    param_bounds = [[Price*0.75,Price*1.5],[Qmax*0.75,Qmax*1.5],[load_effect*0.75,load_effect*1.5], [d_prime*0.99,1],[max_cooling_system_cooling*0.75,max_cooling_system_cooling*1.5],[max_oil_cooling*0.75,max_oil_cooling*1.25],[A*0.75,A*1.25],[B*0.75,B*1.25]]
    
    for param_index in range(len(new_params)):
        lb, ub = param_bounds[param_index]
        new_params[param_index] = random.uniform(lb, ub)
    
    new_demand = {}
    for hour in demand:
        cur_demand = demand[hour]
        new_demand[hour] = random.uniform(cur_demand*0.75, cur_demand*1.5)
    new_params.append(new_demand)

    for component in components:
        old_cost = component.cost
        old_RUL = component.RULmax

        new_cost = random.uniform(old_cost*0.75, old_cost*1.5)
        new_RULmax = random.uniform(old_RUL*0.75, old_RUL*1.5)
        new_params.append(new_cost)
        new_params.append(new_RULmax)        

    return new_params



import sys 
if __name__ == "__main__":
    args = sys.argv
    if args[1] == "original":
        test_original_model()
    elif args[1] == "heuristic":
        test_iterative_refinement_heuristic()
    else:
	    print("Error")
