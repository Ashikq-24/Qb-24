import json
import uuid
import datetime
import pandas as pd
from datetime import datetime, timedelta

# Load datasets
df_stations = pd.read_csv("data/real/railway_stations.csv")
df_routes = pd.read_csv("data/real/Indian-Railway-Network-and-Delays/train_routes_Sep2024.csv")
df_edges = pd.read_csv("data/real/Indian-Railway-Network-and-Delays/IRN_edges.csv")

SCENARIO_ID = "e81d7a9b-3c4f-4d2a-9f1e-8b6a5c4d3e2f"
CONFIG_VERSION = "v1"
GENERATED_AT = "2026-09-05T00:00:00.000Z"
SEED = 2026

def make_uuid(prefix, key):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"railopt.er.{prefix}.{key}"))

# 1. Divisions
divisions = [
    {
        "id": make_uuid("div", "ER-HWH"),
        "code": "ER-HWH",
        "name": "Eastern Railway - Howrah Division"
    },
    {
        "id": make_uuid("div", "ER-ASN"),
        "code": "ER-ASN",
        "name": "Eastern Railway - Asansol Division"
    }
]
div_hwh_id = divisions[0]["id"]
div_asn_id = divisions[1]["id"]

# 2. Stations (from Kaggle railway_stations.csv with real lat/lng)
stn_codes = ["HWH", "DKAE", "KQU", "BWN", "DGR", "RNG", "ASN", "DHN"]
stn_rows = df_stations[df_stations["station_code"].isin(stn_codes)].drop_duplicates("station_code")

stations = []
stn_id_map = {}
for _, row in stn_rows.iterrows():
    code = row["station_code"]
    stn_id = make_uuid("stn", code)
    stn_id_map[code] = stn_id
    div_id = div_hwh_id if code in ["HWH", "DKAE", "KQU", "BWN"] else div_asn_id
    stations.append({
        "id": stn_id,
        "code": code,
        "name": f"{row['station_name']} (Real)",
        "divisionId": div_id,
        "latitude": round(float(row["lat"]), 6),
        "longitude": round(float(row["lng"]), 6)
    })

# 3. Corridors & Segments
corridors_def = [
    {
        "code": "ER-01",
        "name": "Howrah - Barddhaman Main Line",
        "divisionId": div_hwh_id,
        "orig": "HWH",
        "dest": "BWN",
        "lengthKm": 95.0,
        "segments": [
            ("C-01-SEG-01", "Howrah - Bally Section", 0.0, 15.0),
            ("C-01-SEG-02", "Bally - Bandel Section", 15.0, 40.0),
            ("C-01-SEG-03", "Bandel - Barddhaman Section", 40.0, 95.0),
        ]
    },
    {
        "code": "ER-02",
        "name": "Howrah - Barddhaman Chord Line (via Dankuni)",
        "divisionId": div_hwh_id,
        "orig": "HWH",
        "dest": "BWN",
        "lengthKm": 95.0,
        "segments": [
            ("C-02-SEG-01", "Howrah - Dankuni Chord", 0.0, 22.0),
            ("C-02-SEG-02", "Dankuni - Kamarkundu Chord", 22.0, 48.0),
            ("C-02-SEG-03", "Kamarkundu - Barddhaman Chord", 48.0, 95.0),
        ]
    },
    {
        "code": "ER-03",
        "name": "Barddhaman - Durgapur Trunk Section",
        "divisionId": div_asn_id,
        "orig": "BWN",
        "dest": "DGR",
        "lengthKm": 62.0,
        "segments": [
            ("C-03-SEG-01", "Barddhaman - Guskara Section", 0.0, 20.0),
            ("C-03-SEG-02", "Guskara - Panagarh Section", 20.0, 42.0),
            ("C-03-SEG-03", "Panagarh - Durgapur Section", 42.0, 62.0),
        ]
    },
    {
        "code": "ER-04",
        "name": "Durgapur - Asansol Trunk Section",
        "divisionId": div_asn_id,
        "orig": "DGR",
        "dest": "ASN",
        "lengthKm": 42.0,
        "segments": [
            ("C-04-SEG-01", "Durgapur - Andal Junction", 0.0, 18.0),
            ("C-04-SEG-02", "Andal - Raniganj Section", 18.0, 28.0),
            ("C-04-SEG-03", "Raniganj - Asansol Section", 28.0, 42.0),
        ]
    },
    {
        "code": "ER-05",
        "name": "Asansol - Dhanbad Grand Chord",
        "divisionId": div_asn_id,
        "orig": "ASN",
        "dest": "DHN",
        "lengthKm": 58.0,
        "segments": [
            ("C-05-SEG-01", "Asansol - Barakar Section", 0.0, 16.0),
            ("C-05-SEG-02", "Barakar - Mugma Section", 16.0, 32.0),
            ("C-05-SEG-03", "Mugma - Dhanbad Section", 32.0, 58.0),
        ]
    },
    {
        "code": "ER-06",
        "name": "Asansol - Raniganj Industrial Loop",
        "divisionId": div_asn_id,
        "orig": "ASN",
        "dest": "RNG",
        "lengthKm": 18.0,
        "segments": [
            ("C-06-SEG-01", "Asansol - Sitarampur Siding", 0.0, 8.0),
            ("C-06-SEG-02", "Sitarampur - Raniganj Coal Belt", 8.0, 18.0),
        ]
    }
]

