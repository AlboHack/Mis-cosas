"""Pruebas sin red: búsqueda de claves, minutos, puntaje y Markdown."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import buscar_videos as bv  # noqa: E402

CLAVES = bv.parsear_claves("control volume, angular momentum, sprinkler, torque, r x V|r cross V, Euler turbomachine")
SEG = [
    {"start": 0.0, "text": "Today we apply the control"},
    {"start": 4.5, "text": "volume form of angular momentum"},
    {"start": 65.0, "text": "to a lawn sprinkler. The torque is"},
    {"start": 130.0, "text": "the integral of R cross V times the mass flux"},
    {"start": 200.0, "text": "again, the torque on the sprinkler"},
]


def test_parsear_claves_con_alias():
    assert CLAVES[4] == ["r x V", "r cross V"]
    assert len(CLAVES) == 6


def test_normalizar_quita_tildes_y_signos():
    assert bv.normalizar("Momentum ANGULAR, r×V — ¿volumen?") == "momentum angular r v volumen"
    assert bv.normalizar("Ecuación de Euler") == "ecuacion de euler"


def test_clave_partida_entre_segmentos_toma_el_inicio():
    h = bv.buscar_en_transcripcion(SEG, CLAVES)
    assert h["control volume"]["t"] == 0.0  # "control" | "volume" en dos segmentos


def test_minuto_y_conteo():
    h = bv.buscar_en_transcripcion(SEG, CLAVES)
    assert h["angular momentum"]["t"] == 4.5
    assert h["sprinkler"] == {"t": 65.0, "veces": 2}
    assert h["torque"]["veces"] == 2
    assert h["r x V"]["t"] == 130.0  # hallado por el alias
    assert "Euler turbomachine" not in h


def test_no_coincide_dentro_de_otra_palabra():
    h = bv.buscar_en_transcripcion([{"start": 0, "text": "torques sprinklers"}], [["torque"], ["sprinkler"]])
    assert h == {}


def test_mmss():
    assert bv.mmss(65) == "01:05"
    assert bv.mmss(3725) == "1:02:05"


def test_puntaje_y_orden():
    a = bv.Video(id="a", titulo="Sprinkler", transcripcion=SEG, vistas=10)
    b = bv.Video(id="b", titulo="Euler turbomachine equation", descripcion="torque",
                 capitulos=[{"title": "Control volume", "start_time": 30}], vistas=999)
    c = bv.Video(id="c", titulo="Otra cosa", vistas=10**6)
    for v in (a, b, c):
        bv.puntuar(v, CLAVES)
    assert a.puntaje == round(5 / 6, 3)          # 5 claves con minuto
    assert b.puntaje == round((1 + 0.5 + 0.5) / 6, 3)  # capítulo + 2 en título/descripción
    assert c.puntaje == 0
    assert [v.id for v in bv.ordenar([c, b, a])] == ["a", "b", "c"]


def test_markdown_enlaza_al_minuto_y_marca_sin_transcripcion():
    a = bv.Video(id="abc", titulo="RTT | sprinkler", canal="X", duracion=600, transcripcion=SEG,
                 transcripcion_idioma="en", transcripcion_tipo="manual")
    b = bv.Video(id="def", titulo="Sin subs", transcripcion_tipo="sin_transcripcion",
                 errores=["transcripción: TranscriptsDisabled"])
    for v in (a, b):
        bv.puntuar(v, CLAVES)
    md = bv.a_markdown("tema", CLAVES, [a, b])
    assert "https://www.youtube.com/watch?v=abc&t=65s" in md
    assert "RTT / sprinkler" in md  # el '|' no rompe la tabla
    assert "| sin transcripción |" in md
    assert "Aviso: transcripción: TranscriptsDisabled" in md


# ---------------------------------------------------------------- v2: filtro, rareza, extracto

def _clase(**kw):
    """Video de 10 min que pasa la compuerta: 1295 palabras (129.5 ppm) con 10 de derivación."""
    texto = ("we assume steady flow therefore " * 5 + "word " * 1270).split()
    seg = [{"start": 6.0 * i, "text": " ".join(texto[13 * i:13 * i + 13])} for i in range(100)]
    base = dict(id="x", titulo="Lesson 5", canal="Prof", duracion=600, transcripcion=seg,
                transcripcion_idioma="en", transcripcion_tipo="automatica")
    base.update(kw)
    return bv.Video(**base)


def test_compuerta_motivos():
    casos = {
        "sin transcripción en o es": dict(transcripcion=[]),
        "dura menos de 3 min": dict(duracion=150),
        "short o en vivo": dict(live_status="is_live"),
    }
    for motivo, kw in casos.items():
        v = _clase(**kw)
        bv.calcular_senales(v)
        assert v.compuerta == motivo and v.filtro == 0
    lento = _clase(duracion=1800)  # 1295 palabras en 30 min = 43 ppm
    bv.calcular_senales(lento)
    assert lento.compuerta.startswith("habla 43 ppm")


def test_derivacion_e_institucional_suman():
    v = _clase(puntaje=0.6)
    bv.calcular_senales(v)
    assert v.compuerta == ""
    assert v.deriv_n == 10 and v.deriv_por_mil == round(10000 / 1295, 2)
    assert v.institucional == "lesson"
    assert v.filtro == 3


def test_institucional_codigo_de_ramo_y_no_curso():
    assert bv.evidencia_institucional("Joseph Feser", "MEEG331 Ch4 12: RTT", "") == "MEEG331"
    assert bv.evidencia_institucional("IngStark", "Ecuación de cantidad de movimiento",
                                      "Compra mi curso completo https://www.lesson.com/x") == ""
    assert bv.evidencia_institucional("Miguel Jované", "Mecánica de fluidos II - Módulo 8c", "") == "modulo 8c"


def test_rareza_contra_calculo_a_mano():
    import math
    a = bv.Video(id="a", en_transcripcion={"t1": {"t": 0, "veces": 3}, "t2": {"t": 5, "veces": 1}})
    b = bv.Video(id="b", en_transcripcion={"t1": {"t": 0, "veces": 1}})
    idf = bv.aplicar_rareza([a, b], [["t1"], ["t2"]])
    assert idf == {"t1": 0.0, "t2": math.log(2)}  # t1 en los dos videos no distingue
    assert a.rareza == round(math.log(2) * math.log(2) / math.log(2), 3) and b.rareza == 0.0


def test_seleccion_excluye_compuerta_y_respeta_similitud():
    vs = [bv.Video(id=i, puntaje=p, filtro=f, compuerta=c) for i, p, f, c in
          [("a", 0.9, 2, ""), ("b", 0.5, 3, ""), ("c", 0.8, 2, ""), ("d", 1.0, 3, "dura menos de 3 min")]]
    assert [v.id for v in bv.seleccionar(vs, k=2)] == ["b", "a"]


def test_fragmentos_tope_y_sin_traslape():
    en = {f"t{i}": {"t": 100.0 + 40 * i, "veces": 1} for i in range(8)}  # cada 40 s: ventanas de 60 s chocan
    en["intro"] = {"t": 20.0, "veces": 1}
    v = bv.Video(id="v", en_transcripcion=en)
    idf = {t: 1.0 for t in en}
    fr = bv.fragmentos(v, idf)
    assert len(fr) <= bv.MAX_FRAGMENTOS
    assert all(ini >= bv.INTRO_S for _, ini, _ in fr)  # nada pisa la intro
    tramos = sorted((ini, fin) for _, ini, fin in fr)
    assert all(b0 <= a1 for (_, b0), (a1, _) in zip(tramos, tramos[1:]))


def test_fragmentos_prefieren_lo_raro():
    en = {"comun": {"t": 200.0, "veces": 9}, "raro": {"t": 210.0, "veces": 1}}
    fr = bv.fragmentos(bv.Video(id="v", en_transcripcion=en), {"comun": 0.1, "raro": 2.0})
    assert [t for t, _, _ in fr] == ["raro"]


def test_extracto_incluye_intro_fragmento_y_excluidos():
    v = _clase(puntaje=0.6, en_transcripcion={"steady": {"t": 300.0, "veces": 5}})
    fuera = bv.Video(id="z", titulo="Corto", compuerta="dura menos de 3 min")
    md = bv.a_extracto("tema", [["steady"]], [v], {"steady": 1.0}, [fuera])
    assert "**[00:00–01:30] inicio:**" in md
    assert "&t=270s" in md
    assert "Corto](https://www.youtube.com/watch?v=z): dura menos de 3 min" in md


def test_desde_json_sin_red(tmp_path):
    import json
    v = _clase(id="abc", titulo="Lesson on steady flow")
    datos = {"videos": [bv.asdict(v) | {"url": v.url}]}
    (tmp_path / "in.json").write_text(json.dumps(datos), encoding="utf-8")
    rc = bv.main(["steady flow", "--tema-es", "flujo permanente", "--terminos", "steady|permanente",
                  "--desde-json", str(tmp_path / "in.json"), "--salida", str(tmp_path / "out")])
    assert rc == 0
    ext = (tmp_path / "out" / "steady_flow_extracto.md").read_text(encoding="utf-8")
    assert "## 1. Lesson on steady flow" in ext


# ---------------------------------------------------------------- caché y corte por bloqueo

def test_cache_solo_guarda_videos_con_transcripcion(tmp_path):
    import json
    con = bv.asdict(_clase(id="a"))
    sin = bv.asdict(bv.Video(id="b", titulo="sin subs"))
    (tmp_path / "r.json").write_text(json.dumps({"videos": [con, sin]}), encoding="utf-8")
    (tmp_path / "roto.json").write_text("{no es json", encoding="utf-8")
    cache = bv.cargar_cache(tmp_path)
    assert list(cache) == ["a"] and cache["a"]["transcripcion"]


def _red_falsa(monkeypatch, ids, bloquea):
    """Reemplaza YouTube: la búsqueda entrega `ids`; la transcripción falla con IpBlocked si `bloquea`."""
    import types
    pedidos = []
    monkeypatch.setitem(sys.modules, "youtube_transcript_api",
                        types.SimpleNamespace(YouTubeTranscriptApi=lambda: None))
    monkeypatch.setattr(bv, "buscar", lambda consulta, n: [{"id": i, "title": i} for i in ids])
    monkeypatch.setattr(bv, "completar_metadatos", lambda v: None)
    monkeypatch.setattr(bv.time, "sleep", lambda s: None)

    def transcribir(v, api):
        pedidos.append(v.id)
        if bloquea:
            v.transcripcion_tipo = "sin_transcripcion"
            v.errores.append("transcripción: IpBlocked")
    monkeypatch.setattr(bv, "descargar_transcripcion", transcribir)
    return pedidos


def test_corta_tras_tres_bloqueos_seguidos(monkeypatch, tmp_path):
    pedidos = _red_falsa(monkeypatch, [f"v{i}" for i in range(10)], bloquea=True)
    rc = bv.main(["t", "--tema-es", "t", "--terminos", "x", "--salida", str(tmp_path), "--cache", ""])
    assert rc == 2 and len(pedidos) == bv.CORTE_BLOQUEOS
    ext = (tmp_path / "t_extracto.md").read_text(encoding="utf-8")
    assert "Ningún video pasó la compuerta." in ext and "10 de 10 fallaron por bloqueo" in ext


def test_cache_evita_pedir_de_nuevo(monkeypatch, tmp_path):
    import json
    (tmp_path / "cache").mkdir()
    previo = bv.asdict(_clase(id="v0", titulo="Lesson cacheada"))
    (tmp_path / "cache" / "r.json").write_text(json.dumps({"videos": [previo]}), encoding="utf-8")
    pedidos = _red_falsa(monkeypatch, ["v0", "v1"], bloquea=False)
    rc = bv.main(["t", "--tema-es", "t", "--terminos", "steady", "--salida", str(tmp_path / "out"),
                  "--cache", str(tmp_path / "cache")])
    assert rc == 0 and pedidos == ["v1"]
    assert "Lesson cacheada" in (tmp_path / "out" / "t_extracto.md").read_text(encoding="utf-8")
