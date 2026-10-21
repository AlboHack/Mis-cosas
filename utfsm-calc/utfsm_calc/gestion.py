"""CPM y evaluación de flujos (UF)."""
import networkx as nx


def cpm(act):
    """act = {id: (duracion, [predecesoras])}. Devuelve (tabla, ruta_critica, duracion)."""
    G = nx.DiGraph()
    for a, (d, pre) in act.items():
        G.add_node(a, d=d)
        for p in pre:
            G.add_edge(p, a)
    orden = list(nx.topological_sort(G))
    ES, EF = {}, {}
    for a in orden:
        ES[a] = max((EF[p] for p in G.predecessors(a)), default=0)
        EF[a] = ES[a] + act[a][0]
    T = max(EF.values())
    LF, LS = {}, {}
    for a in reversed(orden):
        LF[a] = min((LS[s] for s in G.successors(a)), default=T)
        LS[a] = LF[a] - act[a][0]
    tabla = {a: dict(ES=ES[a], EF=EF[a], LS=LS[a], LF=LF[a], H=LS[a] - ES[a]) for a in orden}
    ruta = [a for a in orden if abs(tabla[a]['H']) < 1e-9]
    return tabla, ruta, T


def vpi(flujos, r, t0=1):
    """Suma explícita sum F_t/(1+r)^t, con t desde t0 (por defecto 1)."""
    return sum(F / (1 + r) ** (t0 + k) for k, F in enumerate(flujos))
