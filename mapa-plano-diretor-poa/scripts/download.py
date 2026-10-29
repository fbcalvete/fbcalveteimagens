"""Baixa as camadas oficiais dos dois planos diretores de Porto Alegre.

Uso: python3 download.py <pasta_saida> [nome_camada ...]
Paginado (resultOffset) e com retry: o servidor da SMAMUS costuma recusar
conexoes quando esta sobrecarregado.
"""
import sys, json, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agsfetch import get

OUT = sys.argv[1]
PROC = "https://mapaspoa-prod-2020.procempa.com.br/arcgis/rest/services/SMAMS_DM/TM_POA_SMAMS_Plano_Diretor/MapServer"
SMA = "https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted"

JOBS = [
    # nome, url da camada, campo OID, page size, geometria?
    # Plano antigo (PDDUA) - mesmo servico usado pelo DMWeb (Procempa)
    ("pddua_subunidades_dmweb", f"{PROC}/16", "OBJECTID", 1000, True),
    ("limite_municipal", f"{PROC}/18", "OBJECTID", 1000, True),
    ("logradouros", f"{PROC}/8", "OBJECTID", 1000, True),
    ("numero_predial", f"{PROC}/3", "OBJECTID", 1000, True),
    ("numero_imovel", f"{PROC}/5", "OBJECTID", 1000, True),
    # Plano novo (PDUS / LUOS) - SMAMUS
    ("pdus_anexo5_zonas_quarteiroes", f"{SMA}/pdus_anexo5_zonasdeocupacao/FeatureServer/0", "objectid", 2000, True),
    ("luos_zoneamento_min", "https://services3.arcgis.com/ArYIEKBXSSNP3WQG/arcgis/rest/services/zoneamento_min/FeatureServer/0", "objectid", 2000, True),
    # Tabelas do regime urbanistico do PDDUA
    ("tab_pddua_ia_anexo6", f"{SMA}/pddua_ia_anexo_6/FeatureServer/0", "objectid", 2000, False),
    ("tab_pddua_vol_anexo7_1", f"{SMA}/pddua_vol_anexo_7_1/FeatureServer/0", "objectid", 2000, False),
    ("tab_pddua_atv_anexo5_1", f"{SMA}/PDDUA_ATVS_ANEXO_5_1/FeatureServer/0", "objectid", 2000, False),
]
only = set(sys.argv[2:])
for name, url, oid, ps, geom in JOBS:
    if only and name not in only:
        continue
    path = os.path.join(OUT, name + ('.geojson' if geom else '.json'))
    if os.path.exists(path):
        print('skip', name); continue
    total = get(url + '/query', {'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'})['count']
    feats = []
    off = 0
    while off < total:
        p = {'where': '1=1', 'outFields': '*', 'orderByFields': oid, 'resultOffset': off,
             'resultRecordCount': ps, 'f': 'geojson' if geom else 'json'}
        if geom:
            p['outSR'] = 4326
        else:
            p['returnGeometry'] = 'false'
        d = get(url + '/query', p, timeout=180)
        fs = d['features']
        if not geom:
            fs = [{'type': 'Feature', 'geometry': None, 'properties': f['attributes']} for f in fs]
        if not fs:
            break
        feats += fs
        off += len(fs)
        print(f'{name}: {off}/{total}', flush=True)
        time.sleep(0.5)
    ids = [f['properties'].get(oid) for f in feats]
    assert len(ids) == len(set(ids)), f'duplicated ids in {name}'
    print(f'{name}: got {len(feats)} of {total}')
    with open(path, 'w') as fh:
        json.dump({'type': 'FeatureCollection', 'source': url, 'downloaded': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), 'features': feats}, fh, ensure_ascii=False)
