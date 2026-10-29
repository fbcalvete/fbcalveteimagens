"""Monta os GIS independentes dos dois planos e a sobreposicao (dinamica).

Uso: python3 build_gis.py <pasta_raw> <pasta_dados>

Saidas (em <pasta_dados>):
  pddua_antigo_zonas.{gpkg,geojson}   subunidades do PDDUA (LC 434/99) + regime
  pdus_novo_zonas.{gpkg,geojson}      ZOTs da LUOS sancionada (2026) + regime
  dinamica_sobreposicao.{gpkg,geojson} intersecao antigo x novo com deltas
  tabelas/*.csv                       anexos e regime por ZOT
"""
import json
import os
import re
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import MultiPolygon, Polygon

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(OUT, 'tabelas'), exist_ok=True)
CRS_M = 31982   # SIRGAS 2000 / UTM 22S (metrico, usado pela Prefeitura)
CRS_G = 4326
FATOR_NAO_ADENSAVEL = 1.5  # metodologia SMAMUS: CA novo = areas adensaveis + nao adensaveis


def ncode(c):
    """Normaliza codigos do PDDUA ('01'->'1', '02A'->'2A', '15,3'->'15.3')."""
    if c is None or (isinstance(c, float) and np.isnan(c)):
        return None
    s = str(c).strip().replace(',', '.').upper()
    if not s:
        return None
    m = re.match(r'^0*(\d+)(.*)$', s)
    return m.group(1) + m.group(2) if m else s


def num(s):
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return None
    t = str(s).strip().replace('*', '').replace('%', '').replace(',', '.')
    try:
        return float(t)
    except ValueError:
        return None


def table(name):
    d = json.load(open(os.path.join(RAW, name + '.json')))
    return pd.DataFrame([f['properties'] for f in d['features']])


def polys_only(gdf):
    gdf = gdf.copy()
    gdf['geometry'] = gdf.geometry.make_valid()

    def keep(g):
        if g is None or g.is_empty:
            return None
        if isinstance(g, (Polygon, MultiPolygon)):
            return g
        ps = [x for x in getattr(g, 'geoms', []) if isinstance(x, (Polygon, MultiPolygon))]
        flat = []
        for p in ps:
            flat += list(p.geoms) if isinstance(p, MultiPolygon) else [p]
        return MultiPolygon(flat) if flat else None
    gdf['geometry'] = gdf.geometry.apply(keep)
    return gdf[gdf.geometry.notna()]


def save(gdf, name, layer):
    g = gdf.to_crs(CRS_G)
    g.to_file(os.path.join(OUT, name + '.gpkg'), layer=layer, driver='GPKG')
    g.to_file(os.path.join(OUT, name + '.geojson'), driver='GeoJSON', COORDINATE_PRECISION=6)


# ---------------------------------------------------------------- PDDUA (antigo)
ia = table('tab_pddua_ia_anexo6')
ia['cod'] = ia.codigo.map(ncode)
ia['ia_bas'] = ia.ia.map(num)
ia['ia_max'] = ia.ia_max.map(num)
ia.loc[ia.ia_max.isna() & ia.ia_bas.notna(), 'ia_max'] = ia.ia_bas   # sem solo criado
ia['ia_obs'] = np.where(ia.ia_bas.isna(), ia.ia, ia.obs_1.fillna(''))
ia = ia.set_index('cod')

vol = table('tab_pddua_vol_anexo7_1')
vol['cod'] = vol.codigo.map(ncode)
vol['alt_max_n'] = vol.alt_max.map(num)
vol = vol.set_index('cod')

atv = table('tab_pddua_atv_anexo5_1')
atv['cod'] = atv.ga.map(ncode)
zona_uso = atv.set_index('cod').zonas_uso.str.strip().str.rstrip('.').to_dict()