corridors = []
segments = []
corr_id_map = {}
seg_list_by_corr = {}

for c_def in corridors_def:
    c_id = make_uuid("corr", c_def["code"])
    corr_id_map[c_def["code"]] = c_id
    corridors.append({
        "id": c_id,
        "code": c_def["code"],
        "name": c_def["name"],
        "divisionId": c_def["divisionId"],
        "originStationId": stn_id_map[c_def["orig"]],
        "destinationStationId": stn_id_map[c_def["dest"]],
        "totalLengthKm": c_def["lengthKm"]
    })
    
    seg_list_by_corr[c_id] = []
    for seq, (s_code, s_desc, start_k, end_k) in enumerate(c_def["segments"], 1):
        s_id = make_uuid("seg", f"{c_def['code']}_{seq}")
        segments.append({
            "id": s_id,
            "corridorId": c_id,
            "sequenceNumber": seq,
            "name": s_desc,
            "startChainageKm": start_k,
            "endChainageKm": end_k
        })
        seg_list_by_corr[c_id].append(s_id)

# 4. Track Resources (Indian Railways Track Machine Depots & Gangs)
track_resources = [
    {
        "id": make_uuid("res", "BCM-ER-01"),
        "code": "BCM-ER-01",
        "name": "Plasser BCM 350 Ballast Cleaner (Howrah Depot)",
        "type": "MACHINE",
        "corridorId": None,
        "capacity": 1
    },
    {
        "id": make_uuid("res", "CSM-ER-01"),
        "code": "CSM-ER-01",
        "name": "Continuous 09-32 Track Tamping Machine (Asansol Depot)",
        "type": "MACHINE",
        "corridorId": None,
        "capacity": 1
    },
    {
        "id": make_uuid("res", "RGM-ER-01"),
        "code": "RGM-ER-01",
        "name": "72-Stone Rail Grinding Machine (Eastern Railway HQ)",
        "type": "MACHINE",
        "corridorId": None,
        "capacity": 1
    },
    {
        "id": make_uuid("res", "T28-ER-01"),
        "code": "T28-ER-01",
        "name": "T-28 Turnout Relaying Crane (Barddhaman Depot)",
        "type": "MACHINE",
        "corridorId": None,
        "capacity": 1
    },
    {
        "id": make_uuid("res", "TW-TRD-01"),
        "code": "TW-TRD-01",
        "name": "8-Wheeler TRD Tower Wagon (Barddhaman OHE)",
        "type": "MACHINE",
        "corridorId": None,
        "capacity": 1
    },
    {
        "id": make_uuid("res", "TW-TRD-02"),
        "code": "TW-TRD-02",
        "name": "8-Wheeler TRD Tower Wagon (Asansol OHE)",
        "type": "MACHINE",
        "corridorId": None,
        "capacity": 1
    },
    # Corridor P-Way Crews
    {
        "id": make_uuid("res", "ENG-CREW-HWH"),
        "code": "ENG-CREW-HWH",
        "name": "Howrah Division P-Way Maintenance Gang",
        "type": "CREW",
        "corridorId": corr_id_map["ER-01"],
        "capacity": 3
    },
    {
        "id": make_uuid("res", "ENG-CREW-ASN"),
        "code": "ENG-CREW-ASN",
        "name": "Asansol Division P-Way Maintenance Gang",
        "type": "CREW",
        "corridorId": corr_id_map["ER-04"],
        "capacity": 3
    },
    # TRD Crews
    {
        "id": make_uuid("res", "TRD-CREW-BWN"),
        "code": "TRD-CREW-BWN",
        "name": "Barddhaman TRD Overhead Line Crew",
        "type": "CREW",
        "corridorId": corr_id_map["ER-03"],
        "capacity": 2
    },
    {
        "id": make_uuid("res", "TRD-CREW-ASN"),
        "code": "TRD-CREW-ASN",
        "name": "Asansol TRD Overhead Line Crew",
        "type": "CREW",
        "corridorId": corr_id_map["ER-05"],
        "capacity": 2
    },
    # S&T Crews
    {
        "id": make_uuid("res", "ST-CREW-HWH"),
        "code": "ST-CREW-HWH",
        "name": "Howrah S&T Signal Maintenance Team",
        "type": "CREW",
        "corridorId": corr_id_map["ER-02"],
        "capacity": 2
    },
    {
        "id": make_uuid("res", "ST-CREW-ASN"),
        "code": "ST-CREW-ASN",
        "name": "Asansol S&T Signal Maintenance Team",
        "type": "CREW",
        "corridorId": corr_id_map["ER-04"],
        "capacity": 2
    }
]

