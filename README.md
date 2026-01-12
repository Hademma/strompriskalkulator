# Strømpris Total (Norge) – HACS startrepo

Dette er et **minimal-fungerende** startrepo for en Home Assistant custom integration som:

- konfigureres i UI (Config Flow)
- kan endres i UI (Options Flow)
- eksponerer justerbare **Number**/**Select**-entiteter (påslag, avgifter, nettleie osv.)
- beregner sensorer for **total variabel strømpris (kr/kWh)** og **fast månedspris (kr/mnd)**

## Hva du må ha fra før
En spotpris-sensor i **NOK/kWh** (f.eks. Nordpool) som denne integrasjonen kan lese.

## Install via HACS (dev)
1. Lag et repo på GitHub med denne strukturen.
2. I HACS: *Custom repositories* → legg til repo-url → type **Integration**.
3. Installer, restart Home Assistant.
4. Settings → Devices & Services → Add Integration → **Strømpris Total (Norge)**.

## Entities du får
- `sensor.<navn>_total_variabel_kr_kwh`
- `sensor.<navn>_fast_kost_kr_mnd`
- `number.<navn>_paaslag_ore_kwh`
- `number.<navn>_strom_fastbelop_kr_mnd`
- `number.<navn>_nett_energiledd_dag_ore_kwh`
- `number.<navn>_nett_energiledd_natt_ore_kwh`
- `number.<navn>_nett_fastledd_kr_mnd`
- `number.<navn>_elavgift_ore_kwh`
- `number.<navn>_enova_ore_kwh`
- `number.<navn>_mva_prosent`
- `select.<navn>_prisomrade`
- `select.<navn>_avtaletype`
- `select.<navn>_nettselskap`

## Tariffer
`custom_components/strompris_total/data/no_dsos.json` er en **eksempel-katalog**.
Bytt ut/utvid med dine egne DSOer og satser.

> NB: Dette er et startrepo. Nettariffer i Norge varierer mye (energiledd dag/natt, kapasitetsledd-trinn osv.).
Integrasjonen er derfor laget slik at DSO-valget bare fyller inn *defaults*, men alt kan overstyres i UI.

## Utvikling
- `config_flow.py`: UI-oppsett + options
- `number.py`/`select.py`: justerbare parametre (lagres i config_entry.options)
- `sensor.py`: beregninger

