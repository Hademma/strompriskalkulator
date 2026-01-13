DOMAIN = "strompris_total"

CONF_NAME = "name"
CONF_SPOT_ENTITY = "spot_entity"
CONF_PRICE_AREA = "price_area"
CONF_DSO = "dso"
CONF_CONTRACT = "contract"
CONF_POWER_ENTITY = "power_entity"

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

# Kapasitetsledd (kr/mnd) per trinn
OPT_KAP_T1_KR = "opt_kap_t1_kr_mnd"
OPT_KAP_T2_KR = "opt_kap_t2_kr_mnd"
OPT_KAP_T3_KR = "opt_kap_t3_kr_mnd"
OPT_KAP_T4_KR = "opt_kap_t4_kr_mnd"
OPT_KAP_T5_KR = "opt_kap_t5_kr_mnd"
OPT_KAP_T6_KR = "opt_kap_t6_kr_mnd"
OPT_KAP_T7_KR = "opt_kap_t7_kr_mnd"

PRICE_AREAS = ["NO1", "NO2", "NO3", "NO4", "NO5"]

CONTRACTS = ["spot_plus_paaslag", "norgespris", "fastpris", "variabel"]

DEFAULTS = {
    OPT_PRICE_AREA: "NO1",
    OPT_DSO: "ukjent",
    OPT_CONTRACT: "spot_plus_paaslag",

    OPT_PAASLAG_ORE: 3.0,
    OPT_STROM_FAST_KR: 49.0,

    OPT_NETT_DAG_ORE: 10.0,
    OPT_NETT_NATT_ORE: 10.0,
    OPT_NETT_FAST_KR: 0.0,

    OPT_ELAVGIFT_ORE: 7.13,
    OPT_ENOVA_ORE: 1.0,
    OPT_MVA_PROSENT: 25.0,

    OPT_KAP_T1_KR: 125.0,
    OPT_KAP_T2_KR: 190.0,
    OPT_KAP_T3_KR: 300.0,
    OPT_KAP_T4_KR: 410.0,
    OPT_KAP_T5_KR: 520.0,
    OPT_KAP_T6_KR: 630.0,
    OPT_KAP_T7_KR: 1175.0,
}

# Kapasitets-trinn (kW)
CAPACITY_TIERS = [
    (2.0,  "0–2 kW",    OPT_KAP_T1_KR),
    (5.0,  "2–5 kW",    OPT_KAP_T2_KR),
    (10.0, "5–10 kW",   OPT_KAP_T3_KR),
    (15.0, "10–15 kW",  OPT_KAP_T4_KR),
    (20.0, "15–20 kW",  OPT_KAP_T5_KR),
    (25.0, "20–25 kW",  OPT_KAP_T6_KR),
    (10_000.0, "25+ kW", OPT_KAP_T7_KR),
]
