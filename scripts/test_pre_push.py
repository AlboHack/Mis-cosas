#!/usr/bin/env python3
"""Prueba T19: hook pre-push sobre un remoto local temporal (no toca el repo real)."""
import os
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hooks", "pre-push")


def run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def commit(repo, ruta, contenido, msg):
    p = os.path.join(repo, ruta)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(contenido)
    run(["git", "add", ruta], repo)
    run(["git", "commit", "-qm", msg], repo)


def main():
    tmp = tempfile.mkdtemp(prefix="t19_")
    try:
        remoto, repo = os.path.join(tmp, "remoto.git"), os.path.join(tmp, "repo")
        run(["git", "init", "-q", "--bare", "-b", "main", remoto], tmp)
        run(["git", "init", "-q", "-b", "main", repo], tmp)
        for k, v in (("user.name", "t"), ("user.email", "t@t")):
            run(["git", "config", k, v], repo)
        run(["git", "remote", "add", "origin", remoto], repo)
        commit(repo, "scripts/a.py", "1", "base")
        run(["git", "push", "-q", "origin", "main"], repo)
        hook_dst = os.path.join(repo, ".git", "hooks", "pre-push")
        shutil.copy(HOOK, hook_dst)
        os.chmod(hook_dst, 0o755)
        env_sin = {k: v for k, v in os.environ.items() if k != "ALLOW_MAIN_PUSH"}

        casos = []
        commit(repo, "universidad/2026-2/x.pdf", "pdf", "chore(sync)")
        casos.append(("datos de sincronización a main: permitido", run(["git", "push", "origin", "main"], repo, env_sin).returncode == 0))

        commit(repo, "scripts/a.py", "2", "codigo")
        casos.append(("código a main sin aprobación: bloqueado", run(["git", "push", "origin", "main"], repo, env_sin).returncode != 0))
        casos.append(("código a main con ALLOW_MAIN_PUSH=1: permitido",
                      run(["git", "push", "origin", "main"], repo, dict(env_sin, ALLOW_MAIN_PUSH="1")).returncode == 0))

        run(["git", "reset", "-q", "--hard", "HEAD~2"], repo)
        commit(repo, "universidad/2026-2/y.pdf", "otro", "divergente")
        casos.append(("force push a main (aun con ALLOW_MAIN_PUSH=1): bloqueado",
                      run(["git", "push", "--force", "origin", "main"], repo, dict(env_sin, ALLOW_MAIN_PUSH="1")).returncode != 0))

        run(["git", "checkout", "-q", "-b", "ag/x"], repo)
        commit(repo, "scripts/b.py", "x", "rama")
        casos.append(("push de código a rama ag/x: permitido", run(["git", "push", "origin", "ag/x"], repo, env_sin).returncode == 0))

        for nombre, ok in casos:
            print(f"  {nombre}: {ok}")
        t19 = all(ok for _, ok in casos)
        print(f"Resultado T19: {'PASS' if t19 else 'FAIL'}")
        return 0 if t19 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
