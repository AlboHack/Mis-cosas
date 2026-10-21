"""Salidas LaTeX coherentes con latex-utfsm (babel es-nodecimaldot: punto decimal)."""
import re


def hc_setup():
    """Configura handcalcs para documentos (equation*, punto decimal). Devuelve el decorador."""
    import handcalcs
    from handcalcs.decorator import handcalc
    handcalcs.set_option("latex_block_start", r"\begin{equation*}")
    handcalcs.set_option("latex_block_end", r"\end{equation*}")
    return handcalc


def tabla_comparacion(filas, caption="", label="", cifras=4):
    """filas: [(nombre, teorico, software)]. Error relativo con '---' si teorico == 0."""
    out = [r"\begin{table}[htbp]", r"\centering",
           rf"\begin{{tabular}}{{l S[table-format=-1.{cifras}e-1] S[table-format=-1.{cifras}e-1] S[table-format=2.3]}}",
           r"\toprule", r"Magnitud & {Teórico} & {Software} & {Error [\%]} \\", r"\midrule"]
    for n, a, b in filas:
        e = "{---}" if a == 0 else f"{abs(b - a) / abs(a) * 100:.3f}"
        out.append(f"{n} & {a:.{cifras}e} & {b:.{cifras}e} & {e} \\\\")
    out += [r"\bottomrule", r"\end{tabular}"]
    if caption:
        out.append(rf"\caption{{{caption}}}")
    if label:
        out.append(rf"\label{{{label}}}")
    out.append(r"\end{table}")
    return "\n".join(out)


def pendientes(ruta_tex):
    """Lista (línea, macro, texto) de \\pend y \\completar{...} en un .tex."""
    res = []
    for i, l in enumerate(open(ruta_tex, encoding="utf-8"), 1):
        for m in re.finditer(r"\\completar\{([^}]*)\}|\\pend\b", l):
            res.append((i, "completar" if m.group(1) is not None else "pend", (m.group(1) or l.strip())[:80]))
    return res
