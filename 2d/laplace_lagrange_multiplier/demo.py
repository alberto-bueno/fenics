"""
Solve

    Laplace(u) = 0 in [0,1]x[0,1]

with 

    u = x^2 - y^2 on the boundary
We use Lagrange multipliers to implement dirichlet bc. The stress on the boundary is computed by a post-processing step in the end. The scheme is explained in

Gunzburger and Hou
TREATING INHOMOGENEOUS ESSENTIAL BOUNDARY CONDITIONS IN FINITE ELEMENT METHODS AND THE CALCULATION OF BOUNDARY STRESSES
SIAM J. Num. Anal., vol. 20, no. 2, pp. 390-424, April 1992
"""
from scipy.sparse.linalg import cg
from dolfin import *

parameters.linear_algebra_backend = "Eigen"

class boundary(SubDomain):
   def inside(self,x,on_boundary):
      return on_boundary


degree = 1
n = 50
mesh = UnitSquareMesh(n,n)
V = FunctionSpace(mesh, 'CG', degree)

u = TrialFunction(V)
v = TestFunction(V)

ubc = Function(V)
uexact = Expression("x[0]*x[0] - x[1]*x[1]",degree=degree)

# Project boundary condition
M = assemble(u*v*ds)
b = assemble(uexact*v*ds)
bd = boundary()
bc = DirichletBC(V, ubc, bd)
binds = bc.get_boundary_values().keys()
M = as_backend_type(M).sparray()
M = M[binds,:][:,binds]
rhs = b[binds]

x,info = cg(M, rhs)
ubc.vector().zero()
ubc.vector()[binds] = x

# Solve
a = inner(grad(u), grad(v))*dx
L = Constant(0)*v*dx
u = Function(V)
solve(a==L, u, bc)
File("sol.pvd") << u

# compute boundary stress du/dn
a = inner(grad(u), grad(v))*dx
b = assemble(a-L)
b = b[binds]
tau,info = cg(M, b)
stress = Function(V)
stress.vector().zero()
stress.vector()[binds] = tau
File("stress.pvd") << stress
