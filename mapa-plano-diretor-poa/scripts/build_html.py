"""Gera o mapa HTML independente a partir dos GIS de ../dados.

Uso: python3 build_html.py <pasta_raw> <saida.html> [--fragmento <saida_artifact.html>]

A geometria vai embutida no HTML (polyline encoding), junto com o Leaflet,
para o arquivo abrir offline com duplo clique. O fragmento (--fragmento) e
a mesma pagina sem <html>/<head>, carregando o Leaflet do cdnjs.
"""
import json
import os
import sys

import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(HERE, '..', 'dados')
RAW, OUT = sys.argv[1], sys.argv[2]
FRAG = sys.argv[sys.argv.index('--fragmento') + 1] if '--fragmento' in sys.argv else None
CRS_M = 31982


def enc(coords, prec):
    f = 10 ** prec
    out, px, py = [], 0, 0
    for x, y in coords:
        X, Y = round(x * f), round(y * f)
        for v in (Y - py, X - px):
            v = ~(v << 1) if v < 0 else (v << 1)
            while v >= 0x20:
                out.append(chr((0x20 | (v & 0x1f)) + 63))
                v >>= 5
            out.append(chr(v + 63))
        px, py = X, Y
    return ''.join(out)


def simp(gdf, tol):
    return gdf.to_crs(CRS_M).geometry.simplify(tol, preserve_topology=True).to_crs(4326)


def enc_poly(geom, prec=6):
    polys = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
    res = []
    for p in polys:
        if p.is_empty:
            continue
        rings = [p.exterior] + list(p.interiors)
        res.append([enc(list(r.coords)[:-1], prec) for r in rings if len(r.coords) >= 4])
    return res


def enc_line(geom, prec=5):
    lines = geom.geoms if isinstance(geom, MultiLineString) else [geom]
    return [enc(list(line.coords), prec) for line in lines if len(line.coords) >= 2]


