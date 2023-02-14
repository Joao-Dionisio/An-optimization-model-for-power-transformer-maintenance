# Cleaning up SCIP results

def remove_headers(file):
    with open(file, "r") as f:
        lines = f.readlines()
    with open(file, "w") as f:
        for index, line in enumerate(lines):
            if line.strip("\n") != "Cannot set feasibility tolerance to small value 1e-12 without GMP - using 1e-10.":
                if index == 0 or line.strip("\n") != " time | node  | left  |LP iter|LP it/n| mem |mdpt |frac |vars |cons |cols |rows |cuts |confs|strbr|  dualbound   | primalbound  |  gap   ": 
                    f.write(line)
    return

def remove_presolve(file):

    with open(file, "r") as f:
        lines = f.readlines()
    with open(file, "w") as f:
        for index, line in enumerate(lines):
            if "(round" not in line:
                #if line.strip("\n") != " time | node  | left  |LP iter|LP it/n| mem |mdpt |frac |vars |cons |cols |rows |cuts |confs|strbr|  dualbound   | primalbound  |  gap   ": 
                if index == 0 or " time |" not in line:
                    f.write(line)
    return

if __name__ == "__main__":
    #remove_presolve("../../Models/PySCIPOpt/Results/iterative_full_log.txt")#nohup_create.out")
    remove_presolve("../../Models/PySCIPOpt/Results/create_50y_log.txt")#nohup_create.out")
