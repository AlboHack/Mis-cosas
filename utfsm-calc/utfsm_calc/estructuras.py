"""Análisis de pórticos planos. Convención: giro antihorario +, w hacia +z (arriba).
N > 0 tracción. Unidades consistentes a elección (Tonf, m)."""
import numpy as np
def portico(nudos, elems, apoyos, cargas_nudo, resortes={}, extra_dofs=0):
    """Rigidez directa de un pórtico plano.

    nudos: {nombre: (x, z)}
    elems: [dict(i, j, E, A, I, q=0, hinge_end=None|'i'|'j', kappa0=0)]; q local, + hacia +w local;
           kappa0 > 0 si la fibra inferior se alarga (gradiente térmico).
    apoyos: {nudo: [gdl restringidos]} con 0 = u, 1 = w, 2 = theta. Ej.: {'A': [0, 1, 2]}.
    cargas_nudo: {nudo: (Fx, Fz, M)}.  resortes: {(nudo, gdl): k}.
    extra_dofs: número de extremos con rótula (comparar_portico lo calcula solo).
    Devuelve (U, R): U[n] = (u, w, theta), R[n] = (Rx, Rz, M); giro y momento antihorario +.
    """
    # nudos: {n:(x,z)}; elems: lista de dict(i,j,E,A,I,q=0,hinge_end=None,kappa0=0)
    names=list(nudos); idx={n:3*k for k,n in enumerate(names)}
    nd=3*len(names)+extra_dofs; K=np.zeros((nd,nd)); F=np.zeros(nd); extra=3*len(names)
    for e in elems:
        (x1,z1),(x2,z2)=nudos[e['i']],nudos[e['j']]; L=np.hypot(x2-x1,z2-z1)
        c,s=(x2-x1)/L,(z2-z1)/L; EA,EI=e['E']*e['A'],e['E']*e['I']
        kl=np.array([[EA/L,0,0,-EA/L,0,0],[0,12*EI/L**3,6*EI/L**2,0,-12*EI/L**3,6*EI/L**2],
                     [0,6*EI/L**2,4*EI/L,0,-6*EI/L**2,2*EI/L],[-EA/L,0,0,EA/L,0,0],
                     [0,-12*EI/L**3,-6*EI/L**2,0,12*EI/L**3,-6*EI/L**2],[0,6*EI/L**2,2*EI/L,0,-6*EI/L**2,4*EI/L]])
        r=np.array([[c,s,0],[-s,c,0],[0,0,1]]); T=np.kron(np.eye(2),r)
        d=[idx[e['i']],idx[e['i']]+1,idx[e['i']]+2,idx[e['j']],idx[e['j']]+1,idx[e['j']]+2]
        if e.get('hinge_end')=='j': d[5]=extra; extra+=1
        if e.get('hinge_end')=='i': d[2]=extra; extra+=1
        K[np.ix_(d,d)]+=T.T@kl@T
        q=e.get('q',0)  # carga uniforme local perpendicular (+ hacia +w local)
        fl=np.array([0,q*L/2,q*L**2/12,0,q*L/2,-q*L**2/12])
        k0=e.get('kappa0',0); fl+=np.array([0,0,-EI*k0,0,0,EI*k0])
        F[d]+=T.T@fl
    for n,(fx,fz,m) in cargas_nudo.items(): F[idx[n]:idx[n]+3]+=[fx,fz,m]
    for (n,dof),k in resortes.items(): K[idx[n]+dof,idx[n]+dof]+=k
    fijos=[idx[n]+dof for n,dofs in apoyos.items() for dof in dofs]
    libres=[k for k in range(nd) if k not in fijos]
    U=np.zeros(nd); U[libres]=np.linalg.solve(K[np.ix_(libres,libres)],F[libres])
    R=K@U-F
    return {n:U[idx[n]:idx[n]+3] for n in names},{n:R[idx[n]:idx[n]+3] for n in apoyos}


def portico_pynite(nudos, elems, apoyos, cargas_nudo, resortes={}):
    """Mismo modelo que `portico`, resuelto con Pynite (código independiente).
    Devuelve desplazamientos {n: (u, w, theta)} y reacciones {n: (Rx, Rz, M)}."""
    from Pynite import FEModel3D
    m = FEModel3D()
    for n, (x, z) in nudos.items():
        m.add_node(n, x, z, 0)
    sop = {n: [False] * 6 for n in nudos}
    for n in nudos:
        sop[n][2] = sop[n][3] = sop[n][4] = True          # fuera del plano
    mapa = {0: 0, 1: 1, 2: 5}                              # u->DX, w->DY, theta->RZ
    for n, dofs in apoyos.items():
        for d in dofs:
            sop[n][mapa[d]] = True
    for n, s in sop.items():
        m.def_support(n, *s)
    for k, e in enumerate(elems):
        mat, sec, nom = f"M{k}", f"S{k}", f"E{k}"
        m.add_material(mat, e['E'], e['E'] / 2.6, 0.3, 1.0)
        m.add_section(sec, e['A'], 1.0, e['I'], 1.0)
        m.add_member(nom, e['i'], e['j'], mat, sec)
        if e.get('hinge_end') == 'j':
            m.def_releases(nom, Rzj=True)
        if e.get('hinge_end') == 'i':
            m.def_releases(nom, Rzi=True)
        if e.get('q', 0):
            m.add_member_dist_load(nom, 'Fy', e['q'], e['q'])   # local, mismo signo que el núcleo
        if e.get('kappa0', 0):
            raise NotImplementedError("gradiente térmico: usar solo `portico`")
    for n, (fx, fz, mz) in cargas_nudo.items():
        for d, v in (('FX', fx), ('FY', fz), ('MZ', mz)):
            if v:
                m.add_node_load(n, d, v)
    nombres = {0: 'DX', 1: 'DY', 2: 'RZ'}
    for (n, d), k in resortes.items():
        m.def_support_spring(n, nombres[d], k)
    m.analyze()
    c = 'Combo 1'
    U = {n: (m.nodes[n].DX[c], m.nodes[n].DY[c], m.nodes[n].RZ[c]) for n in nudos}
    R = {n: (m.nodes[n].RxnFX[c], m.nodes[n].RxnFY[c], m.nodes[n].RxnMZ[c]) for n in apoyos}
    return U, R


def comparar_portico(nudos, elems, apoyos, cargas_nudo, resortes={}):
    """Resuelve con el núcleo y con Pynite; imprime tabla y devuelve el máximo error relativo."""
    extra = sum(1 for e in elems if e.get('hinge_end'))
    U1, R1 = portico(nudos, elems, apoyos, cargas_nudo, resortes, extra)
    U2, R2 = portico_pynite(nudos, elems, apoyos, cargas_nudo, resortes)
    peor = 0.0
    print(f"{'nudo':>5} {'gdl':>4} {'nucleo':>14} {'pynite':>14} {'err %':>8}")
    for n in nudos:
        for d, nom in enumerate(('u', 'w', 'th')):
            a, b = U1[n][d], U2[n][d]
            err = abs(a - b) / abs(a) * 100 if abs(a) > 1e-12 else float('nan')
            if err == err:
                peor = max(peor, err)
            print(f"{n:>5} {nom:>4} {a:14.6e} {b:14.6e} {err:8.4f}")
    return peor
