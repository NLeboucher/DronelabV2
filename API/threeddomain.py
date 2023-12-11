import sympy as sp
from  sympy.solvers.inequalities import reduce_rational_inequalities
from sympy import solve_univariate_inequality, Symbol, sin, Interval, S
from sympy.solvers.inequalities import reduce_rational_inequalities
from sympy import Poly
from sympy.abc import x
class ThreeDDomain:
    def __init__(self, equations):
        self.equations = equations
        self.variables = set()
        self.symbols = []
        self.construct_domain()

    def construct_domain(self):
        for equation in self.equations:
            expr = sp.sympify(equation)
            variables = [Symbol(str(symbol)) for symbol in expr.free_symbols]
            self.variables.update(variables)
            self.symbols.append(expr)

    def simplify_equations(self):
        simplified_eqs = reduce_rational_inequalities(self.equations, self.variables)
        return [str(eq) for eq in simplified_eqs]

    def get_domain(self):
        simplified_eqs = self.simplify_equations()
        return " and ".join(simplified_eqs)

# Example usage:
equations_3d = ['2*x + 2*y - z < 0', 'x + 2*y + z < 0', 'x - y + z < 0']
room_domain = ThreeDDomain(equations_3d)
simplified_domain = room_domain.get_domain()
print("Simplified 3D Domain:", simplified_domain)
