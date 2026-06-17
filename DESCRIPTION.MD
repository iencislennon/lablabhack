# FoodEnergyMAS — Project Description

## The Problem

Every year, food and energy crises claim lives and destabilize economies — not because the warning signs weren't there, but because the information needed to act was scattered across too many systems, too many experts, and too many spreadsheets. By the time analysts compile reports from agriculture ministries, energy agencies, logistics operators, and commodity markets, the window for early intervention has often already closed.

The challenge is not data — it is synthesis. How do you bring together crop forecasts, energy grid data, shipping disruptions, and market prices into a single coherent picture fast enough to actually do something about it?

---

## What We Built

**FoodEnergyMAS** is a multi-agent AI system that acts as a virtual crisis response team. You describe a situation in plain language — a drought, an energy price spike, a shipping disruption, or a combination of all three — and the system immediately deploys five specialised AI agents that analyse the problem simultaneously, each from their own domain.

Within minutes, the system produces a structured policy recommendation backed by real data, with a full audit trail of every decision and a downloadable PDF report ready to share with decision-makers.

---

## How It Works

### Step 1 — You describe the crisis

You type a scenario into the dashboard. It can be as simple as *"Drought in Central Asia reduced wheat harvest by 25%"* or as complex as a multi-paragraph geopolitical situation assessment.

### Step 2 — Five agents analyse in parallel

The system deploys five AI agents simultaneously:

**🌾 The Farmer Agent** looks at crop yields, climate risks, and which specific regions are running short on food. It draws on a knowledge base containing historical harvest data, FAO reports, and climate risk assessments for Central Asia and beyond.

**🚛 The Logistics Agent** maps out supply chain routes, identifies bottlenecks — blocked ports, overloaded rail lines, inadequate storage — and estimates how much food is being lost in transit. It knows about the Black Sea grain corridor, the Suez Canal, and key overland routes.

**⚡ The Energy Agent** analyses electricity prices, grid stability, and how energy problems cascade into food production. A power outage doesn't just affect homes — it disrupts irrigation, cold storage, and food processing. This agent tracks those connections.

**📈 The Market Agent** monitors commodity prices, demand signals, stock levels measured in days of supply, and whether speculative trading is distorting real market signals. It flags when markets are behaving irrationally and prices no longer reflect supply reality.

**🏛️ The Regulator Agent** reads everything the other four agents have produced and issues the final policy recommendation — which subsidies to activate, whether emergency imports are needed, whether strategic reserves should be released, and whether price controls are warranted.

### Step 3 — Conflicts are detected automatically

This is where FoodEnergyMAS does something no single analyst can do at speed. The system's coordinator reads all five agent outputs and checks for contradictions. For example:

- The Market Agent says prices are stable — but the Farmer Agent reports a 34% deficit in key regions. That is a conflict. It gets flagged.
- The Logistics Agent says routes are clear — but the Energy Agent reports critical grid failures along those same routes. That is a conflict. It gets flagged.

These conflicts are surfaced to the decision-maker with a clear explanation.

### Step 4 — Escalation to a human when needed

The system knows when it is not confident enough to act. It automatically escalates to a human when:

- Its confidence score falls below 70%
- A regional food deficit exceeds 30%
- An energy shortage reaches critical level
- Food stock levels drop below 14 days of supply

When escalation happens, the report clearly states the reason and marks the decision for human review.

### Step 5 — A report lands in your hands

The system generates a professional PDF report containing: crop forecasts by region, logistics route plans with costs and timelines, price recommendations per commodity, subsidy proposals with budget estimates, import trigger assessments, and a full audit trail showing exactly what each agent found and why the regulator decided what it did.

---

## Why This Matters

### Speed
A traditional inter-agency analysis of a food and energy crisis takes days to weeks. FoodEnergyMAS produces a first-pass assessment in minutes. This is not a replacement for human expertise — it is a tool that ensures human experts start from a position of synthesised, conflict-checked information rather than raw data.

### Cross-domain thinking
Food crises are never just about food. They are about energy costs making irrigation unaffordable. They are about shipping disruptions that block grain from reaching deficit regions. They are about speculative trading that disconnects prices from reality. FoodEnergyMAS analyses all of these simultaneously and finds the connections between them automatically.

### Transparency
Every decision in the system is logged. The PDF report shows not just what the system recommended, but what each agent found, what conflicts were detected, and what confidence level the system had. Decision-makers can interrogate the reasoning, not just the conclusion.

### Human oversight built in
The system is designed around the principle that algorithms recommend and humans decide. Escalation thresholds are configurable. The system never takes action — it produces recommendations. The human always has the final word.

---

## Real-World Application

FoodEnergyMAS is designed to be useful in:

- **Government ministries** (agriculture, energy, trade) during early-warning situations
- **International organisations** (UN WFP, FAO, World Bank) for rapid situation assessment
- **Humanitarian NGOs** planning emergency food distribution
- **Central banks and finance ministries** monitoring food inflation risks
- **Strategic consulting firms** advising governments on crisis preparedness

---

## The Technology, Simply Explained

The system uses a technique called **Retrieval-Augmented Generation (RAG)**. Before each agent calls an AI language model, it searches a database of real documents — harvest reports, energy statistics, logistics data, market analyses — and pulls the most relevant information. This means agents reason from actual data, not from the model's general training knowledge alone.

The agents coordinate through **Band AI**, a platform designed specifically for multi-agent collaboration. Think of it as a shared workspace where agents can read each other's findings before the regulator makes its final call.

Reports are generated as professional PDFs using the same rendering technology used by many government and legal document systems.

---

## What It Is Not

FoodEnergyMAS is not a fully autonomous decision system. It does not send emails, trigger procurement orders, or contact suppliers. It produces analysis and recommendations. All action remains with the human operators who review the output.

It is also not a replacement for domain experts. It is a tool that makes expert time more valuable by handling the synthesis work that currently consumes most of it.

---

## Built At

**lablab.ai Hackathon — Band AI Track, June 2026**

**Team:** Ansar Tleubayev

**Contact:** [github.com/iencislennon/lablabhack](https://github.com/iencislennon/lablabhack)
