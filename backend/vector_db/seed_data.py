"""
vector_db/seed_data.py — Load realistic seed documents into ChromaDB.

Run once:
    python -m backend.vector_db.seed_data

Each agent gets its own ChromaDB collection. The RAG pipeline queries these
collections before calling Featherless AI, so agents reason from real data
rather than hallucinating figures.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.vector_db.setup import add_documents, get_or_create_collection
from loguru import logger


# ── Farmer documents ───────────────────────────────────────────────────────────

FARMER_DOCS = [
    {
        "id": "f001",
        "text": "Kazakhstan wheat harvest 2023: 16.5 million tonnes, down 8% from the 5-year average due to drought in May–June. Deficit regions: Akmola oblast (-22%), Kostanay oblast (-18%), North Kazakhstan (-11%). 2024 forecast: recovery to 17.8 million tonnes under normal rainfall. Recommended buffer stock: 2.1 million tonnes.",
        "metadata": {"year": 2023, "crop": "wheat", "region": "Kazakhstan", "type": "yield_report"},
    },
    {
        "id": "f002",
        "text": "Central Asia climate risk 2024: drought probability 65% in summer. Critical water-stress zones: southern Uzbekistan, Turkmenistan, southern Kazakhstan. Amu Darya river flow at 40% of historical average. Recommended action: drought-resistant wheat varieties (Kazakhstanskaya 10, Eritrospermum 35) and drip-irrigation expansion.",
        "metadata": {"year": 2024, "type": "climate_risk", "region": "Central_Asia"},
    },
    {
        "id": "f003",
        "text": "Ukraine corn production 2023: 28.3 million tonnes (-12% vs 2022). Causes: conflict reducing planted area by 15%, fertiliser disruptions, fuel shortages for harvest machinery. Export potential: 18 million tonnes. Global impact: feed grain deficit of 9 million tonnes affecting livestock sectors in Turkey, Egypt, and North Africa.",
        "metadata": {"year": 2023, "crop": "corn", "region": "Ukraine", "type": "production_report"},
    },
    {
        "id": "f004",
        "text": "Southeast Asia rice 2024: Thailand 32 million tonnes (+3%), Vietnam 27 million tonnes (stable), India export ban created 8-10 million tonne shortfall. Bangladesh and Philippines facing 15-20% import cost increases. Rice price index up 40% since Jan 2023. FAO alert: 47 countries with food deficits above 20%.",
        "metadata": {"year": 2024, "crop": "rice", "region": "Southeast_Asia", "type": "production_report"},
    },
    {
        "id": "f005",
        "text": "Fertiliser supply crisis 2024: nitrogen production down 25% in Europe due to gas price spike. Russian and Belarusian potash exports cut 35% under sanctions. Global fertiliser price index: urea $340/tonne (+18% YoY), DAP $580/tonne (+12% YoY). Projected yield reduction without adequate fertiliser: 8-15% across Central Asia and Eastern Europe.",
        "metadata": {"year": 2024, "type": "fertilizer_shortage", "impact": "yield_reduction"},
    },
    {
        "id": "f006",
        "text": "FAO Food Security Index Q1 2024: global cereal production 2,810 million tonnes. 47 countries need food assistance. Worst affected: Somalia (deficit 65%), Yemen (58%), Afghanistan (52%), Syria (48%), Ethiopia (43%). Central Asia food security score: 62/100 (moderate risk). Recommended reserve target: 60 days of national consumption.",
        "metadata": {"year": 2024, "type": "food_security_index", "source": "FAO"},
    },
    {
        "id": "f007",
        "text": "Akmola region agricultural report 2024: 3.2 million hectares under cultivation, wheat dominant (2.1M ha). Average yield 1.4 t/ha vs 5-year average of 1.8 t/ha. Irrigation coverage: 12% of arable land. Ground water levels down 0.8m since 2020. Livestock sector: 1.2 million cattle, 4.8 million sheep at risk of feed shortage.",
        "metadata": {"year": 2024, "type": "regional_report", "region": "Akmola", "country": "Kazakhstan"},
    },
]

# ── Logistics documents ────────────────────────────────────────────────────────

LOGISTICS_DOCS = [
    {
        "id": "l001",
        "text": "Black Sea grain corridor post-deal analysis 2024: capacity 3 million tonnes/month reduced to 1.2 million tonnes after suspension. Romania (Constanta port, 4M t/year) and Poland (Gdansk, 2.5M t/year) as alternatives add 12-15 transit days. Cost premium: $45-65/tonne. Insurance premiums up 180% for Black Sea routing.",
        "metadata": {"region": "Black_Sea", "type": "route_analysis", "year": 2024},
    },
    {
        "id": "l002",
        "text": "Central Asia grain loss study 2023: post-harvest losses average 10.2% (range 7-15%). Causes: inadequate elevator capacity (60% pre-1990 infrastructure), temperature excursion during rail transit (average 3.2°C above safe range), rodent damage 1.8%, moisture 2.1%. Modern sealed silos reduce losses to 1.5-2%. Investment needed: $2.3B for full modernisation.",
        "metadata": {"region": "Central_Asia", "type": "loss_analysis", "year": 2023},
    },
    {
        "id": "l003",
        "text": "Kazakhstan rail grain logistics 2024: 52,000 grain wagons total, 38,000 operational. Annual capacity 18 million tonnes. Key bottlenecks: Dostyk/Altynkol (China border) 15M t/year limit, seasonal congestion adds 8-12 days. Aktau Caspian port: 5M t/year, 95% utilisation. Trans-Caspian route to Azerbaijan and Turkey: +14 days but no border queues.",
        "metadata": {"region": "Kazakhstan", "type": "rail_capacity", "year": 2024},
    },
    {
        "id": "l004",
        "text": "Turkey grain logistics hub 2024: Mersin port handles 22M tonnes/year (8M grain). Licensed storage 30M tonnes, available 18-20M tonnes. TMO strategic reserve: 7.2M tonnes. Cost: $9-13/tonne/month storage. Mersin to Aqaba (Jordan) 4 days, Alexandria (Egypt) 3 days, Tripoli (Libya) 5 days. Key redistribution hub for Middle East and North Africa.",
        "metadata": {"region": "Turkey", "type": "storage_capacity", "year": 2024},
    },
    {
        "id": "l005",
        "text": "Suez Canal disruption impact 2024: Houthi attacks reroute 25% of grain trade via Cape of Good Hope. Additional transit: 14-18 days. Daily shipping capacity lost: ~180,000 tonnes. Insurance surcharge: $40-70/tonne. Impact on food costs: Egypt wheat import cost up $28/tonne, Yemen up $52/tonne. WFP emergency procurement costs increased $180M in Q1 2024.",
        "metadata": {"region": "Suez_Canal", "type": "route_disruption", "year": 2024},
    },
    {
        "id": "l006",
        "text": "Cold chain infrastructure report 2024: refrigerated capacity for perishables in Central Asia: 2.8 million tonnes total, 40% functional. Temperature-controlled rail wagons: 3,200 units. 24-hour outage risk: 25-35% perishable loss. Annual investment needed to close gap: $420M. Kazakhstan cold chain capacity utilisation: 78%. Priority investments: Almaty (hub) and Shymkent (production zone).",
        "metadata": {"type": "cold_chain", "region": "Central_Asia", "year": 2024},
    },
]

# ── Energy documents ───────────────────────────────────────────────────────────

ENERGY_DOCS = [
    {
        "id": "e001",
        "text": "Agricultural electricity prices 2024: EU average €0.18/kWh (peak winter €0.31/kWh), Kazakhstan $0.06/kWh (subsidised), Turkey $0.12/kWh, Ukraine $0.09/kWh. Irrigation accounts for 28-35% of farm energy costs. Cold storage 18-22%. Germany: 30% farm electricity subsidy. Kazakhstan: agricultural tariff frozen at 2022 levels through 2025.",
        "metadata": {"type": "energy_prices", "year": 2024},
    },
    {
        "id": "e002",
        "text": "Energy-fertiliser nexus 2024: ammonia synthesis requires 8-12 MWh/tonne. At gas >€50/MWh, European plants uneconomical — 30% capacity offline since 2022. Global nitrogen production deficit: 8M tonnes. Direct impact: urea price +40%, corn yield projections -6-9% in energy-import-dependent countries. Solution: renewable-powered green ammonia facilities (CAPEX $1.2B/500k t capacity).",
        "metadata": {"type": "energy_fertiliser", "year": 2024},
    },
    {
        "id": "e003",
        "text": "Kazakhstan grid status 2024: installed capacity 19.2 GW, peak demand 15.8 GW (82% utilisation). Equipment wear: 65% of generation assets need replacement. Northern grid deficit in winter: 8-12%. Outages 2024: 3 major events, 4-12 hours duration, 2.1M people affected. Planned capacity additions: 1.2 GW wind (2025), 800 MW solar (2026). Russian grid interconnect provides 1.5 GW backup.",
        "metadata": {"region": "Kazakhstan", "type": "grid_status", "year": 2024},
    },
    {
        "id": "e004",
        "text": "Renewable energy in agriculture 2024: solar irrigation pumps cut costs 60-70% vs diesel. Turkey: 35% renewable share, agri-solar (agrivoltaics) covering 45,000 ha. Kazakhstan: 8% renewable share, 2.1 GW total. EU Green Deal: 50% renewable farming target by 2030 projected to cut food production energy costs 12-18%. Payback period for farm solar: 4-6 years at current prices.",
        "metadata": {"type": "renewable_energy", "year": 2024},
    },
    {
        "id": "e005",
        "text": "Energy security impact on food systems 2024: Ukraine grid attacks caused $2.1B agricultural losses. Cold chain failure from power cuts: 12% of 2023 harvest lost post-harvest. Egypt power rationing (6-8 hrs/day) reduced food processing capacity 22%. Critical infrastructure interdependency: 1 hour of grid failure costs $4-8M in food sector output. Diesel backup coverage: only 35% of critical food facilities.",
        "metadata": {"type": "energy_food_security", "year": 2024},
    },
]

# ── Market documents ───────────────────────────────────────────────────────────

MARKET_DOCS = [
    {
        "id": "m001",
        "text": "CBOT wheat futures 2024: Jan $220/t → Mar $195/t → Jun $180/t → Sep $172/t. Drivers: record Russian harvest (90M t), Australia +15% export, India ban support. Spread: Chicago SRW vs Kansas HRW $18/t premium. Key price support levels: $165/t (marginal cost), $155/t (stock release threshold). Forward curve suggests $160-175/t for Q1 2025.",
        "metadata": {"commodity": "wheat", "type": "price_history", "year": 2024},
    },
    {
        "id": "m002",
        "text": "Global grain stocks 2024 (USDA): wheat 310M t (104 days cover), corn 290M t (60 days — approaching critical), rice 180M t (90 days). Critical threshold: 60 days. Corn near critical due to US ethanol demand (40% of US corn crop). China holds 50% of global wheat reserves (155M t), limiting market response. Ex-China stocks: wheat 155M t (52 days), corn 145M t (30 days — critical).",
        "metadata": {"type": "global_stocks", "year": 2024, "source": "USDA"},
    },
    {
        "id": "m003",
        "text": "Commodity speculation 2024: CFTC COT data — net speculative longs on wheat at 3-year high March 2024 (+180,000 contracts). Algorithmic trading 68% of CME grain volume. Geopolitical shock amplification: speculative positions increase volatility by 28-35% during events. HFT activity spikes 340% on shipping disruption news. Recommendation: position limits and circuit breakers for food commodities.",
        "metadata": {"type": "market_speculation", "year": 2024},
    },
    {
        "id": "m004",
        "text": "Food inflation index 2024: FAO FFPI at 118.5 (base 2014-16=100). Country inflation: Argentina +214% YoY, Turkey +65% YoY, Egypt +50% YoY, Pakistan +38% YoY, Nigeria +35% YoY. Wheat-import dependent nations spending 18-35% of GDP on food imports. Currency depreciation multiplier: 1% currency fall → 0.4% food price increase for import-dependent economies.",
        "metadata": {"type": "food_inflation", "year": 2024, "source": "FAO"},
    },
    {
        "id": "m005",
        "text": "Food demand outlook 2024-2050: global population 9.7B by 2050. Urban population 68% by 2050 (vs 56% today) shifts demand toward processed foods (+40%). Asian middle class meat demand +70%, requiring 7x grain equivalent per protein unit. Production must increase 50% by 2030 to meet demand — current trajectory: +23%. Annual investment gap: $267B in agriculture.",
        "metadata": {"type": "demand_forecast", "horizon": "2050"},
    },
    {
        "id": "m006",
        "text": "Kazakhstan domestic food market 2024: wheat flour consumption 4.2M t/year. Domestic production surplus: 8-10M t/year in good years. Export quota 2024: 5M t. Bread price subsidised at 80 tenge/kg (market: 140 tenge). Consumer food basket inflation: +18% YoY. Retailer margin compression: -4pp. Black market flour trade: estimated 8-12% of total market.",
        "metadata": {"type": "domestic_market", "region": "Kazakhstan", "year": 2024},
    },
]

# ── Regulator documents ────────────────────────────────────────────────────────

REGULATOR_DOCS = [
    {
        "id": "r001",
        "text": "Agricultural subsidies comparison 2024: EU CAP €55B/year (€280/ha average). Russia: 3.5% GDP = $65B, enabled 35% production growth in 10 years. Kazakhstan: $1.2B (0.4% GDP), mostly fuel subsidies. IMF recommendation: shift from input subsidies to productivity investment and safety nets. Subsidy efficiency: EU €1 subsidy generates €1.8 output; Kazakhstan €1 generates €1.2 output.",
        "metadata": {"type": "subsidies_policy", "year": 2024},
    },
    {
        "id": "r002",
        "text": "Emergency food import precedents: Egypt 2022 — 500k t wheat emergency purchase (India + Russia) after $50/t price spike, cost $285M, stabilised market in 6 weeks. Turkey 2023 — 2M t duty-free import before elections, reduced bread price 22%. Kazakhstan 2021 — 300k t flour import from Russia during domestic shortage, lifted ban after 8 weeks. Ethiopia 2023 — WFP coordinated 800k t emergency via Djibouti, 14-day delivery.",
        "metadata": {"type": "emergency_import_precedents"},
    },
    {
        "id": "r003",
        "text": "Strategic grain reserves best practices: China 650M t (50% of global stocks, 150 days consumption). US: no grain reserve (relies on markets) but USDA Food Purchase Program ($2.1B). EU: 30-day reserve requirement per member state. FAO minimum: 60 days. Kazakhstan Prodkorporatsiya: 1.5M t (23 days consumption) — below FAO minimum. Recommended target: 3.2M t (50 days). Annual storage cost: $42/t.",
        "metadata": {"type": "strategic_reserves"},
    },
    {
        "id": "r004",
        "text": "Price control effectiveness study 2024: Russia 2022 sugar/oil freeze — reduced target inflation 3pp but caused 15% shortage after 4 months. Turkey 2023 subsidised shops — benefited 8.2M households, $340M cost, reduced food poverty 12%. Risk: controls >6 months create parallel markets (observed in 8 of 12 studied cases). Best practice: targeted subsidies for vulnerable households, not broad price ceilings.",
        "metadata": {"type": "price_controls_analysis"},
    },
    {
        "id": "r005",
        "text": "Human-in-the-loop food security governance: G7 Food Security Initiative 2023 — ministerial sign-off required for interventions affecting >25% deficit. WFP: executive board approval for disbursements >$500M, 72-hour emergency protocol for acute crises. UN OCHA triggers: IPC Phase 4 (Emergency) or above. Best practice: automated early warning (like this MAS) + human decision with 24-48 hour SLA. Accountability: all decisions audited and published within 30 days.",
        "metadata": {"type": "governance_hitl", "source": "G7_WFP_UN"},
    },
    {
        "id": "r006",
        "text": "Kazakhstan food policy toolkit 2024: available instruments — (1) Prodkorporatsiya reserve release (1.5M t, 2-day activation), (2) export quota reduction (3-5 day gazette), (3) import duty waiver (requires Parliament, 14-21 days), (4) direct price subsidy via KazAgro ($180M available), (5) emergency WFP coordination protocol (48-hour activation), (6) EAEU emergency food sharing mechanism (Russia, Belarus, Armenia, Kyrgyzstan).",
        "metadata": {"type": "policy_toolkit", "region": "Kazakhstan", "year": 2024},
    },
]


def seed_all():
    """Load all documents into ChromaDB. Safe to re-run (upserts by ID)."""
    logger.info("🌱 Seeding ChromaDB collections...")

    datasets = [
        ("farmer",    FARMER_DOCS),
        ("logistics", LOGISTICS_DOCS),
        ("energy",    ENERGY_DOCS),
        ("market",    MARKET_DOCS),
        ("regulator", REGULATOR_DOCS),
    ]

    for agent_name, docs in datasets:
        # Check if already seeded
        col = get_or_create_collection(agent_name)
        if col.count() >= len(docs):
            logger.info(f"⏭️  {agent_name}: already has {col.count()} docs — skipping")
            continue
        add_documents(agent_name, docs)
        logger.info(f"✅ {agent_name}: {len(docs)} documents loaded")

    logger.info("🎉 ChromaDB seeding complete!")
    logger.info("You can now run: uvicorn backend.main:app --reload")


if __name__ == "__main__":
    seed_all()