res_id_map = {r["code"]: r["id"] for r in track_resources}

# 5. Assets across corridors
assets = []
asset_types = [
    ("RAIL", "60kg 90UTS Continuous Welded Rail", "CRITICAL"),
    ("TURNOUT", "1:12 Curved Switch Turnout Point", "HIGH"),
    ("OHE_MAST", "25kV AC Traction Cantilever Mast", "HIGH"),
    ("SIGNAL_EI", "Electronic Interlocking Signal Gantry", "CRITICAL"),
    ("TRACK_CIRCUIT", "High-Voltage Impulse Track Circuit", "MEDIUM"),
    ("BALLAST", "Standard 50mm Hard Stone Ballast Cushion", "MEDIUM"),
]

for corr in corridors:
    c_id = corr["id"]
    c_code = corr["code"]
    segs = seg_list_by_corr[c_id]
    for idx, (a_type, a_name, a_crit) in enumerate(asset_types, 1):
        seg_id = segs[idx % len(segs)]
        a_id = make_uuid("asset", f"{c_code}_{a_type}_{idx}")
        assets.append({
            "id": a_id,
            "code": f"AST-{c_code}-{a_type[:3]}-{idx:02d}",
            "name": f"{a_name} ({corr['name']})",
            "assetType": a_type,
            "corridorId": c_id,
            "segmentId": seg_id,
            "criticality": a_crit,
            "installDate": "2021-04-15T00:00:00.000Z",
            "lastMaintenanceDate": "2026-06-10T00:00:00.000Z"
        })

asset_by_corr_and_type = {}
for a in assets:
    c_id = a["corridorId"]
    if c_id not in asset_by_corr_and_type:
        asset_by_corr_and_type[c_id] = {}
    asset_by_corr_and_type[c_id][a["assetType"]] = a["id"]

