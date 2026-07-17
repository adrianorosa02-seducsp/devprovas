from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import requests

from app.schemas.sed import SedMaterial, SedMaterialFilters, SedRequest, SedResponse


FIXTURES_DIR = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "materiais-digitais"

SED_API_URL = "https://sedintegracoes.educacao.sp.gov.br/apirepocmsp/api/materiais-digitais/materiaisdigitais"


class SedAdapter:
    def __init__(self, use_fixtures: bool = True, token: Optional[str] = None):
        self.use_fixtures = use_fixtures
        self.token = token or os.getenv("SED_TOKEN")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _fixture_path(self, filters: SedMaterialFilters) -> Path:
        tipo = "EF" if filters.tipo_ensino == 1 else "EM"
        serie = str(filters.serie)
        bimestre = str(filters.bimestre)
        componente_map = {13: "MAT", 1: "POR"}
        componente = componente_map.get(filters.componente, str(filters.componente))
        filename = f"{tipo}{serie}{bimestre}{componente}.json"
        year_dir = FIXTURES_DIR / str(filters.ano)
        return year_dir / filename

    def _load_fixture(self, filters: SedMaterialFilters) -> Optional[SedResponse]:
        path = self._fixture_path(filters)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return SedResponse(**data)

    def _fetch_api(self, filters: SedMaterialFilters) -> SedResponse:
        payload = {
            "key": self.token,
            "Ano": str(filters.ano),
            "TipoEnsino": str(filters.tipo_ensino),
            "Serie": str(filters.serie),
            "Bimestre": str(filters.bimestre),
            "Componente": str(filters.componente),
            "IsPrepara": filters.is_prepara,
            "IsPreparaReforco": filters.is_prepara_reforco,
        }
        resp = self.session.post(SED_API_URL, json=payload, timeout=30)
        resp.raise_for_status()
        materials = [SedMaterial(**item) for item in resp.json()]
        request_obj = SedRequest(**payload)
        return SedResponse(
            request=request_obj,
            response=materials,
            metadata={"source": "api", "totalItems": len(materials)},
        )

    def get_materiais(self, filters: SedMaterialFilters) -> SedResponse:
        if self.use_fixtures:
            fixture = self._load_fixture(filters)
            if fixture:
                return fixture
        return self._fetch_api(filters)

    def list_available_fixtures(self, ano: int) -> list[str]:
        year_dir = FIXTURES_DIR / str(ano)
        if not year_dir.exists():
            return []
        return [f.name for f in year_dir.glob("*.json")]