old = gpd.read_file(os.path.join(RAW, 'pddua_subunidades_dmweb.geojson'))
old = polys_only(old).to_crs(CRS_M)
old = old.reset_index(drop=True)
o = pd.DataFrame({
    'id_ant': old.index, 'mz': old.MZ, 'ueu': old.UEU, 'subunid': old.SUBUNIDADE, 'cod_subun': old.COD_SUBUN,
    'dens_cod': old.DENSIDADE.map(ncode), 'ativ_cod': old.ATIVIDADE.map(ncode),
    'ia_cod': old.INDICE.map(ncode), 'vol_cod': old.VOLUMETRIA.map(ncode),
})
# o Anexo 5.1 lista onde cada grupamento vale ("Mista 02, Centro Histórico"); o nome da zona e a 1a parte
o['uso_anexo'] = o.ativ_cod.map(zona_uso)
o['zona_uso'] = o.uso_anexo.str.replace(', Centro Histórico', '', regex=False).fillna('Regime urbanístico próprio / a consultar')
o['ia_bas'] = o.ia_cod.map(ia.ia_bas)
o['ia_max'] = o.ia_cod.map(ia.ia_max)
o['solo_cria'] = o.ia_cod.map(ia.sc)
o['tpc'] = o.ia_cod.map(ia.tpc)
o['quota'] = o.ia_cod.map(ia.quota)
o['ia_obs'] = o.ia_cod.map(ia.ia_obs).fillna('Regime urbanístico conforme legislação específica / EVU')
o['alt_max'] = o.vol_cod.map(vol.alt_max_n)
o['alt_txt'] = o.vol_cod.map(vol.alt_max).fillna('Conforme EVU / legislação específica')
o['alt_divisa'] = o.vol_cod.map(vol.alt_div)
o['alt_base'] = o.vol_cod.map(vol.alt_base)
o['tx_ocup'] = o.vol_cod.map(vol.tax_ocup)
o['caeq_bas'] = (o.ia_bas * FATOR_NAO_ADENSAVEL).round(2)
o['caeq_max'] = (o.ia_max * FATOR_NAO_ADENSAVEL).round(2)
obs = old[['OBS_1', 'OBS_2', 'OBS_3', 'OBS_4', 'OBS_5']].fillna(0).astype(int)
o['obs'] = obs.apply(lambda r: ','.join(str(v) for v in r if v), axis=1)
o['area_m2'] = old.area.round(1)
old_g = gpd.GeoDataFrame(o, geometry=old.geometry.values, crs=CRS_M)
print('PDDUA:', len(old_g), 'subunidades; sem IA numerico:', old_g.ia_bas.isna().sum(),
      '; sem altura numerica:', old_g.alt_max.isna().sum())
save(old_g, 'pddua_antigo_zonas', 'pddua_antigo_zonas')
ia.reset_index().drop(columns=['objectid', 'objectid_1'], errors='ignore').to_csv(
    os.path.join(OUT, 'tabelas', 'pddua_anexo6_indice_aproveitamento.csv'), index=False)
vol.reset_index().drop(columns=['objectid', 'objectid_1'], errors='ignore').to_csv(
    os.path.join(OUT, 'tabelas', 'pddua_anexo7_1_volumetria.csv'), index=False)
atv.drop(columns=['objectid', 'objectid_1'], errors='ignore').to_csv(
    os.path.join(OUT, 'tabelas', 'pddua_anexo5_1_zonas_de_uso.csv'), index=False)

# ---------------------------------------------------------------- PDUS / LUOS (novo)
a5 = gpd.read_file(os.path.join(RAW, 'pdus_anexo5_zonas_quarteiroes.geojson'))
a5 = polys_only(a5).to_crs(CRS_M)