# 6. Train Movements (Extracted from real RSTGCN train_routes_Sep2024.csv)
# We map real trains traversing these station pairs across the 2-week planning horizon:
# September 8, 2026 to September 22, 2026
key_trains = [
    {"num": "12019", "name": "Howrah - Ranchi Shatabdi Express", "type": "EXPRESS", "prio": 1},
    {"num": "12303", "name": "Poorva Express (via Patna)", "type": "EXPRESS", "prio": 1},
    {"num": "12314", "name": "Sealdah Rajdhani Express", "type": "EXPRESS", "prio": 1},
    {"num": "12341", "name": "Agniveena Express", "type": "EXPRESS", "prio": 2},
    {"num": "11448", "name": "Shaktipunj Express", "type": "EXPRESS", "prio": 2},
    {"num": "12834", "name": "Howrah Ahmedabad Superfast", "type": "EXPRESS", "prio": 2},
    {"num": "13005", "name": "Amritsar Mail", "type": "PASSENGER", "prio": 3},
    {"num": "12321", "name": "Mumbai Mail (via Gaya)", "type": "PASSENGER", "prio": 3},
    {"num": "3043", "name": "Howrah Raxaul Special", "type": "PASSENGER", "prio": 3},
    {"num": "2023", "name": "Howrah Patna Special SF", "type": "EXPRESS", "prio": 2},
    {"num": "3109", "name": "Sealdah Vadodara Special", "type": "PASSENGER", "prio": 3},
    {"num": "3007", "name": "Howrah Kalka Mail Special", "type": "PASSENGER", "prio": 3},
    {"num": "BOXN-01", "name": "Raniganj - Durgapur Coal Rake", "type": "GOODS", "prio": 4},
    {"num": "BCN-02", "name": "Howrah Goods Freight Special", "type": "GOODS", "prio": 4},
    {"num": "BOXN-03", "name": "Dhanbad Coking Coal Freight", "type": "GOODS", "prio": 4},
    {"num": "BOXN-NIGHT-01", "name": "ECL Raniganj Overnight Coal Rake", "type": "GOODS", "prio": 4},
    {"num": "BOXN-NIGHT-02", "name": "BCCL Dhanbad Night Coking Coal", "type": "GOODS", "prio": 4},
    {"num": "BCN-NIGHT-03", "name": "CONCOR Night Container Freight", "type": "GOODS", "prio": 4},
]

# Corridor timing templates (offset from base day)
corridor_train_schedule = [
    # C-01: HWH - BWN Main Line
    {"train": "12019", "corr": "ER-01", "startH": 6.0, "durationH": 1.25},
    {"train": "12303", "corr": "ER-01", "startH": 8.0, "durationH": 1.15},
    {"train": "12341", "corr": "ER-01", "startH": 18.3, "durationH": 1.2},
    {"train": "12314", "corr": "ER-01", "startH": 17.0, "durationH": 1.1},
    {"train": "3043", "corr": "ER-01", "startH": 23.0, "durationH": 1.5},
    {"train": "BCN-02", "corr": "ER-01", "startH": 14.0, "durationH": 2.2},

    # C-02: HWH - BWN Chord (via DKAE)
    {"train": "12834", "corr": "ER-02", "startH": 23.9, "durationH": 1.3},
    {"train": "13005", "corr": "ER-02", "startH": 19.25, "durationH": 1.3},
    {"train": "2023", "corr": "ER-02", "startH": 14.25, "durationH": 1.2},

    # C-03: BWN - DGR Trunk Section
    {"train": "12019", "corr": "ER-03", "startH": 7.3, "durationH": 0.8},
    {"train": "12303", "corr": "ER-03", "startH": 9.15, "durationH": 0.8},
    {"train": "11448", "corr": "ER-03", "startH": 14.3, "durationH": 0.9},
    {"train": "3007", "corr": "ER-03", "startH": 19.3, "durationH": 0.9},
    {"train": "BOXN-01", "corr": "ER-03", "startH": 15.0, "durationH": 1.5},

    # C-04: DGR - ASN Section
    {"train": "12019", "corr": "ER-04", "startH": 8.0, "durationH": 0.6},
    {"train": "12303", "corr": "ER-04", "startH": 10.0, "durationH": 0.6},
    {"train": "11448", "corr": "ER-04", "startH": 15.2, "durationH": 0.7},
    {"train": "12321", "corr": "ER-04", "startH": 21.0, "durationH": 0.7},
    {"train": "BOXN-01", "corr": "ER-04", "startH": 16.8, "durationH": 1.2},

    # C-05: ASN - DHN Grand Chord
    {"train": "12019", "corr": "ER-05", "startH": 8.7, "durationH": 0.9},
    {"train": "12303", "corr": "ER-05", "startH": 10.7, "durationH": 0.9},
    {"train": "11448", "corr": "ER-05", "startH": 16.0, "durationH": 1.0},
    {"train": "BOXN-03", "corr": "ER-05", "startH": 12.0, "durationH": 1.8},

    # C-06: ASN - RNG Industrial Loop
    {"train": "BOXN-01", "corr": "ER-06", "startH": 10.5, "durationH": 0.6},
    {"train": "3109", "corr": "ER-06", "startH": 11.2, "durationH": 0.5},

    # Overnight Freight Corridors (coal & container traffic across Eastern Railway)
    {"train": "BCN-NIGHT-03", "corr": "ER-01", "startH": 2.0, "durationH": 1.5},
    {"train": "BOXN-NIGHT-01", "corr": "ER-03", "startH": 1.5, "durationH": 2.0},
    {"train": "BOXN-NIGHT-02", "corr": "ER-04", "startH": 2.0, "durationH": 1.5},
]

