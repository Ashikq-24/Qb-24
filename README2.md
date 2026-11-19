# RAILOPT AI — End-to-End Demo & Setup Guide
**CDD Project — AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways**

---

## Table of Contents
1. [Overview & Capabilities](#overview--capabilities)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Prerequisites](#prerequisites)
4. [Step-by-Step Initial Setup (From Scratch)](#step-by-step-initial-setup-from-scratch)
   - [Step 1: Clone the Repository](#step-1-clone-the-repository)
   - [Step 2: Install Node.js Dependencies](#step-2-install-nodejs-dependencies)
   - [Step 3: Setup Python Environment for OR-Tools & Simulator](#step-3-setup-python-environment-for-or-tools--simulator)
   - [Step 4: Configure Database and Environment Variables](#step-4-configure-database-and-environment-variables)
   - [Step 5: Apply Database Migrations and Seed Data](#step-5-apply-database-migrations-and-seed-data)
5. [Starting the Application](#starting-the-application)
6. [Demo Accounts & Authentication](#demo-accounts--authentication)
7. [Full Step-by-Step Demo Walkthrough (Screen Flow)](#full-step-by-step-demo-walkthrough-screen-flow)
   - [Step 1: Login & Role Selection](#step-1-login--role-selection)
   - [Step 2: Select the Real Operations Scenario](#step-2-select-the-real-operations-scenario)
   - [Step 3: Command Center Overview](#step-3-command-center-overview)
   - [Step 4: Inspect Maintenance Demands & Critical Overdue Tasks](#step-4-inspect-maintenance-demands--critical-overdue-tasks)
   - [Step 5: Corridors & Real Infrastructure Density](#step-5-corridors--real-infrastructure-density)
   - [Step 6: Block Planning Timeline (Train Density vs. Maintenance Windows)](#step-6-block-planning-timeline-train-density-vs-maintenance-windows)
   - [Step 7: Execute Optimization Comparison (The Core Demo)](#step-7-execute-optimization-comparison-the-core-demo)
   - [Step 8: Cross-Department Bundling ("Why Were These Bundled?")](#step-8-cross-department-bundling-why-were-these-bundled)
   - [Step 9: Explainability & Diagnostics ("Why Not Scheduled?")](#step-9-explainability--diagnostics-why-not-scheduled)
   - [Step 10: What-If Contingency Simulator](#step-10-what-if-contingency-simulator)
   - [Step 11: Plan Approval & Audit Trail](#step-11-plan-approval--audit-trail)
   - [Step 12: Analytics Dashboard](#step-12-analytics-dashboard)
8. [Real Dataset Specifications](#real-dataset-specifications)
9. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Overview & Capabilities

**RAILOPT AI** is an intelligent decision-support system designed to automate railway maintenance block scheduling across three core railway departments:
- **Engineering / Permanent Way (P-Way)** — track tamping, rail renewal, turnout overhaul.
- **Traction Distribution (TRD)** — overhead equipment (OHE) inspection, cantilever replacement, power block isolation.
- **Signal & Telecommunication (S&T)** — point machine maintenance, axle counter testing, track circuit overhaul.

Instead of manual spreadsheet coordination and siloed maintenance requests, RAILOPT AI uses **Google OR-Tools CP-SAT (Constraint Programming)** along with custom greedy and priority-heuristic algorithms to:
1. Maximize scheduled maintenance workload and eliminate overdue safety risks.
2. Form **cross-departmental shadow bundles** (e.g., executing OHE repairs during track maintenance under a single unified possession).
3. Minimize passenger and freight train delays through a high-fidelity conflict simulator.
4. Provide complete **transparency and explainability** for every decision made or rejected.

---

## Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────┐
│             Web UI (Next.js 14 + Tailwind)             │
│            Runs at http://localhost:3000               │
└───────────────────────────┬────────────────────────────┘
                            │ REST / JSON
┌───────────────────────────▼────────────────────────────┐
│            Backend API (NestJS 11 + Prisma 6)          │
│            Runs at http://localhost:4000               │
│                                                        │
│  - Authentication & RBAC        - Scenario Manager     │
│  - Candidate Window Generator   - Plan Auditor         │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
      Database │                          │ Subprocess Execution
               ▼                          ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│  PostgreSQL 14+ Database │   │  Python 3.11 Subprocess  │
│  Prisma ORM schema       │   │  - OR-Tools CP-SAT       │
│  Stores runs, movements, │   │  - Greedy Solvers        │
│  requests, and plans     │   │  - Conflict Simulator    │
└──────────────────────────┘   └──────────────────────────┘
```

- **Frontend:** Next.js 14, React 18, TailwindCSS, TypeScript.
- **Backend:** NestJS 11, TypeScript, Prisma ORM 6, Passport JWT.
- **Optimization Engine:** Python 3.11, Google OR-Tools CP-SAT (`services/optimizer`).
- **Traffic Simulator:** Python 3.11 deterministic conflict resolver (`services/simulator`).
- **Database:** PostgreSQL 14+.

---

## Prerequisites

Before starting, ensure your system has:
1. **Node.js**: `v20.x` or later (`node -v`)
2. **pnpm**: `v9.x` or `v10.x` (`npm install -g pnpm`)
3. **Python**: `3.11` or compatible (`python3 --version`)
4. **PostgreSQL**: Running locally or via Docker (`psql --version` or Docker desktop)

---

## Step-by-Step Initial Setup (From Scratch)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ashikq-24/Qb-24.git
cd Qb-24
```

### Step 2: Install Node.js Dependencies
Install all monorepo workspace dependencies:
```bash
pnpm install
```

### Step 3: Setup Python Environment for OR-Tools & Simulator
Create and activate a local Python virtual environment inside the repository:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r services/optimizer/requirements.txt -r services/simulator/requirements.txt
```
> **Note for macOS / Linux:** Keep note of the absolute path to your Python binary (e.g. `$(pwd)/.venv/bin/python3`).

### Step 4: Configure Database and Environment Variables

1. **Create PostgreSQL Database & User:**
   Connect to PostgreSQL using `psql` (or pgAdmin) and run:
   ```sql
   CREATE USER railopt WITH PASSWORD 'railopt_dev_password';
   CREATE DATABASE railopt OWNER railopt;
   GRANT ALL PRIVILEGES ON DATABASE railopt TO railopt;
   ```

2. **Configure `apps/api/.env`:**
   Create or edit `apps/api/.env`:
   ```ini
   # Database connection
   POSTGRES_USER=railopt
   POSTGRES_PASSWORD=railopt_dev_password
   POSTGRES_DB=railopt
   POSTGRES_PORT=5432
   DATABASE_URL=postgresql://railopt:railopt_dev_password@localhost:5432/railopt?schema=public

   # API configuration
   API_PORT=4000
   JWT_SECRET=dev-only-change-me
   JWT_EXPIRES_IN=8h

   # Path to Python venv created in Step 3
   PYTHON_BIN=/absolute/path/to/repo/.venv/bin/python3
   OPTIMIZER_TIMEOUT_MS=60000
   SIMULATOR_TIMEOUT_MS=30000

   # Web configuration
   NEXT_PUBLIC_API_BASE_URL=http://localhost:4000
   ```
   *(Replace `/absolute/path/to/repo/.venv/bin/python3` with your actual `.venv/bin/python3` path).*

3. **Configure `apps/web/.env.local`:**
   ```ini
   NEXT_PUBLIC_API_BASE_URL=http://localhost:4000
   ```

### Step 5: Apply Database Migrations and Seed Data

1. **Deploy Prisma Migrations:**
   ```bash
   pnpm --filter @railopt/api exec prisma migrate deploy
   ```

2. **Seed Baseline Demo Users & Synthetic Scenario:**
   ```bash
   pnpm --filter @railopt/api run seed
   ```

3. **Seed Real Indian Railways Scenario (Eastern Railway Howrah–Asansol–Dhanbad):**
   ```bash
   pnpm --filter @railopt/api run seed:real
   ```
   *This seeds real station coordinates, corridors ER-01 to ER-06, overnight freight traffic, and 371 real train movements.*

---

## Starting the Application

You can run both the API and Web frontend in separate terminal windows:

### Terminal 1: Backend API
```bash
# Build the NestJS API
pnpm --filter @railopt/api run build

# Start the API server on http://localhost:4000
node apps/api/dist/main.js
```
*(Or use `pnpm --filter @railopt/api run start:dev` for live watch mode).*

### Terminal 2: Web Frontend
```bash
# Start Next.js development server on http://localhost:3000
pnpm --filter @railopt/web run dev
```

Open your browser to: **`http://localhost:3000`**

---

## Demo Accounts & Authentication

Click the **Sign In** button in the top navigation header and log in using any of the following accounts:

| Role | Email | Password | Allowed Capabilities |
| :--- | :--- | :--- | :--- |
| **Divisional Planner** *(Recommended for Demo)* | `div.planner@railopt.demo` | `railopt-demo-2026` | Run solvers, generate plans, approve plans, trigger what-if |
| **System Administrator** | `admin@railopt.demo` | `railopt-demo-2026` | Full administrative control, all views & actions |
| **Control Operator** | `control.operator@railopt.demo` | `railopt-demo-2026` | Operations monitoring, what-if triggering |
| **Field Engineer** | `field.engineer@railopt.demo` | `railopt-demo-2026` | Submit maintenance requests, view asset status |
| **Department Planner** | `dept.planner@railopt.demo` | `railopt-demo-2026` | Manage department-specific requests |
| **Management / Executive** | `management@railopt.demo` | `railopt-demo-2026` | High-level analytics, compliance, audit review |

---

## Full Step-by-Step Demo Walkthrough (Screen Flow)

Follow this sequence for an end-to-end presentation or evaluation:

### Step 1: Login & Role Selection
1. Open `http://localhost:3000`.
2. Click **Sign in** in the top right.
3. Select or enter:
   - **Email:** `div.planner@railopt.demo`
   - **Password:** `railopt-demo-2026`
4. Notice your role badge displays: **Divisional Planner (DIVISIONAL_PLANNER)**.

---

### Step 2: Select the Real Operations Scenario
In the top navigation header dropdown labeled **Scenario**, select:
> **`Eastern Railway (Howrah - Asansol - Dhanbad) Real Operations (seed 2026)`**

*(All views now sync to the real Eastern Railway corridor topology, station facilities, and live timetables).*

---

### Step 3: Command Center Overview
Navigate to **COMMAND CENTER** (`/`):
- **Executive KPI Cards:**
  - Total Maintenance Requests: **12**
  - Critical Overdue Requests: **2**
  - Available Block Windows: **10**
  - Corridors Under Monitoring: **6**
- **Corridor Asset Readiness:** View live status across Howrah–Barddhaman, Durgapur, Asansol, and Dhanbad trunk routes.
- **Pending Actions:** High-priority track & OHE items requiring divisional clearance.

---

### Step 4: Inspect Maintenance Demands & Critical Overdue Tasks
Navigate to **MAINTENANCE** (`/maintenance`):
1. Notice requests coming from all three departments:
   - `ENGINEERING` (Track tamping, ultrasonic rail flaw testing, rail joint renewal).
   - `TRD` (OHE contact wire replacement, insulator washing).
   - `S_AND_T` (Axle counter overhaul, track circuit replacement).
2. Click the filter button **"Overdue only"**:
   - Notice the high-criticality items flagged in red (`CRITICAL` urgency).
3. Click on any request (e.g., `OHE Contact Wire Replacement` or `Track Tamping`):
   - Review **Isolations Required**: Traction power shutdown (`TRD_POWER_BLOCK`), Traffic possession (`TRAFFIC_BLOCK`).
   - Review **Asset & Track Details**: Corridor segment, speed restrictions, and estimated task duration.

---

### Step 5: Corridors & Real Infrastructure Density
Navigate to **CORRIDORS** (`/corridors`):
1. Review the real 6 Eastern Railway corridor segments:
   - `ER-01`: Howrah Junction (`HWH`) to Barddhaman (`BWN`) Main Line
   - `ER-02`: Howrah (`HWH`) to Barddhaman (`BWN`) Chord Line
   - `ER-03`: Barddhaman (`BWN`) to Durgapur (`DGR`) Main Trunk Route
   - `ER-04`: Durgapur (`DGR`) to Asansol (`ASN`) Industrial Corridor
   - `ER-05`: Asansol (`ASN`) to Barakar (`BRR`) Section
   - `ER-06`: Barakar (`BRR`) to Dhanbad (`DHN`) Grand Chord
2. Inspect the station facility tags, double/quadruple track layouts, and speed limits (110–130 km/h).

---

### Step 6: Block Planning Timeline (Train Density vs. Maintenance Windows)
Navigate to **BLOCK PLANNING** (`/block-planning`):
1. View the interactive Gantt timeline:
   - **Gray Bars:** Maintenance block opportunities where tracks can be possessed.
   - **Blue Bars:** Scheduled passenger, mail/express, and local EMU trains.
   - **Purple / Dark Bars:** High-tonnage freight movements (`BOXN-NIGHT`, `BCN-NIGHT`).
2. Point out how high daytime train density makes midday maintenance impossible without incurring severe delays, creating natural night possession windows between 01:00 AM and 05:00 AM.

---

### Step 7: Execute Optimization Comparison (The Core Demo)
Navigate to **OPTIMIZATION** (`/optimization`). This is the centerpiece of the system.

You will see three solver execution buttons:
1. **RUN FIRST FEASIBLE**
   - Click this button.
   - The naive greedy solver schedules the first matching available window for each task in FIFO order.
   - *Result:* Schedules 10 tasks, but creates **0 bundles** and causes high train delays (**750 minutes**).
2. **RUN PRIORITY FIRST**
   - Click this button.
   - The priority heuristic sorts tasks by criticality, overdue penalties, and risk weight.
   - *Result:* Higher objective score (**888.7**), reduced train delay (**660 minutes**), but limited cross-departmental coordination.
3. **RUN RAILOPT OPTIMIZED**
   - Click this button.
   - The **Google OR-Tools CP-SAT** mathematical constraint model optimizes simultaneously for:
     - Priority scores & overdue penalties
     - Cross-departmental task bundling
     - Minimization of simulated train delays
   - *Result:*
     - **Highest Objective Value:** `890.7`
     - **Cross-Departmental Bundles:** `1 bundle` formed
     - **Train Delay:** Minimized down to `660 minutes`
     - **Solve Time:** Sub-second execution (~7–15 ms)

#### Optimization Results Benchmark Table:
| Strategy | Objective Score | Tasks Scheduled | Critical Scheduled | Bundles Formed | Total Train Delay | Solve Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **First Feasible** *(Naive)* | 882.2 | 10 / 12 | 2 / 2 | 0 | 750 min | 1 ms |
| **Priority First** *(Heuristic)* | 888.7 | 10 / 12 | 2 / 2 | 1 | 660 min | 1 ms |
| **RAILOPT Optimized** *(OR-Tools)* | **890.7** | **10 / 12** | **2 / 2** | **1** | **660 min** | **7 ms** |

---

### Step 8: Cross-Department Bundling ("Why Were These Bundled?")
1. Return to **BLOCK PLANNING** (`/block-planning`).
2. Select the **RAILOPT Optimized** plan from the Plan dropdown.
3. Observe the scheduled blocks. Look for the **green "BUNDLE" badge** on Corridor `ER-03`.
4. Click on the bundled block:
   - Notice that both a **P-Way Track Tamping** job and a **TRD OHE Inspection** are scheduled in the *exact same window on the same track segment*.
   - Because track tamping already requires a full traffic possession and overhead clearance, scheduling them together saves a redundant 3-hour track shutdown!
5. Open **MAINTENANCE** and inspect one of the bundled tasks:
   - The **"Why Scheduled?"** panel explicitly displays:
     > `Bundled with TRD-2026-004 (compatible cross-department task in the same corridor window)`.

---

### Step 9: Explainability & Diagnostics ("Why Not Scheduled?")
1. In **MAINTENANCE**, find one of the unscheduled tasks (e.g. `S&T Axle Counter Overhaul`).
2. Click to open its details panel.
3. Read the **"Why Not Scheduled?"** explanation card:
   - Displays the exact constraint reason:
     - `RESOURCE_UNAVAILABLE` (crew/machine quota exceeded for the shift), or
     - `OPERATIONAL_CONFLICT` (scheduling this lower-priority task would delay express passenger trains beyond tolerance threshold).
   - Shows the exact priority score breakdown and weights.

---

### Step 10: What-If Contingency Simulator
Navigate to **WHAT-IF** (`/what-if`):
1. **Scenario Simulation:** Test how the network reacts to sudden real-world disruptions.
2. Select Event Type: **Corridor becomes unavailable** (e.g., emergency derailment or broken rail).
3. Select Corridor: `ER-03 - Barddhaman to Durgapur Main Trunk Route`.
4. Click **TRIGGER WHAT-IF**.
5. **Instant Re-Optimization & Comparison:**
   - The engine automatically runs two parallel solver passes:
     - **Base Plan (Before Disruption)**
     - **Re-Optimized Plan (After Disruption)**
   - The **DELTA Comparison Cards** display:
     - Change in scheduled tasks
     - Impact on train delays
     - Re-routed or deferred maintenance tasks
   - Provides dispatchers with immediate contingency planning in seconds without human guesswork.

---

### Step 11: Plan Approval & Audit Trail
1. Return to **OPTIMIZATION** (`/optimization`).
2. Next to the **RAILOPT Optimized** row, click **Approve**.
3. The plan revision is now locked and marked **APPROVED**:
   - The record becomes immutable in PostgreSQL.
   - Attempting to approve or reject again returns an HTTP 409 Conflict error.
4. Navigate to **AUDIT** (`/audit`):
   - Review the complete cryptographically-traceable audit log:
     - Timestamp
     - User identity (`div.planner@railopt.demo`)
     - Action type (`PLAN_APPROVED`)
     - Solver version, parameters, and seed used.

---

### Step 12: Analytics Dashboard
Navigate to **ANALYTICS** (`/analytics`):
- **Department Allocation:** Visual breakdown of maintenance hours granted across P-Way, TRD, and S&T.
- **Delay vs. Asset Availability Curve:** Trade-off analysis between train punctuality and track health.
- **Solver Performance:** Benchmarks of CP-SAT execution times and optimality gap.

---

## Real Dataset Specifications

The project includes pre-configured real data extracted and synthesized from official railway data sources:

1. **Stations & Geolocation Data:**
   - Sourced from Kaggle Indian Railway Stations dataset (`shraddha4ever20`).
   - Includes official railway station codes, names, latitudes, longitudes, and division classifications:
     - `HWH` (Howrah Junction, 22.5839° N, 88.3426° E)
     - `BWN` (Barddhaman Junction, 23.2324° N, 87.8615° E)
     - `DGR` (Durgapur, 23.4988° N, 87.3119° E)
     - `ASN` (Asansol Junction, 23.6889° N, 86.9661° E)
     - `DHN` (Dhanbad Junction, 23.7917° N, 86.4304° E)

2. **Train Timetables & Movement Data:**
   - Sourced from IIT Kharagpur RSTGCN September 2024 train movement datasets (`KoyenaChowdhury/RSTGCN`).
   - Models realistic passenger traffic across Eastern Railway's Howrah–Asansol–Dhanbad trunk.
   - Supplemented with overnight freight traffic corridors (`BOXN-NIGHT`, `BCN-NIGHT`) to reproduce authentic midnight freight paths and track possession conflicts.

---

## Troubleshooting & FAQ

### 1. Port 3000 or Port 4000 is already in use
Run the following command to free the ports:
```bash
lsof -ti:3000,4000 | xargs -r kill -9
```

### 2. Prisma Connection Error (`User was denied access` or database does not exist)
Ensure your PostgreSQL server is active and the `railopt` database exists:
```bash
# Connect with your superuser (postgres)
psql -U postgres -c "CREATE USER railopt WITH PASSWORD 'railopt_dev_password';"
psql -U postgres -c "CREATE DATABASE railopt OWNER railopt;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE railopt TO railopt;"
```

### 3. Solver Error: `python3: command not found` or `ModuleNotFoundError: No module named 'ortools'`
Check that `PYTHON_BIN` in `apps/api/.env` points to your activated `.venv` python executable:
```bash
# Verify virtualenv packages
source .venv/bin/activate
python3 -c "import ortools; print(ortools.__version__)"
which python3
```
Copy that path into `apps/api/.env` under `PYTHON_BIN`.

### 4. How to re-seed or reset data?
To reset and re-seed the real operations scenario:
```bash
pnpm --filter @railopt/api run seed:real
```

---

*RAILOPT AI is a decision-support and planning system developed as part of the CDD Project.*
