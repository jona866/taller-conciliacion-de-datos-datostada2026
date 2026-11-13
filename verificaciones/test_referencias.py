import ast
import json
import shutil
import subprocess
import sys
import types
from pathlib import Path

import pytest


RAIZ = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/jona866/taller-conciliacion-de-datos-datostada2026.git"
CUADERNOS = sorted((RAIZ / "cuadernos").glob("*.ipynb"))


def preparacion(cuaderno):
    notebook = json.loads(cuaderno.read_text(encoding="utf-8"))
    return next(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code" and "REPO_URL" in "".join(cell["source"])
    )


@pytest.mark.parametrize("cuaderno", CUADERNOS, ids=lambda p: p.name)
def test_referencia_del_cuaderno(cuaderno):
    source = preparacion(cuaderno)
    tree = ast.parse(source)
    asignacion = next(
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "REPO_URL" for target in node.targets)
    )
    assert ast.literal_eval(asignacion.value) == REPO_URL
    assert "/content/taller-conciliacion-de-datos-datostada2026" in source


def test_preparacion_colab_con_clon_limpio(tmp_path, monkeypatch):
    destino = tmp_path / "repo"
    ejecutar = subprocess.run
    clones = []

    def simular_clon(command, **kwargs):
        if command[:2] == ["git", "clone"]:
            clones.append(command)
            destino.mkdir()
            for name in ("nnc.py", "generar_datos.py"):
                shutil.copy2(RAIZ / name, destino / name)
            shutil.copytree(RAIZ / "sql", destino / "sql")
            return subprocess.CompletedProcess(command, 0)
        return ejecutar(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", simular_clon)
    monkeypatch.setitem(sys.modules, "google.colab", types.ModuleType("google.colab"))
    monkeypatch.delitem(sys.modules, "nnc", raising=False)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.chdir(tmp_path)

    for cuaderno in CUADERNOS:
        source = preparacion(cuaderno).replace(
            'pathlib.Path("/content/taller-conciliacion-de-datos-datostada2026")',
            f"pathlib.Path({str(destino)!r})",
        )
        namespace = {}
        exec(compile(source, str(cuaderno), "exec"), namespace)
        assert namespace["con"].execute("SHOW TABLES").fetchall()
        namespace["con"].close()

    assert len(clones) == 1
    assert clones[0][-2] == REPO_URL
    assert (destino / "datos" / "manifiesto.json").is_file()
    assert (destino / "datos" / "verificacion.json").is_file()
