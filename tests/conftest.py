import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nnc  # noqa: E402


@pytest.fixture(scope="session")
def caso():
    # Conjunto de datos a revisar: caso3 (octubre) o carga_nueva (semana 1 de noviembre)
    return os.environ.get("NNC_DATOS", "caso3")


@pytest.fixture(scope="session")
def con(caso):
    return nnc.conectar(caso)


@pytest.fixture(scope="session")
def params(caso):
    return nnc.PARAMETROS[caso]
