"""
Math (tm)
"""

def solve(A, b, lsq_row_weights):
    """
    Solves the equation Ax = b,
    using the non-negative least-squares method (scipy.optimize.nnls).

    This works for non-square matrices as well.

    Arguments:
    A:
        The left-hand matrix.
    b:
        The right-hand vector.
    lsq_row_weights:
        If there is no exact solution, the solver minimizes the sum of
        squared errors in each row.
        These weights are multiplied onto the rows to allow weighting
        the rows in a fine-grained way.

    Returns:
        A tuple (x, success, b).
        success is True if an exact solution was found.
        b contains the actual value of Ax.
    """
    from scipy.optimize import nnls
    from numpy import matrix, asarray, diag

    A = matrix(A)
    b = matrix(b).transpose()
    weight_matrix = diag(lsq_row_weights)
    A_weighted = weight_matrix @ A
    b_weighted = asarray((weight_matrix @ b).transpose())[0]

    x, rnorm = nnls(A_weighted, b_weighted)

    return list(x), rnorm < 1e-10, list(asarray(A @ x)[0])