# Regime por ZOT: os campos ca_*/vol_* do Anexo 5 refletem a coluna `zona`;
# usa so as linhas onde zona == zot_emendas para nao herdar regime da zona antiga.
REG = {
    'ca_bas_txt': 'ca_01', 'ca_max_txt': 'ca_02', 'ca_3_txt': 'ca_03', 'ca_4_txt': 'ca_04',
    'alt_txt': 'vol_h_01', 'lote_min': 'lote_01', 'testada': 'lote_02', 'mod_frac': 'mod_frac',
    'perm_min': 'vol_p_06', 'perm_max': 'vol_p_05', 'afast_fre': 'vol_02', 'afast_lat': 'vol_03',
    'afast_fun': 'vol_04', 'recuo_jard': 'vol_08', 'parcelam': 'parc', 'edificac': 'edif',
    'ativid': 'ativ', 'ocupacao': 'ocup_emendas', 'caract': 'caract', 'finalid': 'final',
}
ok = a5[a5.zona == a5.zot_emendas]
mode = lambda s: s.dropna().mode().iloc[0] if s.dropna().size else None
reg = ok.groupby('zot_emendas').agg({v: mode for v in REG.values()}).rename(columns={v: k for k, v in REG.items()})
reg.index.name = 'zot'
reg.loc['ZOT 08.3 - D'] = None   # criada por emenda; parametros nao publicados na base GIS
reg.loc['ZOT 08.3 - D', ['caract', 'finalid']] = [
    'Subzona criada por emenda na Câmara (Cidade Baixa / Bom Fim).',
    'Parâmetros não publicados na base GIS da Prefeitura - consultar a LUOS sancionada.']
reg.loc['POLÍGONO VETADO'] = None
reg.loc['POLÍGONO VETADO', ['caract', 'finalid']] = [
    'Área cuja alteração aprovada pela Câmara foi vetada na sanção (jul/2026).',
    'Regime depende da apreciação do veto pela Câmara - ver campo zot_projeto.']
reg['ca_bas'] = reg.ca_bas_txt.map(num)
reg['ca_max'] = reg.ca_max_txt.map(num)
# CA maximo "Nao se aplica"/"Ajuste/TDC": sem acrescimo oneroso -> igual ao basico
reg.loc[reg.ca_max.isna() & reg.ca_bas.notna(), 'ca_max'] = reg.ca_bas
reg['alt_max'] = reg.alt_txt.map(num)
reg = reg[['ocupacao', 'ca_bas', 'ca_max', 'alt_max', 'ca_bas_txt', 'ca_max_txt', 'ca_3_txt', 'ca_4_txt',
           'alt_txt', 'lote_min', 'testada', 'mod_frac', 'perm_min', 'perm_max', 'afast_fre', 'afast_lat',
           'afast_fun', 'recuo_jard', 'parcelam', 'edificac', 'ativid', 'caract', 'finalid']]
reg.to_csv(os.path.join(OUT, 'tabelas', 'pdus_regime_por_zot.csv'))

# Geometria: mapa da LUOS sancionada (inclui emendas e poligonos vetados) ...
lu = gpd.read_file(os.path.join(RAW, 'luos_zoneamento_min.geojson'))
lu = polys_only(lu).to_crs(CRS_M)
lu = lu[lu.zona_posaud.notna()]
new = gpd.GeoDataFrame({
    'zot': lu.zona_posaud.values, 'bairro': lu.bairro.values, 'setor': lu.setor.values,
    'upl': lu.upl.values, 'fonte': 'LUOS sancionada (zoneamento_min)'}, geometry=lu.geometry.values, crs=CRS_M)

# ... complementada pelos quarteiroes do Anexo 5 que o mapa da LUOS nao cobre (areas ESPECIAIS etc.)
cover = lu.geometry.union_all()
rest = a5[['zot_emendas', 'bairro', 'setor', 'upl', 'geometry']].copy()
rest['geometry'] = rest.geometry.difference(cover)
rest = rest[~rest.geometry.is_empty].explode(index_parts=False)
rest = rest[(rest.area >= 300) & (rest.area / rest.length >= 3)]   # descarta frestas de borda
rest = rest[rest.zot_emendas.notna()]
comp = gpd.GeoDataFrame({
    'zot': rest.zot_emendas.values, 'bairro': rest.bairro.str.title().values, 'setor': rest.setor.values,
    'upl': rest.upl.values, 'fonte': 'Anexo 5 PDUS (complemento)'}, geometry=rest.geometry.values, crs=CRS_M)
new = pd.concat([new, comp], ignore_index=True)

