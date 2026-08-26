# Project Tasks and Milestones

### 1. Data Preprocessing & Data Engineering
- [x] Process raw BIS Consolidated Banking Statistics (Table B4) bulk downloads.
- [x] Filter dimensions for positive outstanding claims, immediate-counterparty basis, and domestic banks.
- [x] Clean and handle missing values without artificially imputing zeroes.
- [x] Reshape wide data to long format to construct a directed edge list for 2007-2010.

### 2. Network Cartography (Structural Analysis)
- [x] Construct directed graph (DiGraph) of the 2008-Q1 global banking network using `networkx`.
- [x] Calculate Out-Degree to identify the top 5 global lending hubs.
- [x] Calculate Betweenness Centrality to identify inter-regional bridges.
- [x] Identify peripheral nodes and visualize structural fragility.
- [x] Evaluate the Connection-Cascade trade-off.

### 3. Causal Analysis (Nonlinear & Asymmetric Risk)
- [x] Track global claims over time to visualize nonlinear phase transitions (hockey-stick curve).
- [x] Plot log-scale distributions to prove extreme asymmetric risk (top 1% holding 34% of global exposure).
- [x] Trace causal sequence paths ($A \rightarrow B \rightarrow C$) vs. common exposures.
- [x] Apply the legal "but for" test to determine causality of the network collapse.

### 4. Strategic-Behavioral Game Theory
- [x] Model the 2008 crash as a coordination failure / Prisoner's Dilemma.
- [x] Extract empirical withdrawal data to prove strategic herding and cross-border capital flight.
- [x] Evaluate the moral hazard consequences of Central Bank Liquidity Swap line interventions.

### 5. Integration and Policy Evaluation
- [x] Generate an Overlay Map integrating Structural Hubs, Cascade Paths, and Strategic Actors.
- [x] Isolate the "Triple-Point" bottleneck (The United Kingdom).
- [x] Map the banking topology to a secondary domain (Global Supply Chains).
- [x] Produce an executive-level visual briefing communicating systemic concentration risk.