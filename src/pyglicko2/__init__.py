from contextlib import contextmanager
from math import pi as π, exp, sqrt, log as ln


__version__ = '0.0.1a0'


SCALE = 173.7178
DEFAULT_R, DEFAULT_RD, DEFAULT_σ = 1500, 350, 0.06
ε = 1e-6
LOSS, DRAW, WIN = 0, 0.5, 1


class System:
    def __init__(self, τ: float = 0.6):
        self.τ = τ


@contextmanager
def system(τ: float = 0.6):
    psys = Player.sys
    Player.sys = System(τ)
    try:
        yield Player.sys
    finally:
        Player.sys = psys


class Player:
    sys = System()

    def __init__(self, r: float = DEFAULT_R, RD: float = DEFAULT_RD, σ: float = DEFAULT_σ):
        self.r, self.RD, self.σ = r, RD, σ
        self.μ, self.φ = (r - DEFAULT_R) / SCALE, self.RD / SCALE
    
    def update(self, players=[], s=[]):
        if not len(players):
            self.φ = φ_star = sqrt(self.φ**2 + self.σ**2)
            return
        g = lambda φ: 1/sqrt(1 + 3*φ**2/π**2)
        E = lambda μ, μ_j, φ_j: 1/(1 + exp(-g(φ_j) * (μ - μ_j)))
        v = sum(g(p.φ)**2 * E(self.μ, p.μ, p.φ) * (1 - E(self.μ, p.μ, p.φ)) for p in players)**-1
        Δ = v * sum(g(p.φ) * (s_j - E(self.μ, p.μ, p.φ)) for p, s_j in zip(players, s, strict=True))
        A = a = ln(self.σ**2)
        f = lambda x: exp(x) * (Δ**2 - self.φ**2 - v - exp(x)) / (2*(self.φ**2 + v + exp(x))**2) - (x - a) / Player.sys.τ**2
        if Δ**2 > self.φ**2 + v:
            B = ln(Δ**2 - self.φ**2 - v)
        else:
            k = 1
            while f(a - k * Player.sys.τ) < 0:
                k += 1
            B = a - k * Player.sys.τ
        f_A, f_B = f(A), f(B)
        while abs(B - A) > ε:
            f_C = f(C := A + (A - B) * f_A / (f_B - f_A))
            if f_C * f_B <= 0:
                A, f_A = B, f_B
            else:
                f_A /= 2
            B, f_B = C, f_C
        self.σ = exp(A/2)
        φ_star = sqrt(self.φ**2 + self.σ**2)
        self.φ = 1/sqrt(1/φ_star**2 + 1/v)
        self.μ += self.φ**2 * sum(g(p.φ) * (s_j - E(self.μ, p.μ, p.φ)) for p, s_j in zip(players, s, strict=True))
        self.r, self.RD = SCALE * self.μ + DEFAULT_R, SCALE * self.φ
    
    def __repr__(self):
        return f'Player(r={self.r}, RD={self.RD}, σ={self.σ})'