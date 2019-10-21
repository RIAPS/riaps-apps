import logging

# import libs.cplex as cplex
from libs.LinearProgram import LinearProgram

import cplex as cplex
# from LinearProgram import LinearProgram

class LinearProgramCplex(LinearProgram):
  def __init__(self):
    super(LinearProgramCplex, self).__init__()

  def solve(self):
    logging.info("Solving linear program with {} variables and {} constraints...".format(len(self.variables), len(self.constraints)))
    (A, b, c) = self.construct()

    A_cplex = []
    for row in A:
      A_cplex.append([list(range(len(self.variables))), row])

    prob = cplex.Cplex()

    prob.set_log_stream(None)
    #prob.set_error_stream(None)
    #prob.set_warning_stream(None)
    prob.set_results_stream(None)

    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.variables.add(obj=c)
    prob.linear_constraints.add(lin_expr=A_cplex, senses=['L'] * len(self.constraints), rhs=b)
    prob.solve()
    x = prob.solution.get_values()
#    logging.info("Solver output: message = '{}', fun = {}, status = {}".format(result.message, result.fun, result.status))
    solution = {name: x[var] for (name, var) in self.variables.items()}
    objective = prob.solution.get_objective_value()
    return (solution, objective)

if __name__ == "__main__":
  program = LinearProgramCplex()
  program.set_objective({"x1": -1, "x2": -1})
  program.add_constraint({"x1" : 1}, 2)
  program.add_constraint({"x2" : 1}, 1)
  print(program.solve())