train_movements = []
base_date = datetime(2026, 9, 8, 0, 0, 0)
train_meta_by_num = {t["num"]: t for t in key_trains}

for day_offset in range(14): # 14 days planning horizon
    current_day = base_date + timedelta(days=day_offset)
    for entry in corridor_train_schedule:
        # If it is an overnight freight train, run on days 1, 3, 5, 7, 9 to simulate heavy trunk freight
        if "NIGHT" in entry["train"] and (day_offset % 2 != 1):
            continue
        t_meta = train_meta_by_num[entry["train"]]
        c_id = corr_id_map[entry["corr"]]
        start_time = current_day + timedelta(hours=entry["startH"])
        end_time = start_time + timedelta(hours=entry["durationH"])
        t_id = make_uuid("train", f"{entry['train']}_{day_offset}_{entry['corr']}")
        
        train_movements.append({
            "id": t_id,
            "trainNumber": entry["train"],
            "trainType": t_meta["type"],
            "corridorId": c_id,
            "segmentId": None,
            "trackResourceId": None,
            "scheduledStart": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "scheduledEnd": end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "priority": t_meta["prio"]
        })

# 7. Block Windows (Real Indian Railways shadow possession windows)
# Night windows (01:00 - 05:00) and midday freight margin windows (11:30 - 13:30)
block_windows = []
for day_offset in range(1, 14, 2): # alternating days
    day_date = base_date + timedelta(days=day_offset)
    for c_code, c_id in corr_id_map.items():
        # Night integrated block window (240 min)
        night_start = day_date + timedelta(hours=1, minutes=0)
        night_end = day_date + timedelta(hours=5, minutes=0)
        bw_night_id = make_uuid("bw", f"{c_code}_night_{day_offset}")
        block_windows.append({
            "id": bw_night_id,
            "corridorId": c_id,
            "segmentId": None,
            "startTime": night_start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endTime": night_end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "durationMinutes": 240,
            "permittedDepartments": ["ENGINEERING", "TRD", "S_AND_T"],
            "allowsIsolationTypes": ["TRACK_ISOLATION", "POWER_ISOLATION", "SIGNAL_ISOLATION", "FULL_ISOLATION"],
            "allowsPowerTypes": ["NONE", "TRACTION_POWER_OFF", "AUXILIARY_POWER", "LOW_VOLTAGE"],
            "maxConcurrentResources": 3,
            "operationalRestrictions": "Integrated multi-department possession window."
        })
        
        # Midday short window on select corridors (120 min)
        if c_code in ["ER-01", "ER-03", "ER-05"]:
            mid_start = day_date + timedelta(hours=11, minutes=30)
            mid_end = day_date + timedelta(hours=13, minutes=30)
            bw_mid_id = make_uuid("bw", f"{c_code}_mid_{day_offset}")
            block_windows.append({
                "id": bw_mid_id,
                "corridorId": c_id,
                "segmentId": None,
                "startTime": mid_start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "endTime": mid_end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "durationMinutes": 120,
                "permittedDepartments": ["ENGINEERING", "TRD"],
                "allowsIsolationTypes": ["TRACK_ISOLATION", "POWER_ISOLATION"],
                "allowsPowerTypes": ["NONE", "TRACTION_POWER_OFF"],
                "maxConcurrentResources": 2,
                "operationalRestrictions": "Midday traffic regulation margin."
            })

