import json, re, sys, unicodedata
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from buscar_videos import normalizar
d = json.load(open(sys.argv[1]))
TERM = ["control volume","volumen de control","control surface","superficie de control","momentum","cantidad de movimiento",
 "angular momentum","momento angular","torque","par","moment","momento","velocity","velocidad","relative velocity","velocidad relativa",
 "angular velocity","velocidad angular","mass flow","flujo masico","flow rate","caudal","density","densidad","rho","pressure","presion",
 "reynolds transport","transporte de reynolds","conservation","conservacion","steady","permanente","estacionario","incompressible","incompresible",
 "nozzle","boquilla","tobera","jet","chorro","flux","flujo","inertial","inercial","vector","cross product","producto cruz","producto vectorial",
 "radius","radio","omega","newton","force","fuerza","area","normal","outlet","inlet","salida","entrada"]
DERIV = ["integrate","integral","assume","assumption","boundary condition","derive","derivation","therefore","neglect","approximate",
 "simplify","substitute","plug in","solve for","so that","which gives",
 "integramos","integral","suponemos","supongamos","asumimos","hipotesis","condicion de borde","condicion de contorno","derivamos","deducimos",
 "despreciamos","por lo tanto","reemplazamos","sustituimos","despejamos","simplificamos","nos queda"]
EQ = ["equals","is equal to","squared","divided by","times","over","minus","plus","sine","cosine","dot product","cross",
 "igual a","es igual","al cuadrado","dividido","por","menos","mas","seno","coseno","sobre"]
EQ_STRICT = ["equals","is equal to","squared","divided by","minus","sine","cosine","igual a","es igual","al cuadrado","dividido","menos","seno","coseno"]
def cnt(t, L):
    return sum(len(re.findall(r"(?<![a-z0-9])"+re.escape(normalizar(x))+r"(?![a-z0-9])", t)) for x in set(L))
rows=[]
for v in d['videos']:
    seg = v.get('transcripcion') or []
    if isinstance(seg,str): seg=eval(seg)
    dur = float(v['duracion'] or 0); mins = dur/60
    t = " ".join(normalizar(s['text']) for s in seg)
    w = len(t.split())
    r = dict(canal=v['canal'][:22], tit=v['titulo'][:28], min=mins, vistas=int(v['vistas'] or 0), cob=float(v['puntaje']),
             tipo=v['transcripcion_tipo'][:4], idi=v.get('transcripcion_idioma',''))
    if w and mins:
        r.update(wpm=w/mins, term=cnt(t,TERM)/mins, deriv=cnt(t,DERIV)/mins, eq=cnt(t,EQ_STRICT)/mins,
                 term_k=1000*cnt(t,TERM)/w, deriv_k=1000*cnt(t,DERIV)/w, eq_k=1000*cnt(t,EQ_STRICT)/w)
    rows.append(r)
print("| Canal | Título | min | vistas | cob | idi | ppm | term/min | deriv/min | ec/min | term/1000p | deriv/1000p | ec/1000p |")
print("|"+"---|"*13)
for r in rows:
    f=lambda k,fmt="{:.1f}": fmt.format(r[k]) if k in r else "—"
    print(f"| {r['canal']} | {r['tit']} | {r['min']:.1f} | {r['vistas']} | {r['cob']:.2f} | {r['idi'] or '—'} | {f('wpm','{:.0f}')} | {f('term')} | {f('deriv')} | {f('eq')} | {f('term_k','{:.0f}')} | {f('deriv_k')} | {f('eq_k')} |")
