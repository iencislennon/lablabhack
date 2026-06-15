"""
vector_db/seed_data.py — Load realistic seed documents into ChromaDB.
Run once before starting the system:
    python -m backend.vector_db.seed_data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.vector_db.setup import add_documents
from loguru import logger


# ── Farmer agent documents ─────────────────────────────────────────────────────

FARMER_DOCS = [
    {
        "id": "f001",
        "text": "Kazakhstan wheat harvest 2023: 16.5 million tonnes, down 8% from average due to drought in May–June. Key deficit regions: Akmola oblast (-22%), Kostanay oblast (-18%). 2024 forecast: expected recovery to 17.8 million tonnes under normal rainfall conditions.",
        "metadata": {"year": 2023, "crop": "wheat", "region": "Kazakhstan", "type": "yield_report"},
    },
    {
        "id": "f002",
        "text": "Agricultural climate report 2024: Drought risk in Central Asia has risen to 65% during summer months. Regions facing critical water stress: southern Uzbekistan, Turkmenistan, southern Kazakhstan. Recommended action: transition to drought-resistant wheat and maize varieties.",
        "metadata": {"year": 2024, "type": "climate_risk", "region": "Central_Asia"},
    },
    {
        "id": "f003",
        "text": "Ukraine corn production 2023: 28.3 million tonnes (-12% vs 2022). Causes: ongoing conflict, 15% reduction in planted area, fertiliser supply disruptions. Export potential dropped to 18 million tonnes. Key global risk: shortage of feed grain.",
        "metadata": {"year": 2023, "crop": "corn", "region": "Ukraine", "type": "production_report"},
    },
    {
        "id": "f004",
        "text": "Rice: Southeast Asia production 2024. Thailand — 32 million tonnes (+3%), Vietnam — 27 million tonnes (stable). India introduced export restrictions, creating a global market shortfall of 8–10 million tonnes. Rice prices surged 40% since early 2023.",
        "metadata": {"year": 2024, "crop": "rice", "region": "Southeast_Asia", "type": "production_report"},
    },
    {
        "id": "f005",
        "text": "FAO Food Security Index 2024: 47 countries face food deficits exceeding 20%. Sub-Saharan Africa — 31 countries in critical condition. Middle East: grain import dependency at 70–90%. Urgent international intervention required.",
        "metadata": {"year": 2024, "type": "food_security_index", "source": "FAO"},
    },
    {
        "id": "f006",
        "text": "Fertiliser shortage 2023–2024: nitrogen fertiliser production fell 25% due to high gas prices. Russia and Belarus, under sanctions, cut potash deliveries by 35%. This is projected to reduce yields by 8–15% in the next growing season.",
        "metadata": {"year": 2024, "type": "fertilizer_shortage", "impact": "yield_reduction"},
    },
]

# ── Logistics agent documents ──────────────────────────────────────────────────

LOGISTICS_DOCS = [
    {
        "id": "l001",
        "text": "Black Sea grain corridor: capacity 3 million tonnes/month through Odesa, Chornomorsk, and Yuzhne ports. After the grain deal collapsed in 2023, throughput fell by 60%. Alternative route via Romania and Poland: +12–15 days transit, cost premium +$45/tonne.",
        "metadata": {"region": "Black_Sea", "type": "route_analysis", "year": 2023},
    },
    {
        "id": "l002",
        "text": "Grain transport losses in Central Asia: average losses of 8–12% of volume when stored more than 3 months under high temperatures. Main causes: outdated elevators (60% built before 1990), rodents, humidity. Modern silos reduce losses to 2–3%.",
        "metadata": {"region": "Central_Asia", "type": "loss_analysis"},
    },
    {
        "id": "l003",
        "text": "Kazakhstan rail grain capacity: 52,000 grain wagons, throughput 18 million tonnes/year. Bottlenecks: China border crossing at Dostyk (15 million t/year), Aktogay station — delays up to 8 days. Caspian sea route via Aktau: 5 million t/year, utilisation at 95%.",
        "metadata": {"region": "Kazakhstan", "type": "rail_capacity"},
    },
    {
        "id": "l004",
        "text": "Turkey grain storage capacity: 30 million tonnes licensed, 18–20 million tonnes effectively available. Storage cost: $8–12/tonne per month. TMO strategic reserve (Toprak Mahsulleri Ofisi): 7.2 million tonnes. Port of Mersin — key transhipment hub for the Middle East.",
        "metadata": {"region": "Turkey", "type": "storage_capacity"},
    },
    {
        "id": "l005",
        "text": "Suez Canal: 12% of global grain trade. Houthi attacks in 2024 increased transit time via Cape of Good Hope by 14–18 days. Insurance premiums rose 300%. Impact: delivery cost from Argentina and USA to Asia up $30–50/tonne.",
        "metadata": {"region": "Suez_Canal", "type": "route_disruption", "year": 2024},
    },
]

# ── Energy agent documents ─────────────────────────────────────────────────────

ENERGY_DOCS = [
    {
        "id": "e001",
        "text": "Agricultural electricity prices in Europe 2024: average €0.18/kWh, peaking at €0.31/kWh in winter. Irrigation accounts for 30% of agri energy consumption; refrigerated grain storage adds 25% to costs. Germany subsidises farmers: 30% rebate on electricity bills.",
        "metadata": {"region": "Europe", "type": "energy_prices", "year": 2024},
    },
    {
        "id": "e002",
        "text": "Energy crisis impact on fertilisers: ammonia production requires 8–12 MWh per tonne. At gas prices above €50/MWh, production becomes uneconomical. In 2022–2023, 30% of European nitrogen fertiliser capacity shut down. Result: 15 million tonne urea shortfall on the world market.",
        "metadata": {"type": "energy_impact_fertilizers", "year": 2023},
    },
    {
        "id": "e003",
        "text": "Kazakhstan grid status 2024: peak load 15.8 GW against installed capacity of 19.2 GW (82%). Winter deficit in northern regions up to 8%. Equipment wear rate 65%. In 2024, three emergency outages lasting 4–12 hours each affected 2.1 million people.",
        "metadata": {"region": "Kazakhstan", "type": "grid_status", "year": 2024},
    },
    {
        "id": "e004",
        "text": "Renewable energy in agriculture: solar-powered irrigation pumps cut costs by 60–70% vs diesel. Turkey reached 35% renewable share in 2024. Wind installations in Kazakhstan cover 8% of electricity demand. By 2030, 50% renewables could reduce food production costs by 12–18%.",
        "metadata": {"type": "renewable_energy", "year": 2024},
    },
    {
        "id": "e005",
        "text": "Critical infrastructure: the food cold chain consumes 17% of all electricity in the food industry. A 24-hour power outage destroys 20–35% of perishable stock. In Ukraine in 2023, grid attacks caused losses of 12% of the harvest due to storage failure.",
        "metadata": {"type": "critical_infrastructure", "year": 2023},
    },
]

# ── Market agent documents ─────────────────────────────────────────────────────

MARKET_DOCS = [
    {
        "id": "m001",
        "text": "CBOT wheat prices 2024: January $220/t, March $195/t, June $180/t. Decline driven by record Russian harvest (90 million t) and increased Australian supply (+15%). Price support: African deficit, India export ban. Q3 2024 forecast: $165–185/t.",
        "metadata": {"commodity": "wheat", "type": "price_history", "year": 2024},
    },
    {
        "id": "m002",
        "text": "Global grain stocks 2024: wheat 310 million tonnes (104 days of cover), corn 290 million tonnes (60 days), rice 180 million tonnes (90 days). Critical threshold: below 60 days. Corn is approaching the critical level due to high US biofuel demand.",
        "metadata": {"type": "global_stocks", "year": 2024, "source": "USDA"},
    },
    {
        "id": "m003",
        "text": "Speculative activity in grain markets: COT (Commitment of Traders) net-long speculators on wheat reached their highest level since 2022 in March 2024. Algorithmic trading accounts for 70% of volume. During geopolitical instability, speculators amplify volatility by 25–35%.",
        "metadata": {"type": "market_speculation", "year": 2024},
    },
    {
        "id": "m004",
        "text": "Food inflation 2024: FAO global food price index at 118.5 points (2014–2016=100). Highest food inflation: Argentina +214% YoY, Turkey +65% YoY, Egypt +50% YoY. Key drivers: weak national currencies, elevated transport costs.",
        "metadata": {"type": "food_inflation", "year": 2024, "source": "FAO"},
    },
    {
        "id": "m005",
        "text": "Food demand outlook: global population will reach 9.7 billion by 2050. Urbanisation increases demand for processed foods by 40%. Rising middle class in Asia will increase meat consumption by 70%, requiring 7x more grain per unit of protein. Production must increase 50% by 2030.",
        "metadata": {"type": "demand_forecast", "horizon": "2030-2050"},
    },
]

# ── Regulator agent documents ──────────────────────────────────────────────────

REGULATOR_DOCS = [
    {
        "id": "r001",
        "text": "EU agricultural subsidies 2024: Common Agricultural Policy (CAP) — €55 billion/year. Direct payments to farmers: €200–300/ha. Eco-schemes: 25% of budget. Russia subsidises agriculture at 3.5% of GDP, which enabled a 35% production increase over 10 years.",
        "metadata": {"type": "subsidies_policy", "region": "EU_Russia", "year": 2024},
    },
    {
        "id": "r002",
        "text": "Emergency food import precedents: Egypt 2022 — emergency purchase of 500,000 tonnes of wheat from India and Russia after a price spike. Turkey 2023 — duty-free import of 2 million tonnes of grain to stabilise prices before elections. Kazakhstan 2024 — import quota of 300,000 tonnes of flour from Russia.",
        "metadata": {"type": "emergency_import_precedents"},
    },
    {
        "id": "r003",
        "text": "Strategic grain reserves: China holds 650 million tonnes (50% of global stocks). The US lacks a grain equivalent of the Strategic Petroleum Reserve but operates the USDA Food Purchase Program. Kazakhstan's Prodkorporatsiya manages a 1.5 million tonne reserve. FAO recommends a minimum of 60 days of consumption.",
        "metadata": {"type": "strategic_reserves", "source": "FAO"},
    },
    {
        "id": "r004",
        "text": "Anti-inflation measures in the food sector: Russia 2022 — price freeze on sugar and sunflower oil for 6 months (reduced inflation by 3 pp). Turkey 2023 — subsidised shops for low-income households, saving families 30–40% of their food budget. Risk: supply shortfall if price controls persist too long.",
        "metadata": {"type": "anti_inflation_measures"},
    },
    {
        "id": "r005",
        "text": "Human-in-the-loop in food security policy: G7 Food Security Initiative 2023 — early-warning system requiring ministerial sign-off when deficit exceeds 25%. WFP requires executive board approval for disbursements above $500 million. Principle: algorithms recommend, humans decide.",
        "metadata": {"type": "governance_principles", "source": "G7_WFP"},
    },
]


def seed_all():
    logger.info("🌱 Seeding ChromaDB with realistic data...")

    add_documents("farmer", FARMER_DOCS)
    logger.info(f"✅ Farmer: {len(FARMER_DOCS)} documents")

    add_documents("logistics", LOGISTICS_DOCS)
    logger.info(f"✅ Logistics: {len(LOGISTICS_DOCS)} documents")

    add_documents("energy", ENERGY_DOCS)
    logger.info(f"✅ Energy: {len(ENERGY_DOCS)} documents")

    add_documents("market", MARKET_DOCS)
    logger.info(f"✅ Market: {len(MARKET_DOCS)} documents")

    add_documents("regulator", REGULATOR_DOCS)
    logger.info(f"✅ Regulator: {len(REGULATOR_DOCS)} documents")

    logger.info("🎉 ChromaDB seeding complete!")


if __name__ == "__main__":
    seed_all()