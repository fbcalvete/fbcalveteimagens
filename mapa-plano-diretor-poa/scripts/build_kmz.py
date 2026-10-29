"""Exporta as tres camadas para KMZ (Google Earth), com cores por zona e ficha do regime.

Uso: python3 build_kmz.py <saida.kmz>
Cada camada vira uma pasta que liga/desliga no painel "Lugares" do Google Earth.
"""
import html
import json
import os
import sys
import zipfile

import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPolygon

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(HERE, '..', 'dados')
OUT = sys.argv[1]
CORES = json.load(open(os.path.join(HERE, 'cores.json'), encoding='utf-8'))
CINZA = '#b9bcc6'
EF_ANT, EF_NOVO = 1.2, 0.8   # eficiencia de projeto (mesma do build_gis)


def ramp(anch, v):
    if v <= anch[0][0]:
        return anch[0][1]
    for (v0, c0), (v1, c1) in zip(anch, anch[1:]):
        if v <= v1:
            t = (v - v0) / (v1 - v0)
            a, b = [int(c0[i:i + 2], 16) for i in (1, 3, 5)], [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
            return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(a, b))
    return anch[-1][1]


def gcolor(g):
    """Ganho (%) -> cor: vermelhos se perde, amarelo so na variacao nula, verdes se ganha (mesma regra do HTML)."""
    G = CORES['ganho']
    return G['zero'] if abs(g) < G['tol'] else ramp(G['neg'] if g < 0 else G['pos'], g)


def ok(v):
    return v is not None and not (isinstance(v, float) and np.isnan(v)) and v > 0


def kcolor(hexc, alpha):
    h = hexc.lstrip('#')
    return f'{alpha:02x}{h[4:6]}{h[2:4]}{h[0:2]}'


def fmt(v, unit=''):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return '—'
    if isinstance(v, float):
        return f'{v:.2f}'.rstrip('0').rstrip('.').replace('.', ',') + unit
    return html.escape(str(v)) + unit


def table(rows):
    tr = ''.join(f'<tr><td style="color:#555;padding:2px 8px 2px 0">{k}</td><td><b>{v}</b></td></tr>' for k, v in rows)
    return f'<![CDATA[<table style="font:12px sans-serif">{tr}</table>]]>'


def coords(ring):
    return ' '.join(f'{x:.6f},{y:.6f}' for x, y in ring.coords)


def geom_kml(g):
    polys = g.geoms if isinstance(g, MultiPolygon) else [g]
    out = []
    for p in polys:
        if p.is_empty:
            continue
        inner = ''.join(f'<innerBoundaryIs><LinearRing><coordinates>{coords(r)}</coordinates></LinearRing></innerBoundaryIs>'
                        for r in p.interiors)
        out.append(f'<Polygon><outerBoundaryIs><LinearRing><coordinates>{coords(p.exterior)}</coordinates>'
                   f'</LinearRing></outerBoundaryIs>{inner}</Polygon>')
    return out[0] if len(out) == 1 else '<MultiGeometry>' + ''.join(out) + '</MultiGeometry>'


def simp(gdf):
    g = gdf.to_crs(31982)
    g['geometry'] = g.geometry.simplify(0.3, preserve_topology=True)
    return g.to_crs(4326)


styles, folders = {}, []


def style(sid, color, alpha=0x99):
    styles[sid] = (f'<Style id="{sid}"><LineStyle><color>{kcolor("#ffffff", 0xb0)}</color><width>0.6</width></LineStyle>'
                   f'<PolyStyle><color>{kcolor(color, alpha)}</color></PolyStyle></Style>')
    return sid


def folder(name, items, visible):
    folders.append(f'<Folder><name>{html.escape(name)}</name><visibility>{int(visible)}</visibility>{"".join(items)}</Folder>')


def placemark(name, sid, desc, geom, visible):
    return (f'<Placemark><name>{html.escape(name)}</name><visibility>{int(visible)}</visibility>'
            f'<styleUrl>#{sid}</styleUrl><description>{desc}</description>{geom_kml(geom)}</Placemark>')


