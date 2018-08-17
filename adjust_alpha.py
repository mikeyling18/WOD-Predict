
from scipy.optimize import minimize
import numpy as np
import pandas as pd
from predict import predict_score


def change_alphas(wod_df, old_score, old_error, wod_time):
    num_unique_movements = len(np.unique(wod_df['movement']))
    x0 = wod_df['alpha']                                #old alpha values
    x_init = x0
    reps = wod_df['reps_performed']

    if old_error >= 0.0:
        x0 = x0 + 0.1 * x0
        lower_bound = x0
        upper_bound = x0 + 0.1 * x0
    else:
        lower_bound = x0 - 0.1 * x0
        upper_bound = x0

    bounds = list()

    for i in range(0, len(x0)):
        b = (lower_bound[i], upper_bound[i])
        bounds.append(b)

    temp_df = wod_df.copy()

    def objective(x):
        objective_str = 'abs(' + str(old_score) + ' - ('
        for i in range(0,len(x0)):
            objective_str = objective_str + str(reps[i % num_unique_movements]) + '*' + str(x[i % num_unique_movements]) + '+'
            x[i] = x[i % num_unique_movements]
        objective_str = objective_str[:-1] + '))'
        return eval(objective_str)

    def constraint1(x):
        temp_df['alpha'] = x
        reps_per_movement_df_new_alphas = temp_df
        new_score = predict_score(reps_per_movement_df_new_alphas, wod_time)
        new_error = (new_score - old_score) / old_score
        if old_error >= 0.0:
            return old_error - new_error
        else:
            return new_error - old_error

    def constraint2(x):
        temp_df['alpha'] = x
        reps_per_movement_df_new_alphas = temp_df
        new_score = predict_score(reps_per_movement_df_new_alphas, wod_time)
        new_error = (new_score - old_score) / old_score
        if old_error >= 0.0:
            return new_error
        else:
            return -new_error

    def constraint3(x):
        temp_df['alpha'] = x
        reps_per_movement_df_new_alphas = temp_df
        new_score = predict_score(reps_per_movement_df_new_alphas, wod_time)
        if old_error >= 0.0:
            return old_score - new_score
        else:
            return new_score - old_score

    cons1 = {'type': 'ineq', 'fun': constraint1}
    cons2 = {'type': 'ineq', 'fun': constraint2}
    cons3 = {'type': 'ineq', 'fun': constraint3}
    cons = [cons1]

    z = minimize(objective, x0, method = 'SLSQP', bounds = bounds, constraints = cons)
    new_alphas = z['x']
    alpha_change = x_init - new_alphas
    # x_init = x_init[0:num_unique_movements - 1]
    # new_alphas = new_alphas[0:num_unique_movements - 1]
    print('old alphas: {} \n'
          'new alphas: {} \n'
          'change in alpha: {}'.format(list(x_init[0:num_unique_movements]), new_alphas[0:num_unique_movements], list(alpha_change)))
    return new_alphas