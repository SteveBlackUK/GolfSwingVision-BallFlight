import numpy as np
import numpy.linalg as la
from log import logger


def mvee(points, tol=0.001):
    """
    Find the minimum volume ellipse.
    Return A, c where the equation for the ellipse given in "center form" is
    (x-c).T * A * (x-c) = 1
    """

    try: 
        points = np.asmatrix(points)
        
        N, d = points.shape
        Q = np.column_stack((points, np.ones(N))).T
        err = tol+1.0
        u = np.ones(N)/N
        iteration_count = 0  # Add a counter variable

        while err > tol:
            iteration_count += 1  # Increment the counter in each iteration
            X = Q * np.diag(u) * Q.T
            M = np.diag(Q.T * la.inv(X) * Q)
            jdx = np.argmax(M)
            step_size = (M[jdx]-d-1.0)/((d+1)*(M[jdx]-1.0))
            new_u = (1-step_size)*u
            new_u[jdx] += step_size
            err = la.norm(new_u-u)
            u = new_u
        c = u*points
        A = la.inv(points.T*np.diag(u)*points - c.T*c)/d
        # Print the total number of iterations after the loop
        logger.info(f'Total number of iterations: {iteration_count}')
        return np.asarray(A), np.squeeze(np.asarray(c))
    except ValueError as ve:
        logger.error(f"ValueError occurred: {ve}")
        return None, None
    except TypeError as te:
        logger.error(f"TypeError occurred: {te}")
        return None, None
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return None, None