# zona na versao pos-audiencia (a do link do Experience), para referencia
cent = gpd.GeoDataFrame({'i': new.index}, geometry=new.representative_point(), crs=CRS_M)
jj = gpd.sjoin(cent, a5[['zona_posaud', 'geometry']], how='left', predicate='within').drop_duplicates('i')
new['zot_projeto'] = jj.set_index('i').zona_posaud.reindex(new.index).values
new = new.join(reg[['ocupacao', 'ca_bas', 'ca_max', 'alt_max', 'ca_bas_txt', 'ca_max_txt', 'alt_txt',
                    'lote_min', 'mod_frac', 'perm_min', 'perm_max', 'recuo_jard']], on='zot')
new['area_m2'] = new.area.round(1)
new.insert(0, 'id_novo', new.index)
new = gpd.GeoDataFrame(new, geometry='geometry', crs=CRS_M)
print('PDUS:', len(new), 'poligonos;', (new.fonte != 'LUOS sancionada (zoneamento_min)').sum(),
      'de complemento; ZOTs:', new.zot.nunique())
save(new, 'pdus_novo_zonas', 'pdus_novo_zonas')

# ---------------------------------------------------------------- Sobreposicao
OLDC = ['id_ant', 'cod_subun', 'zona_uso', 'dens_cod', 'ativ_cod', 'ia_cod', 'vol_cod', 'ia_bas', 'ia_max',
        'caeq_bas', 'caeq_max', 'alt_max']
NEWC = ['id_novo', 'zot', 'ocupacao', 'ca_bas', 'ca_max', 'alt_max', 'bairro']
a = old_g[OLDC + ['geometry']].rename(columns={'alt_max': 'alt_ant'})
b = new[NEWC + ['geometry']].rename(columns={'alt_max': 'alt_novo'})
ov = gpd.overlay(a, b, how='intersection', keep_geom_type=True)
ov = ov[ov.area >= 10].copy()
ov['d_ca_bas'] = (ov.ca_bas - ov.caeq_bas).round(2)
ov['d_ca_max'] = (ov.ca_max - ov.caeq_max).round(2)
ov['d_alt'] = (ov.alt_novo - ov.alt_ant).round(1)
ov['r_ca_max'] = (ov.ca_max / ov.caeq_max).round(3)


def classe(d, tol):
    return np.select([d.isna(), d > tol, d < -tol], ['Sem comparação', 'Ampliou', 'Reduziu'], 'Manteve')


ov['din_camax'] = classe(ov.d_ca_max, 0.05)
ov['din_cabas'] = classe(ov.d_ca_bas, 0.05)
ov['din_alt'] = classe(ov.d_alt, 0.5)
ov['area_m2'] = ov.area.round(1)
print('Sobreposicao:', len(ov), 'pecas')
print(ov.groupby('din_camax').area_m2.sum().div(1e6).round(2).to_string())
save(ov, 'dinamica_sobreposicao', 'dinamica_sobreposicao')


# ---------------------------------------------------------------- Resumo por bairro
def wmean(df, col):
    v = df[df[col].notna()]
    return round((v[col] * v.area_m2).sum() / v.area_m2.sum(), 2) if len(v) else None


rows = []
for bairro, df in ov.groupby(ov.bairro.fillna('(sem bairro)')):
    tot = df.area_m2.sum()
    r = {'bairro': bairro, 'area_ha': round(tot / 1e4, 1)}
    for c in ['Ampliou', 'Manteve', 'Reduziu', 'Sem comparação']:
        r['pct_camax_' + c.split()[0].lower()] = round(df.loc[df.din_camax == c, 'area_m2'].sum() / tot * 100, 1)
    comp = df.loc[df.d_ca_max.notna(), 'area_m2'].sum()
    r['pct_area_comparavel'] = round(comp / tot * 100, 1)
    ok = comp / tot >= 0.25   # media so quando ao menos 1/4 do bairro e comparavel
    r.update({'d_ca_bas_medio': wmean(df, 'd_ca_bas') if ok else None, 'd_ca_max_medio': wmean(df, 'd_ca_max') if ok else None,
              'd_alt_medio_m': wmean(df, 'd_alt') if ok else None})
    rows.append(r)
pd.DataFrame(rows).sort_values('d_ca_max_medio', ascending=False).to_csv(
    os.path.join(OUT, 'tabelas', 'dinamica_por_bairro.csv'), index=False)
