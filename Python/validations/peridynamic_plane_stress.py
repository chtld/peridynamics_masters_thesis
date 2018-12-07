from peridynamic_neighbor_data import *
from peridynamic_stiffness import*
from peridynamic_boundary_conditions import *
from peridynamic_materials import *
from fenics import *
import mshr
import timeit as tm
from peridynamic_infl_fun import *

def solve_peridynamic_bar(horizon, m=mesh, npts=15, material='steel', omega_fun=None, plot_=False, force=-5e8):
    """
    solves the peridynamic bar with a specified load

    """

    print('horizon value: %4.3f\n'%horizon)
    #m = rectangle_mesh(Point(0,0), Point(3,1), numptsX=20, numptsY=10)
    #m = rectangle_mesh_with_hole(npts=npts)
    
    #establish the influence function 
    #omega_fun = unit_infl_fun

    cell_cent = get_cell_centroids(m)
    cell_vol = get_cell_volumes(m)
    purtub_fact = 1e-6
    dim = np.shape(cell_cent[0])[0]
    
    if material is 'steel':
        E, nu, rho, mu, bulk, gamma = get_steel_properties(dim)
 
    nbr_lst, _, _, mw = peridym_get_neighbor_data(m, horizon, omega_fun)
    
    K = computeK(horizon, cell_vol, nbr_lst, mw, cell_cent, E, nu, mu, bulk, gamma, omega_fun)
    bc_type = {0:'dirichlet', 1:'force'}
    bc_vals = {'dirichlet': 0, 'force': force}
    
    K_bound, fb = peridym_apply_bc(m, K, bc_type, bc_vals, cell_vol)
    
    print("solving the stystem")
    start = tm.default_timer()
    sol = np.linalg.solve(K_bound, fb)
    end = tm.default_timer()
    print("Time taken for solving the system of equation: %4.3f secs" %(end-start))
    u_disp = copy.deepcopy(sol)#
    u_disp = np.reshape(u_disp, (int(len(sol)/dim), dim))
    a, _ = get_peridym_mesh_bounds(m)
    
    node_ids = a[0][0] #normal to x directon
    
    for i, nk in enumerate(node_ids):
        u_disp = np.insert(u_disp, nk, np.zeros(dim, dtype=float), axis=0)
    
    disp_cent = cell_cent + u_disp

    if plot_ is True: 
        x, y = cell_cent.T
        plt.figure()
        plt.scatter(x,y, s=300, color='r', marker='o', alpha=0.1, label='original configuration')
        x,y = (cell_cent + 20*u_disp).T
        plt.scatter(x,y, s=300, color='b', marker='o', alpha=0.6, label='horizon='+str(horizon))
        #plt.ylim(-0.5, 1.5)
        plt.legend()
        plt.title("influence function:"+str(omega_fun))
        plt.show(block=False)
    

    return K, K_bound, disp_cent, u_disp