old = simp(gpd.read_file(os.path.join(DADOS, 'pddua_antigo_zonas.gpkg')))
items = []
for r in old.itertuples():
    sid = style(f'ia_{r.ia_bas}'.replace('.', '_'), ramp(CORES['priv'], r.ia_bas * EF_ANT) if ok(r.ia_bas) else CINZA)
    desc = table([('Zona de uso', fmt(r.zona_uso)), ('MZ · UEU · subunidade', f'{r.mz} · {r.ueu} · {r.subunid}'),
                  ('D-A-I-V', f'{r.dens_cod}-{r.ativ_cod}-{r.ia_cod}-{r.vol_cod}'),
                  ('IA básico / máximo', f'{fmt(r.ia_bas)} / {fmt(r.ia_max)}'),
                  ('CA equivalente (×1,5)', f'{fmt(r.caeq_bas)} / {fmt(r.caeq_max)}'),
                  ('Altura máxima', fmt(r.alt_max, ' m') if r.alt_max == r.alt_max and r.alt_max is not None else fmt(r.alt_txt)),
                  ('Taxa de ocupação', fmt(r.tx_ocup)), ('Fonte do IA', fmt(r.ia_fonte)),
                  ('Norma do IA', fmt(r.ia_lei) + (' · ' + html.escape(r.ia_lei_obs) if isinstance(r.ia_lei_obs, str) else '')
                   if isinstance(r.ia_lei, str) else '—'),
                  ('Regime definido por (DMWeb)', fmt(r.regime_ref) if r.regime_ref else '—'),
                  ('Teto do IA (Anexo 6)', fmt(r.ia_teto))])
    items.append(placemark(f'IA {fmt(r.ia_bas)} · {r.zona_uso}', sid, desc, r.geometry, False))
folder('Plano antigo · PDDUA · cor pelo IA básico', items, False)

new = simp(gpd.read_file(os.path.join(DADOS, 'pdus_novo_zonas.gpkg')))
items = []
for r in new.itertuples():
    ef = EF_ANT if r.base_calc == 'PDDUA (IA)' else EF_NOVO   # Zona Rural mantem a base de calculo do PDDUA
    sid = style(f'ca_{r.base_calc[0]}_{r.ca_bas}'.replace('.', '_'), ramp(CORES['priv'], r.ca_bas * ef) if ok(r.ca_bas) else CINZA)
    desc = table([('ZOT', fmt(r.zot)), ('Ocupação', fmt(r.ocupacao)), ('CA básico / máximo', f'{fmt(r.ca_bas_txt)} / {fmt(r.ca_max_txt)}'),
                  ('Fonte do CA básico', fmt(r.fonte_ca_bas)),
                  ('Altura máxima', fmt(r.alt_txt, ' m')), ('Lote mínimo', fmt(r.lote_min, ' m²')),
                  ('Bairro · setor', f'{fmt(r.bairro)} · {fmt(r.setor)}'), ('ZOT no projeto pós-audiência', fmt(r.zot_projeto))])
    items.append(placemark(f'CA {fmt(r.ca_bas_txt)} · {r.zot}', sid, desc, r.geometry, False))
folder('Plano novo · LUOS 2026 · cor pelo CA básico', items, False)

ov = simp(gpd.read_file(os.path.join(DADOS, 'dinamica_sobreposicao.gpkg')))
items = []
for r in ov.itertuples():
    g = r.ganho_bas
    has = g == g and g is not None
    cor = gcolor(g) if has else CINZA
    sid = style('g_' + cor[1:] if has else 'g_sem', cor, 0xc0)
    nome = (f'{"+" if g > 0 else ""}{fmt(g)}%' if has else 'Sem comparação') + f' · IA {fmt(r.ia_bas)} → CA {fmt(r.ca_bas)}'
    desc = table([('Ganho de área privativa (básico)', f'{"+" if has and g > 0 else ""}{fmt(g)}%' if has else 'sem comparação'),
                  ('IA anterior → CA futuro', f'{fmt(r.ia_bas)} → {fmt(r.ca_bas)}'),
                  ('Área privativa por m² de terreno', f'{fmt(r.priv_ant)} → {fmt(r.priv_novo)}'),
                  ('Ganho com o potencial máximo', f'{fmt(r.ganho_max)}%'),
                  ('Fonte do IA anterior', fmt(r.ia_fonte) + (f' ({fmt(r.ia_lei)})' if isinstance(r.ia_lei, str) else '')),
                  ('Altura', f'{fmt(r.alt_ant, " m")} → {fmt(r.alt_novo, " m")}'),
                  ('Antigo', fmt(r.zona_uso)), ('Novo', fmt(r.zot))])
    items.append(placemark(nome, sid, desc, r.geometry, True))
folder('Dinâmica · ganho de área privativa (CA × 0,8 ÷ IA × 1,2 − 1)', items, True)

kml = ('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
       '<name>Planos Diretores de Porto Alegre</name>'
       '<description>PDDUA (LC 434/99) × LUOS sancionada (2026). Fonte: Prefeitura de Porto Alegre (SMAMUS/Procempa).</description>'
       + ''.join(styles.values()) + ''.join(folders) + '</Document></kml>')
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.writestr('doc.kml', kml)
print('KMZ:', OUT, round(os.path.getsize(OUT) / 1e6, 2), 'MB')
