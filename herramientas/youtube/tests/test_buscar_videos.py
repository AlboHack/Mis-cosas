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
