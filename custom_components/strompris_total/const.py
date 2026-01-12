DOMAIN = "strompris_total"

CONF_NAME = "name"
CONF_SPOT_ENTITY = "spot_entity"
CONF_PRICE_AREA = "price_area"
CONF_DSO = "dso"
CONF_CONTRACT = "contract"

# Options keys (stored in config_entry.options)
OPT_PRICE_AREA = "opt_price_area"
OPT_DSO = "opt_dso"
OPT_CONTRACT = "opt_contract"

OPT_PAASLAG_ORE = "opt_paaslag_ore_kwh"
OPT_STROM_FAST_KR = "opt_strom_fast_kr_mnd"

OPT_NETT_DAG_ORE = "opt_nett_energiledd_dag_ore_kwh"
OPT_NETT_NATT_ORE = "opt_nett_energiledd_natt_ore_kwh"
OPT_NETT_FAST_KR = "opt_nett_fastledd_kr_mnd"

OPT_ELAVGIFT_ORE = "opt_elavgift_ore_kwh"
OPT_ENOVA_ORE = "opt_enova_ore_kwh"
OPT_MVA_PROSENT = "opt_mva_prosent"

PRICE_AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]
CONTRACTS = ["spot_plus_paaslag", "fastpris", "variabel"]

DEFAULTS = {
    OPT_PRICE_AREA: "NO1",
    OPT_DSO: "ukjent",
    OPT_CONTRACT: "spot_plus_paaslag",
    OPT_PAASLAG_ORE: 3.0,
    OPT_STROM_FAST_KR: 49.0,
    OPT_NETT_DAG_ORE: 10.0,
    OPT_NETT_NATT_ORE: 10.0,
    OPT_NETT_FAST_KR: 0.0,
    OPT_ELAVGIFT_ORE: 7.13,  # juster etter behov
    OPT_ENOVA_ORE: 1.0,
    OPT_MVA_PROSENT: 25.0,
}