# 8. Maintenance Demands (Standard Indian Railways P-Way / TRD / S&T work orders)
maintenance_requests = []
req_dependencies = []

def add_req(req_num, dept, c_code, a_type, w_type, desc, crit, urg, due_day_offset, dur_min, iso, pwr, res_list, tags):
    c_id = corr_id_map[c_code]
    a_id = asset_by_corr_and_type[c_id][a_type]
    due_date = (base_date + timedelta(days=due_day_offset)).strftime("%Y-%m-%dT00:00:00.000Z")
    r_id = make_uuid("req", req_num)
    
    req_obj = {
        "id": r_id,
        "requestNumber": req_num,
        "department": dept,
        "assetId": a_id,
        "corridorId": c_id,
        "segmentId": seg_list_by_corr[c_id][0],
        "workType": w_type,
        "description": desc,
        "criticality": crit,
        "urgency": urg,
        "dueDate": due_date,
        "estimatedDurationMinutes": dur_min,
        "requiredIsolation": iso,
        "requiredPower": pwr,
        "status": "OPEN",
        "requiredResources": [{"trackResourceId": res_id_map[r_code], "quantity": q} for (r_code, q) in res_list],
        "tags": tags
    }
    maintenance_requests.append(req_obj)
    return r_id

# Scenario 1: Overdue Critical USFD Track Defect on C-01 (Must be scheduled immediately)
r_overdue = add_req(
    "REQ-ER-2026-001", "ENGINEERING", "ER-01", "RAIL", "TRACK_RENEWAL",
    "Emergency replacement of USFD-detected flaw on Howrah-Bandel 60kg rail",
    "CRITICAL", "CRITICAL", 2, 210, "TRACK_ISOLATION", "NONE",
    [("ENG-CREW-HWH", 1)], ["overdue", "critical"]
)

# Scenario 2: Heavy Mechanized Ballast Cleaning on C-03 (Requires BCM-ER-01)
r_bcm_c03 = add_req(
    "REQ-ER-2026-002", "ENGINEERING", "ER-03", "BALLAST", "BALLAST_CLEANING",
    "Deep screening of track ballast cushion by BCM machine on Barddhaman-Durgapur trunk",
    "HIGH", "HIGH", 5, 230, "TRACK_ISOLATION", "NONE",
    [("BCM-ER-01", 1), ("ENG-CREW-ASN", 1)], ["machine-scarce"]
)

# Scenario 3: Competing Ballast Cleaning on C-04 (Requires SAME BCM-ER-01 -> resource conflict!)
r_bcm_c04 = add_req(
    "REQ-ER-2026-003", "ENGINEERING", "ER-04", "BALLAST", "BALLAST_CLEANING",
    "Ballast cleaning on Durgapur-Andal coal evacuation route",
    "HIGH", "MEDIUM", 5, 230, "TRACK_ISOLATION", "NONE",
    [("BCM-ER-01", 1), ("ENG-CREW-ASN", 1)], ["machine-conflict"]
)

# Scenario 4: TRD 25kV OHE Maintenance on C-01 (Bundling Candidate with P-Way)
r_trd_c01 = add_req(
    "REQ-ER-2026-004", "TRD", "ER-01", "OHE_MAST", "OHE_MAINTENANCE",
    "Periodic OHE contact wire height and stagger adjustment near Bally",
    "HIGH", "HIGH", 3, 180, "POWER_ISOLATION", "TRACTION_POWER_OFF",
    [("TW-TRD-01", 1), ("TRD-CREW-BWN", 1)], ["bundle-candidate"]
)