def val(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return round(float(v), 3)
    return v


old = gpd.read_file(os.path.join(DADOS, 'pddua_antigo_zonas.gpkg')).sort_values('id_ant')
new = gpd.read_file(os.path.join(DADOS, 'pdus_novo_zonas.gpkg')).sort_values('id_novo')
ov = gpd.read_file(os.path.join(DADOS, 'dinamica_sobreposicao.gpkg'))
assert (old.id_ant.values == np.arange(len(old))).all() and (new.id_novo.values == np.arange(len(new))).all()

payload = {}
og = simp(old, 0.3)
payload['old'] = {
    'g': [enc_poly(g) for g in og],
    'a': [[r.cod_subun, val(r.mz), val(r.ueu), val(r.subunid), r.dens_cod, r.ativ_cod, r.ia_cod, r.vol_cod, r.obs or '']
          for r in old.itertuples()],
}
lk_ia, lk_vol, lk_zu = {}, {}, {}
for r in old.drop_duplicates('ia_cod').itertuples():
    lk_ia[r.ia_cod] = [val(r.ia_bas), val(r.ia_max), r.solo_cria, r.tpc, r.quota, r.ia_obs]
for r in old.drop_duplicates('vol_cod').itertuples():
    lk_vol[r.vol_cod] = [val(r.alt_max), r.alt_txt, r.alt_divisa, r.alt_base, r.tx_ocup]
for r in old.drop_duplicates('ativ_cod').itertuples():
    lk_zu[r.ativ_cod] = r.zona_uso
payload['lk'] = {'ia': lk_ia, 'vol': lk_vol, 'zu': lk_zu}

ng = simp(new, 0.3)
FONTE = {'LUOS sancionada (zoneamento_min)': 0, 'Anexo 5 PDUS (complemento)': 1}
payload['new'] = {
    'g': [enc_poly(g) for g in ng],
    'a': [[r.zot, r.bairro, r.setor, r.upl, FONTE[r.fonte], r.zot_projeto] for r in new.itertuples()],
}
reg = gpd.pd.read_csv(os.path.join(DADOS, 'tabelas', 'pdus_regime_por_zot.csv')).set_index('zot')
payload['reg'] = {z: {k: val(v) for k, v in row.items()} for z, row in reg.iterrows()}

vg = simp(ov, 0.3)
keep = [i for i, g in enumerate(vg) if g is not None and not g.is_empty]
payload['ov'] = {
    'g': [enc_poly(vg.iloc[i]) for i in keep],
    'a': [[int(ov.id_ant.iloc[i]), int(ov.id_novo.iloc[i])] for i in keep],
}
area = ov.groupby('din_camax').area_m2.sum().div(1e6).round(2).to_dict()
area_alt = ov.groupby('din_alt').area_m2.sum().div(1e6).round(2).to_dict()
payload['stats'] = {'camax': area, 'alt': area_alt}

# Logradouros oficiais (base de ruas offline + busca por endereco)
st = gpd.read_file(os.path.join(RAW, 'logradouros.geojson'))
stg = simp(st, 1.0)
CAT = {'R': 'Rua', 'AV': 'Avenida', 'BC': 'Beco', 'AC': 'Acesso', 'PCA': 'Praça', 'ESTR': 'Estrada',
       'PSG': 'Passagem', 'DIR': 'Diretriz', 'TRAV': 'Travessa', 'TRVS': 'Travessa', 'RP': 'Rua Particular',
       'LG': 'Largo', 'RTL': 'Rótula', 'VA': 'Via de Acesso', 'AL': 'Alameda', 'PRQ': 'Parque',
       'VDT': 'Viaduto', 'TUN': 'Túnel', 'ESC': 'Escadaria', 'VIA': 'Via', 'EST': 'Estrada'}
names, nidx, segs = [], {}, []
inum = lambda v: 0 if v is None or (isinstance(v, float) and np.isnan(v)) else int(v)
for r, g in zip(st.itertuples(), stg):
    if g is None or g.is_empty:
        continue
    cat = (r.CDIDECAT or '').strip()
    nm = ' '.join(x for x in [(r.NMIDEPRE or '').strip(), (r.NMIDELOG or '').strip()] if x)
    key = (r.CDIDELOG, cat, nm)
    if key not in nidx:
        nidx[key] = len(names)
        names.append([CAT.get(cat, cat.title()), nm.title().replace(' Da ', ' da ').replace(' Do ', ' do ')
                      .replace(' Dos ', ' dos ').replace(' Das ', ' das ').replace(' De ', ' de ').replace(' E ', ' e '),
                      1 if cat in ('AV', 'ESTR', 'VDT', 'TUN', 'RTL') else 0])
    for line in enc_line(g):
        segs.append([nidx[key], inum(r.NRIMPINI), inum(r.NRIMPFIN), inum(r.NRPARINI), inum(r.NRPARFIN), line])
payload['st'] = {'n': names, 's': segs}

# Numeros prediais do cadastro (anotacoes do DMWeb): localizam o lote na busca por endereco
pts, seen = [], set()
for nm in ('numero_predial', 'numero_imovel'):
    path = os.path.join(RAW, nm + '.geojson')
    if not os.path.exists(path):
        continue
    g = gpd.read_file(path, columns=['TEXTSTRING'])
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    g['num'] = gpd.pd.to_numeric(g.TEXTSTRING.str.extract(r'^\s*(\d{1,5})\s*$')[0], errors='coerce')
    g = g[g.num.notna()]
    c = g.to_crs(CRS_M).geometry.centroid.to_crs(4326)
    for n, y, x in zip(g.num.astype(int), c.y, c.x):
        k = (n, round(y, 4), round(x, 4))
        if k not in seen:
            seen.add(k)
            pts.append((n, round(y, 5), round(x, 5)))
pts.sort(key=lambda t: (round(t[1], 2), t[2]))
payload['np'] = {'n': [t[0] for t in pts], 'c': enc([(t[2], t[1]) for t in pts], 5)}
print('numeros prediais', len(pts))

lim = gpd.read_file(os.path.join(RAW, 'limite_municipal.geojson'))
payload['lim'] = [s for g in simp(lim, 2.0) if g is not None for s in enc_line(g)]

# ponto de exemplo para a abertura (quarteirao no Menino Deus)
ex = new[new.bairro.fillna('').str.lower().eq('menino deus') & new.zot.eq('ZOT 07')]
pt = (ex if len(ex) else new).to_crs(CRS_M).sort_values('area_m2').iloc[len(ex) // 2:].geometry.iloc[0]
pt = gpd.GeoSeries([pt.representative_point()], crs=CRS_M).to_crs(4326).iloc[0]
payload['cores'] = json.load(open(os.path.join(HERE, 'cores.json'), encoding='utf-8'))
payload['meta'] = {
    'exemplo': [round(pt.y, 6), round(pt.x, 6)],
    'gerado': gpd.pd.Timestamp.now(tz='America/Sao_Paulo').strftime('%d/%m/%Y'),
}
for k in ('old', 'new', 'ov'):
    print(k, len(payload[k]['g']), 'feicoes')
print('ruas', len(names), 'logradouros /', len(segs), 'trechos')

def clean(o):
    """NaN -> null e tipos numpy -> python, sem arredondar (coordenadas)."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    return o


data = json.dumps(clean(payload), ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('</', '<\\/')
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
head, body = tpl.split('<!--BODY-->')
css = open(os.path.join(HERE, 'vendor', 'leaflet.css'), encoding='utf-8').read()
js = open(os.path.join(HERE, 'vendor', 'leaflet.js'), encoding='utf-8').read()


def render(standalone):
    h = head.replace('/*LEAFLET_CSS*/', css)
    b = body.replace('/*DADOS*/', data).replace('/*MODO*/', 'true' if standalone else 'false')
    if standalone:
        b = b.replace('<!--LEAFLET_JS-->', '<script>' + js + '</script>')
        return ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + h + '\n</head>\n<body>\n' + b + '\n</body>\n</html>\n')
    b = b.replace('<!--LEAFLET_JS-->',
                  '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>')
    return h + '\n' + b


open(OUT, 'w', encoding='utf-8').write(render(True))
print('HTML:', OUT, round(os.path.getsize(OUT) / 1e6, 2), 'MB')
if FRAG:
    open(FRAG, 'w', encoding='utf-8').write(render(False))
    print('fragmento:', FRAG, round(os.path.getsize(FRAG) / 1e6, 2), 'MB')
