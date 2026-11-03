"""T30: archivos con datos de terceros (listas de notas o de curso) no pasan al repo público."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sincronizar_aula_semanal as s  # noqa: E402

EXCLUIR = ["2026pr Notas.pdf", "Notas 15-10.pdf", "Calificaciones Certamen 1.xlsx", "NOTAS_C2.pdf",
           "Nómina curso.pdf", "Lista de alumnos paralelo 200.pdf", "Asistencia_ayudantia.xlsx",
           "/storage/x/CIV233/Evaluaciones_y_Entregas/Notas (final).pdf"]
CONSERVAR = ["Pauta Ayudantía 6.pdf", "CIV244_Clase_01_handout.pdf", "Apunte-10-Cinematica_conservacion_masa.pdf",
             "CIV222 2026-20 Ejercicio Gestión de Costos.pdf", "Listado de rendimientos.pdf", "Notación indicial.pdf",
             "Anotaciones de clase.pdf", "Programa de Estudio.pdf"]

fallas = [f"excluir {n}" for n in EXCLUIR if not s.es_dato_de_terceros(n)]
fallas += [f"conservar {n}" for n in CONSERVAR if s.es_dato_de_terceros(n)]
for f in fallas:
    print("FALLA", f)
print(f"Resultado T30: {'PASS' if not fallas else 'FAIL'}")
sys.exit(1 if fallas else 0)