# Scenario 5: Engineering Rail Grinding on C-01 (Bundles with TRD on C-01!)
r_eng_c01 = add_req(
    "REQ-ER-2026-005", "ENGINEERING", "ER-01", "RAIL", "RAIL_GRINDING",
    "RGM rail surface reprofiling on Howrah-Barddhaman main line",
    "HIGH", "MEDIUM", 3, 180, "TRACK_ISOLATION", "NONE",
    [("RGM-ER-01", 1), ("ENG-CREW-HWH", 1)], ["bundle-candidate"]
)

# Scenario 6: S&T Point Machine Overhaul on C-04 (Predecessor)
r_st_pre = add_req(
    "REQ-ER-2026-006", "S_AND_T", "ER-04", "TURNOUT", "POINTS_CROSSING_MAINTENANCE",
    "Point machine overhaul and lock testing at Andal Junction",
    "HIGH", "HIGH", 6, 120, "SIGNAL_ISOLATION", "NONE",
    [("ST-CREW-ASN", 1)], ["dependency-predecessor"]
)

# Scenario 7: Track Tamping on C-04 (Successor to S&T overhaul)
r_eng_succ = add_req(
    "REQ-ER-2026-007", "ENGINEERING", "ER-04", "TURNOUT", "POINTS_CROSSING_MAINTENANCE",
    "CSM machine tamping through Andal turnout following point overhaul",
    "MEDIUM", "MEDIUM", 8, 150, "TRACK_ISOLATION", "NONE",
    [("CSM-ER-01", 1), ("ENG-CREW-ASN", 1)], ["dependency-successor"]
)

req_dependencies.append({
    "predecessorId": r_st_pre,
    "successorId": r_eng_succ
})

# Scenario 8: TRD OHE Maintenance on C-03 (Bundling Candidate with Ballast Cleaning)
r_trd_c03 = add_req(
    "REQ-ER-2026-008", "TRD", "ER-03", "OHE_MAST", "OHE_MAINTENANCE",
    "Replacement of 25kV porcelain bracket insulators near Panagarh",
    "MEDIUM", "HIGH", 5, 200, "POWER_ISOLATION", "TRACTION_POWER_OFF",
    [("TW-TRD-01", 1), ("TRD-CREW-BWN", 1)], ["bundle-candidate"]
)

# Additional diverse tasks across the network
r_eng_c02 = add_req(
    "REQ-ER-2026-009", "ENGINEERING", "ER-02", "RAIL", "TRACK_RENEWAL",
    "Through rail renewal on Dankuni-Kamarkundu chord line",
    "HIGH", "HIGH", 7, 210, "TRACK_ISOLATION", "NONE",
    [("ENG-CREW-HWH", 1)], ["routine"]
)
r_st_c02 = add_req(
    "REQ-ER-2026-010", "S_AND_T", "ER-02", "SIGNAL_EI", "INTERLOCKING_UPGRADE",
    "Electronic interlocking software patch test at Kamarkundu",
    "HIGH", "MEDIUM", 7, 90, "SIGNAL_ISOLATION", "NONE",
    [("ST-CREW-HWH", 1)], ["routine"]
)
r_trd_c05 = add_req(
    "REQ-ER-2026-011", "TRD", "ER-05", "OHE_MAST", "TRACTION_SUBSTATION_MAINTENANCE",
    "Barakar Traction Substation (TSS) transformer annual overhaul",
    "CRITICAL", "HIGH", 9, 220, "FULL_ISOLATION", "TRACTION_POWER_OFF",
    [("TW-TRD-02", 1), ("TRD-CREW-ASN", 1)], ["critical-trd"]
)
r_eng_c05 = add_req(
    "REQ-ER-2026-012", "ENGINEERING", "ER-05", "BALLAST", "BALLAST_CLEANING",
    "Ballast regulation and track consolidation near Mugma",
    "MEDIUM", "LOW", 9, 180, "TRACK_ISOLATION", "NONE",
    [("CSM-ER-01", 1), ("ENG-CREW-ASN", 1)], ["routine"]
)

