import numpy as np
import numpy.linalg as la
# import matplotlib.pyplot as plt
# from matplotlib.patches import Ellipse
# import matplotlib
# matplotlib.use('Agg')


def mvee(points, tol=0.001):
    """
    Find the minimum volume ellipse.
    Return A, c where the equation for the ellipse given in "center form" is
    (x-c).T * A * (x-c) = 1
    """
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
    print(f'Total number of iterations: {iteration_count}')
    return np.asarray(A), np.squeeze(np.asarray(c))


# def plot_ellipse_and_points(points, center, a, b, angle):
#     fig, ax = plt.subplots()

#     # Plot the points
#     ax.scatter(points[:, 0], points[:, 1], color='blue')

#     # Create and plot the ellipse
#     ellipse = Ellipse(xy=center, width=2*a, height=2*b,
#                       angle=np.degrees(angle), edgecolor='red', fill=False)
#     ax.add_artist(ellipse)

#     # Set the aspect ratio to be equal
#     ax.set_aspect('equal', adjustable='box')

#     plt.savefig('ellipse_plot.png')

#     # Show the plot
#     plt.show()
