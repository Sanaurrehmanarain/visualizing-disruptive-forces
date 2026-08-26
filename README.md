<div align="center">
  <a href="ProjectReport.pdf">
    <img src="banner.svg" alt="ProjectBanner" width="100%">
  </a>
  <p><em>Click the banner to view the full analysis report</em></p>
</div>

# Visualizing Disruptive Forces in the Global Banking Network: A Multi-Lens Analysis of the 2008 Financial Crisis

## Introduction
The 2008–09 global financial crisis demonstrated that modern financial architecture cannot be fully understood through traditional macroeconomic indicators alone. Instead, global finance operates as a complex, adaptive system where distress in a specific asset class can trigger a catastrophic global collapse. 

This project systematically applies three distinct analytical lenses to empirical banking data to understand how localized shocks propagate through the international system:
1. **Network Cartography:** Mapping the structural topology to identify highly connected hubs, peripheral nodes, and critical bridges.
2. **Causal Inference:** Analyzing temporal dynamics and exposure distributions to distinguish genuine sequential contagion from simultaneous common exposures, isolating nonlinear phase transitions.
3. **Strategic-Behavioral Game Theory:** Modeling the rational, self-preserving incentives of major banking hubs that inadvertently lead to cross-border bank runs.

By overlaying these three methodologies, this project pinpoints the **"Triple-Point"**—the specific nodes where extreme structural connectivity, lethal causal pathways, and strategic hoarding intersect.

---

## Data Source
We utilized the **Bank for International Settlements (BIS) Consolidated Banking Statistics (Table B4)** to construct a quarterly network of positive reported international claims on an immediate-counterparty basis. 
* **Nodes:** Reporting and counterparty countries.
* **Edges:** Directed, weighted positive claims outstanding in USD millions.
* **Timeframe:** 2007-Q1 through 2010-Q4.

---

## Results & Visualizations

### 1. Network Topology (Structural Core & Hubs)
The global banking network exhibits an extreme core-periphery architecture centralized around European financial centers. France and the United Kingdom function as hyper-connected financial super-spreaders, mediating massive gross international claims.

![Global Cross-Border Banking Network Topology](figures/fig_a1_network_topology.png)

**Table A1: Empirical Node Metrics (2008-Q1)**

| Country (Node) | Network Role | Out-Degree | In-Degree | Betweenness | Total Outward Claims (USD Millions) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **France** | Core Hub / Bridge | 186 | 21 | 0.0150 | $2,498,736 |
| **United Kingdom** | Core Hub / Bridge | 183 | 22 | 0.0170 | $2,089,045 |
| **Belgium** | Core Hub / Bridge | 162 | 19 | 0.0092 | $1,022,563 |
| **Spain** | Core Hub / Bridge | 154 | 21 | 0.0087 | $471,658 |
| **Chinese Taipei**| Regional Hub | 130 | 12 | 0.0042 | $165,207 |
| **Italy** | Bridge / Intermediary| 124 | 20 | 0.0050 | $749,874 |

### 2. Nonlinear & Asymmetric Risk
The network is subject to severe nonlinear crashes and fat-tailed risk distributions. Just **1% of all cross-border lending connections held over 34% of the entire world's financial exposure** in 2008-Q1. 

![Nonlinear Systemic Shock](figures/fig_b1_nonlinear_shock_timeline.png)
![Asymmetric Exposure Distribution](figures/fig_b2_fat_tail_distribution.png)

### 3. Strategic Coordination Failure (The Bank Run)
The massive drop in cross-border lending was not merely mechanical; it was a strategic choice. Faced with uncertainty, major hubs engaged in a Prisoner's Dilemma, executing simultaneous capital flight from the United States to protect themselves, which inadvertently starved the global periphery of liquidity.

![Strategic Coordination Failure](figures/fig_c1_strategic_withdrawal.png)

### 4. Integration: The Triple-Point Overlay
By intersecting the three lenses, we identify the **United Kingdom** as the ultimate systemic bottleneck (The Triple-Point). It operates simultaneously as a structural hub, a link in the primary causal cascade, and a strategic hoarding actor.

![Disruptive Forces Overlay Map](figures/fig_2a_overlay_map.png)

This vulnerability is a universal structural pattern, behaving identically to hoarding cascades seen in global supply chains (e.g., the semiconductor shortage).

![Cross-Domain Supply Chain](figures/fig_2c_supply_chain_domain.png)

---

## Conclusion and Policy Recommendation
Assessing the network holistically reveals a severe trade-off between structural circuit breakers and strategic behavior. Imposing strict capital freezes triggers behavioral panics (bank runs). 

**Recommendation:** Regulate banks based on their physical location within the global network. Institutions operating in "Triple-Point" jurisdictions must be subjected to automated, mandatory liquidity reserves (Asymmetric Capital Surcharges) that scale with their level of network Betweenness Centrality, ensuring they have the capital to absorb shocks without triggering a global withdrawal cascade.

![The Systemic Bottleneck Briefing](figures/fig_step4_briefing_visual.png)

---

## Citation

If you use this project in academic research, publications, educational
materials, or derivative works, please cite it and provide appropriate
credit to the original author. A [`CITATION.cff`](CITATION.cff) file is included, so GitHub also provides a **"Cite this repository"** button in the sidebar (BibTeX, APA, and other formats).

**Suggested citation:**

> Arain, S. U. R. (2026). *Visualizing Disruptive Forces in the Global
Banking Network: A Multi-Lens Analysis of the 2008 Financial Crisis* (Version 1.0) [Software]. https://github.com/Sanaurrehmanarain/visualizing-disruptive-forces

| | |
|---|---|
| **Author** | Sana Ur Rehman Arain |
| **Role** | Data Scientist |
| **GitHub** | [@sanaurrehmanarain](https://github.com/sanaurrehmanarain) |
| **Contact** | sana.arain.work@gmail.com |

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details. The license requires that the original copyright notice be retained in copies of the software.

---

<p align="center">
⭐ If this project was useful to you, consider starring the repo — it helps others discover it and supports future work.
</p>