# 9. Task Compatibility Rules
task_compat_rules = [
    {
        "workTypeA": "RAIL_GRINDING",
        "workTypeB": "SIGNAL_MAINTENANCE",
        "department": None,
        "compatible": True,
        "reason": "Rail grinding on through track does not disrupt track circuit sensor maintenance."
    },
    {
        "workTypeA": "OHE_MAINTENANCE",
        "workTypeB": "BALLAST_CLEANING",
        "department": None,
        "compatible": True,
        "reason": "TRD tower wagon working on OHE mast allows ballast cleaning below under common power block."
    },
    {
        "workTypeA": "GENERAL_INSPECTION",
        "workTypeB": "TRACK_RENEWAL",
        "department": None,
        "compatible": False,
        "reason": "Heavy track dismantling during rail renewal precludes footplate/general inspection."
    }
]

# 10. Scenario Events (What-If triggers)
scenario_events = [
    {
        "id": make_uuid("evt", "C03_UNAVAIL"),
        "eventType": "CORRIDOR_UNAVAILABLE",
        "source": "SYNTHETIC",
        "payload": {
            "corridorId": corr_id_map["ER-03"],
            "corridorCode": "ER-03",
            "reason": "Emergency rail fracture detected on Barddhaman-Durgapur trunk section",
            "effectiveFrom": "2026-09-12T00:00:00.000Z",
            "effectiveTo": "2026-09-15T00:00:00.000Z"
        }
    },
    {
        "id": make_uuid("evt", "NEW_CRITICAL"),
        "eventType": "NEW_CRITICAL_REQUEST",
        "source": "SYNTHETIC",
        "payload": {
            "corridorId": corr_id_map["ER-01"],
            "department": "ENGINEERING",
            "workType": "TRACK_RENEWAL",
            "description": "Critical fishplate bolt shear detected on Howrah approach track"
        }
    }
]

# Final Assembly
scenario_data = {
    "scenario": {
        "id": SCENARIO_ID,
        "name": "Eastern Railway (Howrah - Asansol - Dhanbad) Real Operations",
        "seed": SEED,
        "description": "Real Indian Railways operations scenario constructed from Kaggle station coordinates and RSTGCN September 2024 train timetables on the Eastern Railway trunk corridor.",
        "configVersion": CONFIG_VERSION,
        "generatedAt": GENERATED_AT
    },
    "divisions": divisions,
    "stations": stations,
    "corridors": corridors,
    "segments": segments,
    "trackResources": track_resources,
    "assets": assets,
    "maintenanceRequests": maintenance_requests,
    "requestDependencies": req_dependencies,
    "taskCompatibilityRules": task_compat_rules,
    "blockWindows": block_windows,
    "trainMovements": train_movements,
    "scenarioEvents": scenario_events
}

with open("data/real/real_scenario.json", "w") as f:
    json.dump(scenario_data, f, indent=2)

print(f"SUCCESS: Generated data/real/real_scenario.json with:")
print(f"- {len(divisions)} Divisions (Eastern Railway: Howrah & Asansol)")
print(f"- {len(stations)} Real Stations with GPS coordinates (Howrah, Barddhaman, Durgapur, Asansol, Dhanbad)")
print(f"- {len(corridors)} Real Corridors and {len(segments)} Segments")
print(f"- {len(track_resources)} Indian Railways Track Machines & Crews (BCM, CSM, RGM, Tower Wagons)")
print(f"- {len(assets)} Track, OHE & Signaling Assets")
print(f"- {len(train_movements)} Real Train Movements (Shatabdi, Poorva, Rajdhani, Coal Rakes)")
print(f"- {len(block_windows)} Block Possession Windows")
print(f"- {len(maintenance_requests)} Multi-department Maintenance Requisitions")
print(f"- {len(req_dependencies)} Task Dependencies")
print(f"- {len(task_compat_rules)} Compatibility Rules")
print(f"- {len(scenario_events)} What-If Disruption Events")
