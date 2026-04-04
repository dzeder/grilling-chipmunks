#!/usr/bin/env python3
"""
Fix Equipment warehouse assignments and Route vehicle/driver links.

Equipment.Fulfillment_Location__c is a master-detail (not updatable),
so we must: clear route links → delete equipment → recreate with correct
warehouses → relink routes → assign drivers.

Generates CSVs in migration_output/fixes/:
  1. clear_route_vehicles.csv     — nulls Vehicle__c on 211 linked routes
  2. delete_equipment.csv         — 235 equipment IDs for deletion
  3. Equipment_Vehicles_v2.csv    — new equipment with correct warehouses
  4. (after insert) relink_route_vehicles.csv — restore route→vehicle links
  5. fix_route_drivers.csv        — assign Mobile Driver to delivery routes
"""

import csv
import os
import re
import psycopg2

MIGRATION_DIR = os.path.join(os.path.dirname(__file__), "migration_output")
FIXES_DIR = os.path.join(MIGRATION_DIR, "fixes")

# --- Warehouse code → Salesforce Parent Location ID ---
WAREHOUSE_MAP = {
    "1": "a0kWE00000FdVsvYAF",  # GULF MOBILE
    "2": "a0kWE00000FdVsyYAF",  # GOLDRINGGULF MILTON
    "5": "a0kWE00000FdVszYAF",  # WAREHOUSE 5 JACKSON
    "6": "a0kWE00000FdVt0YAF",  # WAREHOUSE 6 GULFPORT
    "7": "a0kWE00000FdVt1YAF",  # MONTGOMERY
    "9": "a0kWE00000FdVt2YAF",  # BIRMINGHAM
    "10": "a0kWE00000FdVswYAF",  # HUNTSVILLE
    "11": "a0kWE00000FdVsxYAF",  # ABC BOARD
    "99": "a0kWE00000FdVt3YAF",  # AL LIQUOR SALES
}
DEFAULT_WAREHOUSE = "1"  # Gulf Mobile

# RecordType for Motorized Vehicle
RT_MOTORIZED_VEHICLE = "012WE00000LU71bYAD"

# Mobile Driver user ID (generic placeholder)
MOBILE_DRIVER_ID = "005WE00000d5JgXYAU"

# --- Existing sandbox data (from queries) ---

# 211 routes with vehicles: route_key → equipment_key
ROUTE_VEHICLE_MAP = {}
# route_id → route_key for linked routes
LINKED_ROUTE_IDS = {}

# 235 equipment IDs for deletion
EQUIPMENT_IDS = []

# 97 routes without vehicles
UNLINKED_ROUTES = []


def load_route_vehicle_data():
    """Load the route-vehicle mapping from the query output."""
    # Hardcoded from sandbox query - route_key maps 1:1 to equipment_key
    # (they're the same number for all 211 linked routes)
    data = """104,104
105,105
107,107
108,108
109,109
110,110
111,111
112,112
113,113
114,114
115,115
116,116
117,117
118,118
124,124
125,125
150,150
151,151
152,152
153,153
154,154
155,155
156,156
157,157
158,158
159,159
161,161
162,162
171,171
172,172
173,173
181,181
182,182
217,217
219,219
220,220
221,221
222,222
223,223
224,224
225,225
226,226
227,227
228,228
229,229
230,230
231,231
232,232
233,233
234,234
235,235
236,236
237,237
238,238
240,240
241,241
242,242
243,243
282,282
285,285
290,290
297,297
344,344
345,345
346,346
347,347
348,348
350,350
351,351
352,352
353,353
354,354
358,358
359,359
481,481
482,482
483,483
484,484
485,485
486,486
487,487
488,488
489,489
490,490
491,491
493,493
495,495
496,496
497,497
499,499
501,501
701,701
702,702
703,703
704,704
705,705
706,706
707,707
708,708
709,709
710,710
711,711
712,712
713,713
714,714
715,715
716,716
717,717
718,718
719,719
801,801
802,802
803,803
804,804
805,805
806,806
807,807
808,808
809,809
810,810
811,811
815,815
901,901
902,902
903,903
904,904
905,905
906,906
907,907
908,908
909,909
910,910
911,911
912,912
913,913
914,914
915,915
916,916
917,917
918,918
919,919
921,921
922,922
923,923
924,924
925,925
926,926
927,927
928,928
929,929
930,930
931,931
932,932
933,933
934,934
950,950
951,951
952,952
953,953
954,954
975,975
976,976
977,977
980,980
997,997
998,998
999,999
H01,H01
H02,H02
H03,H03
H04,H04
H05,H05
H06,H06
H07,H07
H08,H08
H09,H09
H10,H10
H11,H11
H12,H12
H13,H13
H14,H14
H15,H15
H16,H16
H17,H17
H18,H18
H19,H19
H20,H20
H21,H21
H22,H22
H23,H23
H24,H24
H25,H25
H26,H26
H27,H27
H28,H28
H29,H29
H30,H30
H31,H31
H32,H32
H33,H33
H34,H34
H35,H35
H36,H36
H37,H37
H38,H38
H39,H39
H40,H40
H41,H41
H42,H42
H43,H43
H44,H44"""
    for line in data.strip().split("\n"):
        rk, ek = line.split(",")
        ROUTE_VEHICLE_MAP[rk] = ek


def get_truck_warehouse_mapping():
    """Query VIP to get dominant warehouse per truck."""
    conn = psycopg2.connect(
        host="gulfstream-db2-data.postgres.database.azure.com",
        port=5432,
        database="gulfstream",
        user="ohanafy",
        password="Xq7!mR#2vK$9pLw@nZ",
        sslmode="require",
    )
    cur = conn.cursor()
    cur.execute("""
        WITH truck_wh AS (
            SELECT
                TRIM("TUTRK#") as truck_num,
                TRIM(b."CMWHSE") as warehouse,
                COUNT(*) as cust_count,
                ROW_NUMBER() OVER (
                    PARTITION BY TRIM("TUTRK#")
                    ORDER BY COUNT(*) DESC
                ) as rn
            FROM staging."TRUCKT" t
            JOIN staging."HDRROUTET" r
                ON TRIM(t."TUTRK#") = TRIM(r."ROUTE")
            JOIN staging."BRATTT" b
                ON TRIM(r."ROUTE") = TRIM(b."CMBRT")
            WHERE b."CMWHSE" IS NOT NULL
            GROUP BY TRIM(t."TUTRK#"), TRIM(b."CMWHSE")
        )
        SELECT truck_num, warehouse, cust_count
        FROM truck_wh WHERE rn = 1
        ORDER BY truck_num
    """)
    mapping = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()
    print(f"  VIP truck→warehouse: {len(mapping)} trucks mapped to {len(set(mapping.values()))} warehouses")
    return mapping


def classify_unlinked_routes():
    """Classify the 97 unlinked routes into categories."""
    routes_raw = """a18WE000009UfgVYAS,Route 127 - Slater, Victor,127
a18WE000009UfgWYAS,Route 146 - Seasoverflw146,146
a18WE000009UfgmYAC,Route 175 - Cart In Mkt 1,175
a18WE000009UfgnYAC,Route 180 - Gdc Transfers,180
a18WE000009UfgqYAC,Route 183 - Inven Device,183
a18WE000009UfgrYAC,Route 184 - Seasoverflw184,184
a18WE000009UfgsYAC,Route 185 - Seasoverflw185,185
a18WE000009UfgtYAC,Route 188 - Houston,Justin,188
a18WE000009UfguYAC,Route 192 - Hngmsc Fest Rt,192
a18WE000009UfgvYAC,Route 197 - Gdc Samples,197
a18WE000009UfgwYAC,Route 198 - Mob Swapouts,198
a18WE000009UfgxYAC,Route 199 - Mobile House,199
a18WE000009UfgyYAC,Route 200 - Regulated Glas,200
a18WE000009UfgzYAC,Route 210 - Rlf Negron, El,210
a18WE000009Ufh0YAC,Route 211 - Rlf Spicer,Rog,211
a18WE000009Ufh1YAC,Route 212 - Green, Richard,212
a18WE000009Ufh2YAC,Route 213 - Overflow 213,213
a18WE000009Ufh3YAC,Route 214 - Travis, Patric,214
a18WE000009Ufh4YAC,Route 215 - Overflow 215,215
a18WE000009Ufh5YAC,Route 216 - Overflow 216,216
a18WE000009Ufh7YAC,Route 218 - Overflow 218,218
a18WE000009UfhWYAS,Route 275 - Cart In Mkt 2,275
a18WE000009UfhXYAS,Route 280 - Mlt Transfers,280
a18WE000009UfhcYAC,Route 299 - Milton House,299
a18WE000009UfhpYAC,Route 465 - Pc Spec Event,465
a18WE000009UfhqYAC,Route 475 - Cart In Mkt 4,475
a18WE000009UfhrYAC,Route 480 - Pc Transfers,480
a18WE000009Ufi9YAC,Route 502 - Andrews, Micah,502
a18WE000009UfiAYAS,Route 503 - Myers, Kelvin,503
a18WE000009UfiBYAS,Route 504 - Jacque, Dillon,504
a18WE000009UfiCYAS,Route 505 - Carter,Chester,505
a18WE000009UfiDYAS,Route 506 - Haynes, Blake,506
a18WE000009UfiEYAS,Route 507 - Carpenter, Daw,507
a18WE000009UfiFYAS,Route 508 - Tyler, Josh,508
a18WE000009UfiGYAS,Route 509 - Xtra Rt  Ebm 5,509
a18WE000009UfiHYAS,Route 510 - Xtra Rt Ebm 5,510
a18WE000009UfiIYAS,Route 514 - Bogle,Br Merch,514
a18WE000009UfiJYAS,Route 580 - 5 Transfers,580
a18WE000009UfiKYAS,Route 597 - Ebm Jack Sampl,597
a18WE000009UfiLYAS,Route 599 - Jackson House,599
a18WE000009UfiMYAS,Route 620 - Johnson, Deont,620
a18WE000009UfiNYAS,Route 621 - Mitro,Micheal,621
a18WE000009UfiOYAS,Route 622 - Goodwin, Curry,622
a18WE000009UfiPYAS,Route 623 - Welford, Mike,623
a18WE000009UfiQYAS,Route 624 - Cook, Willie D,624
a18WE000009UfiRYAS,Route 625 - Nguyen, Fuji,625
a18WE000009UfiSYAS,Route 626 - Jomisko,Robert,626
a18WE000009UfiTYAS,Route 680 - 6 Transfers,680
a18WE000009UfiUYAS,Route 697 - Ebm Gport Samp,697
a18WE000009UfiVYAS,Route 699 - Gulfport House,699
a18WE000009UfipYAC,Route 775 - Cart In Mkt 7,775
a18WE000009UfiqYAC,Route 780 - Abc Transfers,780
a18WE000009UfirYAC,Route 781 - Boone, Hunter,781
a18WE000009UfisYAC,Route 782 - Open Rt 782,782
a18WE000009UfitYAC,Route 783 - Open Rt 783,783
a18WE000009UfiuYAC,Route 784 - Open Rt 784,784
a18WE000009UfivYAC,Route 788 - Demop Swapouts,788
a18WE000009UfiwYAC,Route 789 - Dothan Swapout,789
a18WE000009UfixYAC,Route 791 - Bouier, Dallas,791
a18WE000009UfiyYAC,Route 792 - Thomas,Anthony,792
a18WE000009UfizYAC,Route 793 - Lawrence, Greg,793
a18WE000009Ufj0YAC,Route 794 - Open Rt 794,794
a18WE000009Ufj1YAC,Route 795 - Rt 795 Open,795
a18WE000009Ufj2YAC,Route 796 - Open Rt 796,796
a18WE000009Ufj3YAC,Route 797 - Abc Samples,797
a18WE000009Ufj4YAC,Route 798 - Montg Swapouts,798
a18WE000009Ufj5YAC,Route 799 - Montg House,799
a18WE000009UfjIYAS,Route 816 - Open Rt 816,816
a18WE000009UfjJYAS,Route 817 - Open Rt 817,817
a18WE000009UfjKYAS,Route 818 - Open Rt 818,818
a18WE000009UfjLYAS,Route 888 - Open Rt 888,888
a18WE000009UfjyYAC,Route 955 - Open Rt 955,955
a18WE000009UfjzYAC,Route 956 - Open Rt 956,956
a18WE000009Ufk0YAC,Route 958 - Open Rt 958,958
a18WE000009Ufk1YAC,Route 959 - Open Rt 959,959
a18WE000009Ufk2YAC,Route 960 - Open Rt 960,960
a18WE000009Ufk3YAC,Route 961 - Open 961,961
a18WE000009Ufk4YAC,Route 962 - Dates,Niesha,962
a18WE000009Ufk5YAC,Route 963 - Daniels,Dereck,963
a18WE000009Ufk6YAC,Route 964 - Open Rt 964,964
a18WE000009Ufk7YAC,Route 965 - Open Rt 965,965
a18WE000009Ufk8YAC,Route 966 - Open Rt 966,966
a18WE000009Ufk9YAC,Route 967 - Open Rt 967,967
a18WE000009UfkAYAS,Route 968 - Open Rt 968,968
a18WE000009UfkBYAS,Route 969 - Dawson, Jordan,969
a18WE000009UfkCYAS,Route 970 - Smith, Billy,970
a18WE000009UfkDYAS,Route 971 - Spare Rt 971,971
a18WE000009UfkEYAS,Route 972 - Johnson,Kobie,972
a18WE000009UfkFYAS,Route 973 - May, Johnathan,973
a18WE000009UfkGYAS,Route 974 - Mosley,Kejuan,974
a18WE000009UfkKYAS,Route 978 - Tolliver,Kim,978
a18WE000009UfkMYAS,Route 985 - Bham Transfer,985
a18WE000009Ufl8YAC,Route H45 - Open Rt H45,H45
a18WE000009Ufl9YAC,Route H80 - Hunts Transfer,H80
a18WE000009UflAYAS,Route H97 - Hunts Samples,H97
a18WE000009UflBYAS,Route H99 - Hunts House,H99
a18WE000009UflCYAS,Route L99 - Al Liquor Rt,L99"""

    # Classification patterns
    special_patterns = [
        (r"(?i)transfer", "Transfer"),
        (r"(?i)sample", "Samples"),
        (r"(?i)house\b", "House"),
        (r"(?i)swapout", "Swapout"),
        (r"(?i)cart in mkt", "Cart-In-Market"),
        (r"(?i)overflow|seasoverflw", "Overflow/Seasonal"),
        (r"(?i)open rt|open \d|spare", "Open/Spare"),
        (r"(?i)inven device", "Inventory Device"),
        (r"(?i)regulated", "Regulated"),
        (r"(?i)spec event|fest rt", "Special Event"),
        (r"(?i)xtra rt", "Extra"),
        (r"(?i)merch\b", "Merchandiser"),
        (r"(?i)al liquor", "AL Liquor"),
        (r"(?i)rlf\b", "Relief Driver"),
    ]

    classified = {"Delivery": [], "Special": []}
    categories = {}

    for line in routes_raw.strip().split("\n"):
        parts = line.split(",")
        route_id = parts[0]
        route_name = ",".join(parts[1:-1])
        route_key = parts[-1]

        category = None
        for pattern, cat in special_patterns:
            if re.search(pattern, route_name):
                category = cat
                break

        if category:
            classified["Special"].append({"id": route_id, "name": route_name, "key": route_key, "category": category})
            categories[category] = categories.get(category, 0) + 1
        else:
            classified["Delivery"].append({"id": route_id, "name": route_name, "key": route_key})

    print("\n  Route Classification:")
    print(f"    Delivery routes (real drivers, no matching truck): {len(classified['Delivery'])}")
    print(f"    Special/non-delivery routes: {len(classified['Special'])}")
    for cat, count in sorted(categories.items()):
        print(f"      {cat}: {count}")

    return classified


def generate_csvs():
    """Generate all fix CSVs."""
    print("=== Equipment & Route Fix CSV Generator ===\n")

    # Step 1: Load data
    print("1. Loading route-vehicle mapping...")
    load_route_vehicle_data()
    print(f"   {len(ROUTE_VEHICLE_MAP)} route→vehicle links to preserve")

    # Step 2: Get truck→warehouse from VIP
    print("\n2. Querying VIP for truck→warehouse mapping...")
    truck_warehouse = get_truck_warehouse_mapping()

    # Step 3: Read original equipment CSV
    print("\n3. Reading original Equipment_Vehicles.csv...")
    equipment_rows = []
    with open(os.path.join(MIGRATION_DIR, "Equipment_Vehicles.csv")) as f:
        reader = csv.DictReader(f)
        for row in reader:
            equipment_rows.append(row)
    print(f"   {len(equipment_rows)} equipment records")

    # Step 4: Classify routes
    print("\n4. Classifying unlinked routes...")
    classified = classify_unlinked_routes()

    # --- Generate CSVs ---

    # CSV 1: Clear route vehicles (set to empty)
    # We'll query route IDs at load time, so generate from route keys
    print("\n5. Generating clear_route_vehicles.csv...")
    # Hardcoded route_id → route_key from sandbox query
    route_ids_raw = """a18WE000009UCplYAG,104
a18WE000009UCpmYAG,105
a18WE000009UCpnYAG,107
a18WE000009UCpoYAG,108
a18WE000009UCppYAG,109
a18WE000009UCpqYAG,110
a18WE000009UCprYAG,111
a18WE000009UCpsYAG,112
a18WE000009UCptYAG,113
a18WE000009UCpuYAG,114
a18WE000009UCpvYAG,115
a18WE000009UCpwYAG,116
a18WE000009UCpxYAG,117
a18WE000009UCpyYAG,118
a18WE000009UfgTYAS,124
a18WE000009UfgUYAS,125
a18WE000009UfgXYAS,150
a18WE000009UfgYYAS,151
a18WE000009UfgZYAS,152
a18WE000009UfgaYAC,153
a18WE000009UfgbYAC,154
a18WE000009UfgcYAC,155
a18WE000009UfgdYAC,156
a18WE000009UfgeYAC,157
a18WE000009UfgfYAC,158
a18WE000009UfggYAC,159
a18WE000009UfghYAC,161
a18WE000009UfgiYAC,162
a18WE000009UfgjYAC,171
a18WE000009UfgkYAC,172
a18WE000009UfglYAC,173
a18WE000009UfgoYAC,181
a18WE000009UfgpYAC,182
a18WE000009Ufh6YAC,217
a18WE000009Ufh8YAC,219
a18WE000009Ufh9YAC,220
a18WE000009UfhAYAS,221
a18WE000009UfhBYAS,222
a18WE000009UfhCYAS,223
a18WE000009UfhDYAS,224
a18WE000009UfhEYAS,225
a18WE000009UfhFYAS,226
a18WE000009UfhGYAS,227
a18WE000009UfhHYAS,228
a18WE000009UfhIYAS,229
a18WE000009UfhJYAS,230
a18WE000009UfhKYAS,231
a18WE000009UfhLYAS,232
a18WE000009UfhMYAS,233
a18WE000009UfhNYAS,234
a18WE000009UfhOYAS,235
a18WE000009UfhPYAS,236
a18WE000009UfhQYAS,237
a18WE000009UfhRYAS,238
a18WE000009UfhSYAS,240
a18WE000009UfhTYAS,241
a18WE000009UfhUYAS,242
a18WE000009UfhVYAS,243
a18WE000009UfhYYAS,282
a18WE000009UfhZYAS,285
a18WE000009UfhaYAC,290
a18WE000009UfhbYAC,297
a18WE000009UfhdYAC,344
a18WE000009UfheYAC,345
a18WE000009UfhfYAC,346
a18WE000009UfhgYAC,347
a18WE000009UfhhYAC,348
a18WE000009UfhiYAC,350
a18WE000009UfhjYAC,351
a18WE000009UfhkYAC,352
a18WE000009UfhlYAC,353
a18WE000009UfhmYAC,354
a18WE000009UfhnYAC,358
a18WE000009UfhoYAC,359
a18WE000009UfhsYAC,481
a18WE000009UfhtYAC,482
a18WE000009UfhuYAC,483
a18WE000009UfhvYAC,484
a18WE000009UfhwYAC,485
a18WE000009UfhxYAC,486
a18WE000009UfhyYAC,487
a18WE000009UfhzYAC,488
a18WE000009Ufi0YAC,489
a18WE000009Ufi1YAC,490
a18WE000009Ufi2YAC,491
a18WE000009Ufi3YAC,493
a18WE000009Ufi4YAC,495
a18WE000009Ufi5YAC,496
a18WE000009Ufi6YAC,497
a18WE000009Ufi7YAC,499
a18WE000009Ufi8YAC,501
a18WE000009UfiWYAS,701
a18WE000009UfiXYAS,702
a18WE000009UfiYYAS,703
a18WE000009UfiZYAS,704
a18WE000009UfiaYAC,705
a18WE000009UfibYAC,706
a18WE000009UficYAC,707
a18WE000009UfidYAC,708
a18WE000009UfieYAC,709
a18WE000009UfifYAC,710
a18WE000009UfigYAC,711
a18WE000009UfihYAC,712
a18WE000009UfiiYAC,713
a18WE000009UfijYAC,714
a18WE000009UfikYAC,715
a18WE000009UfilYAC,716
a18WE000009UfimYAC,717
a18WE000009UfinYAC,718
a18WE000009UfioYAC,719
a18WE000009Ufj6YAC,801
a18WE000009Ufj7YAC,802
a18WE000009Ufj8YAC,803
a18WE000009Ufj9YAC,804
a18WE000009UfjAYAS,805
a18WE000009UfjBYAS,806
a18WE000009UfjCYAS,807
a18WE000009UfjDYAS,808
a18WE000009UfjEYAS,809
a18WE000009UfjFYAS,810
a18WE000009UfjGYAS,811
a18WE000009UfjHYAS,815
a18WE000009UfjMYAS,901
a18WE000009UfjNYAS,902
a18WE000009UfjOYAS,903
a18WE000009UfjPYAS,904
a18WE000009UfjQYAS,905
a18WE000009UfjRYAS,906
a18WE000009UfjSYAS,907
a18WE000009UfjTYAS,908
a18WE000009UfjUYAS,909
a18WE000009UfjVYAS,910
a18WE000009UfjWYAS,911
a18WE000009UfjXYAS,912
a18WE000009UfjYYAS,913
a18WE000009UfjZYAS,914
a18WE000009UfjaYAC,915
a18WE000009UfjbYAC,916
a18WE000009UfjcYAC,917
a18WE000009UfjdYAC,918
a18WE000009UfjeYAC,919
a18WE000009UfjfYAC,921
a18WE000009UfjgYAC,922
a18WE000009UfjhYAC,923
a18WE000009UfjiYAC,924
a18WE000009UfjjYAC,925
a18WE000009UfjkYAC,926
a18WE000009UfjlYAC,927
a18WE000009UfjmYAC,928
a18WE000009UfjnYAC,929
a18WE000009UfjoYAC,930
a18WE000009UfjpYAC,931
a18WE000009UfjqYAC,932
a18WE000009UfjrYAC,933
a18WE000009UfjsYAC,934
a18WE000009UfjtYAC,950
a18WE000009UfjuYAC,951
a18WE000009UfjvYAC,952
a18WE000009UfjwYAC,953
a18WE000009UfjxYAC,954
a18WE000009UfkHYAS,975
a18WE000009UfkIYAS,976
a18WE000009UfkJYAS,977
a18WE000009UfkLYAS,980
a18WE000009UfkNYAS,997
a18WE000009UfkOYAS,998
a18WE000009UfkPYAS,999
a18WE000009UfkQYAS,H01
a18WE000009UfkRYAS,H02
a18WE000009UfkSYAS,H03
a18WE000009UfkTYAS,H04
a18WE000009UfkUYAS,H05
a18WE000009UfkVYAS,H06
a18WE000009UfkWYAS,H07
a18WE000009UfkXYAS,H08
a18WE000009UfkYYAS,H09
a18WE000009UfkZYAS,H10
a18WE000009UfkaYAC,H11
a18WE000009UfkbYAC,H12
a18WE000009UfkcYAC,H13
a18WE000009UfkdYAC,H14
a18WE000009UfkeYAC,H15
a18WE000009UfkfYAC,H16
a18WE000009UfkgYAC,H17
a18WE000009UfkhYAC,H18
a18WE000009UfkiYAC,H19
a18WE000009UfkjYAC,H20
a18WE000009UfkkYAC,H21
a18WE000009UfklYAC,H22
a18WE000009UfkmYAC,H23
a18WE000009UfknYAC,H24
a18WE000009UfkoYAC,H25
a18WE000009UfkpYAC,H26
a18WE000009UfkqYAC,H27
a18WE000009UfkrYAC,H28
a18WE000009UfksYAC,H29
a18WE000009UfktYAC,H30
a18WE000009UfkuYAC,H31
a18WE000009UfkvYAC,H32
a18WE000009UfkwYAC,H33
a18WE000009UfkxYAC,H34
a18WE000009UfkyYAC,H35
a18WE000009UfkzYAC,H36
a18WE000009Ufl0YAC,H37
a18WE000009Ufl1YAC,H38
a18WE000009Ufl2YAC,H39
a18WE000009Ufl3YAC,H40
a18WE000009Ufl4YAC,H41
a18WE000009Ufl5YAC,H42
a18WE000009Ufl6YAC,H43
a18WE000009Ufl7YAC,H44"""

    clear_path = os.path.join(FIXES_DIR, "clear_route_vehicles.csv")
    with open(clear_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Id", "ohfy__Vehicle__c"])
        for line in route_ids_raw.strip().split("\n"):
            rid, rkey = line.split(",")
            writer.writerow([rid, "#N/A"])  # #N/A clears lookup in bulk API
    print(f"   Written: {clear_path} (211 rows)")

    # CSV 2: Equipment IDs for deletion
    print("\n6. Generating delete_equipment.csv...")
    equip_ids_raw = """a0GWE000009lFtG2AU
a0GWE000009lFtH2AU
a0GWE000009lFtI2AU
a0GWE000009lFtJ2AU
a0GWE000009lFtK2AU
a0GWE000009lFtL2AU
a0GWE000009lFtM2AU
a0GWE000009lFtN2AU
a0GWE000009lFtO2AU
a0GWE000009lFtP2AU
a0GWE000009lFtQ2AU
a0GWE000009lFtR2AU
a0GWE000009lFtS2AU
a0GWE000009lFtT2AU
a0GWE000009lFtU2AU
a0GWE000009lFtV2AU
a0GWE000009lFtW2AU
a0GWE000009lFtX2AU
a0GWE000009lFtY2AU
a0GWE000009lFtZ2AU
a0GWE000009lFta2AE
a0GWE000009lFtb2AE
a0GWE000009lFtc2AE
a0GWE000009lFtd2AE
a0GWE000009lFte2AE
a0GWE000009lFtf2AE
a0GWE000009lFtg2AE
a0GWE000009lFth2AE
a0GWE000009lFti2AE
a0GWE000009lFtj2AE
a0GWE000009lFtk2AE
a0GWE000009lFtl2AE
a0GWE000009lFtm2AE
a0GWE000009lFtn2AE
a0GWE000009lFto2AE
a0GWE000009lFtp2AE
a0GWE000009lFtq2AE
a0GWE000009lFtr2AE
a0GWE000009lFts2AE
a0GWE000009lFtt2AE
a0GWE000009lFtu2AE
a0GWE000009lFtv2AE
a0GWE000009lFtw2AE
a0GWE000009lFtx2AE
a0GWE000009lFty2AE
a0GWE000009lFtz2AE
a0GWE000009lFu02AE
a0GWE000009lFu12AE
a0GWE000009lFu22AE
a0GWE000009lFu32AE
a0GWE000009lFu42AE
a0GWE000009lFu52AE
a0GWE000009lFu62AE
a0GWE000009lFu72AE
a0GWE000009lFu82AE
a0GWE000009lFu92AE
a0GWE000009lFuA2AU
a0GWE000009lFuB2AU
a0GWE000009lFuC2AU
a0GWE000009lFuD2AU
a0GWE000009lFuE2AU
a0GWE000009lFuF2AU
a0GWE000009lFuG2AU
a0GWE000009lFuH2AU
a0GWE000009lFuI2AU
a0GWE000009lFuJ2AU
a0GWE000009lFuK2AU
a0GWE000009lFuL2AU
a0GWE000009lFuM2AU
a0GWE000009lFuN2AU
a0GWE000009lFuO2AU
a0GWE000009lFuP2AU
a0GWE000009lFuQ2AU
a0GWE000009lFuR2AU
a0GWE000009lFuS2AU
a0GWE000009lQjR2AU
a0GWE000009lQjS2AU
a0GWE000009lQjT2AU
a0GWE000009lQjU2AU
a0GWE000009lQjV2AU
a0GWE000009lQjW2AU
a0GWE000009lQjX2AU
a0GWE000009lQjY2AU
a0GWE000009lQjZ2AU
a0GWE000009lQja2AE
a0GWE000009lQjb2AE
a0GWE000009lQjc2AE
a0GWE000009lQjd2AE
a0GWE000009lQje2AE
a0GWE000009lQjf2AE
a0GWE000009lQjg2AE
a0GWE000009lQjh2AE
a0GWE000009lQji2AE
a0GWE000009lQjj2AE
a0GWE000009lQjk2AE
a0GWE000009lQjl2AE
a0GWE000009lQjm2AE
a0GWE000009lQjn2AE
a0GWE000009lQjo2AE
a0GWE000009lQjp2AE
a0GWE000009lQjq2AE
a0GWE000009lQjr2AE
a0GWE000009lQjs2AE
a0GWE000009lQa42AE
a0GWE000009lQjt2AE
a0GWE000009lQju2AE
a0GWE000009lQjv2AE
a0GWE000009lQjw2AE
a0GWE000009lQjx2AE
a0GWE000009lQjy2AE
a0GWE000009lQjz2AE
a0GWE000009lQk02AE
a0GWE000009lQk12AE
a0GWE000009lQk22AE
a0GWE000009lQk32AE
a0GWE000009lQk42AE
a0GWE000009lQk52AE
a0GWE000009lQk62AE
a0GWE000009lQk72AE
a0GWE000009lQk82AE
a0GWE000009lQk92AE
a0GWE000009lQkA2AU
a0GWE000009lQkB2AU
a0GWE000009lQkC2AU
a0GWE000009lQkD2AU
a0GWE000009lQkE2AU
a0GWE000009lQkF2AU
a0GWE000009lQkG2AU
a0GWE000009lQkH2AU
a0GWE000009lQkI2AU
a0GWE000009lQkJ2AU
a0GWE000009lQkK2AU
a0GWE000009lQkL2AU
a0GWE000009lQkM2AU
a0GWE000009lQkN2AU
a0GWE000009lQkO2AU
a0GWE000009lQkP2AU
a0GWE000009lQkQ2AU
a0GWE000009lQkR2AU
a0GWE000009lQkS2AU
a0GWE000009lQkT2AU
a0GWE000009lQkU2AU
a0GWE000009lQkV2AU
a0GWE000009lQkW2AU
a0GWE000009lQkX2AU
a0GWE000009lQkY2AU
a0GWE000009lQkZ2AU
a0GWE000009lQka2AE
a0GWE000009lQkb2AE
a0GWE000009lQkc2AE
a0GWE000009lQkd2AE
a0GWE000009lQke2AE
a0GWE000009lQkf2AE
a0GWE000009lQkg2AE
a0GWE000009lQkh2AE
a0GWE000009lQki2AE
a0GWE000009lQkj2AE
a0GWE000009lQkk2AE
a0GWE000009lQkl2AE
a0GWE000009lQkm2AE
a0GWE000009lQkn2AE
a0GWE000009lQko2AE
a0GWE000009lQkp2AE
a0GWE000009lQkq2AE
a0GWE000009lQkr2AE
a0GWE000009lQks2AE
a0GWE000009lQkt2AE
a0GWE000009lQku2AE
a0GWE000009lQkv2AE
a0GWE000009lQkw2AE
a0GWE000009lQkx2AE
a0GWE000009lQky2AE
a0GWE000009lQkz2AE
a0GWE000009lQl02AE
a0GWE000009lQl12AE
a0GWE000009lQl22AE
a0GWE000009lQl32AE
a0GWE000009lQl42AE
a0GWE000009lQa52AE
a0GWE000009lQa62AE
a0GWE000009lQa72AE
a0GWE000009lQa82AE
a0GWE000009lQl52AE
a0GWE000009lQa92AE
a0GWE000009lQl62AE
a0GWE000009lQl72AE
a0GWE000009lQaA2AU
a0GWE000009lQl82AE
a0GWE000009lQl92AE
a0GWE000009lQlA2AU
a0GWE000009lQlB2AU
a0GWE000009lQlC2AU
a0GWE000009lQlD2AU
a0GWE000009lQlE2AU
a0GWE000009lQlF2AU
a0GWE000009lQlG2AU
a0GWE000009lQlH2AU
a0GWE000009lQlI2AU
a0GWE000009lQlJ2AU
a0GWE000009lQlK2AU
a0GWE000009lQlL2AU
a0GWE000009lQlM2AU
a0GWE000009lQlN2AU
a0GWE000009lQlO2AU
a0GWE000009lQlP2AU
a0GWE000009lQlQ2AU
a0GWE000009lQlR2AU
a0GWE000009lQlS2AU
a0GWE000009lQlT2AU
a0GWE000009lQlU2AU
a0GWE000009lQlV2AU
a0GWE000009lQlW2AU
a0GWE000009lQlX2AU
a0GWE000009lQlY2AU
a0GWE000009lQlZ2AU
a0GWE000009lQla2AE
a0GWE000009lQlb2AE
a0GWE000009lQlc2AE
a0GWE000009lQld2AE
a0GWE000009lQle2AE
a0GWE000009lQlf2AE
a0GWE000009lQlg2AE
a0GWE000009lQlh2AE
a0GWE000009lQli2AE
a0GWE000009lQlj2AE
a0GWE000009lQlk2AE
a0GWE000009lQll2AE
a0GWE000009lQlm2AE
a0GWE000009lQln2AE
a0GWE000009lQlo2AE
a0GWE000009lQlp2AE
a0GWE000009lQlq2AE
a0GWE000009lQlr2AE
a0GWE000009lQaB2AU
a0GWE000009lQaC2AU"""

    delete_path = os.path.join(FIXES_DIR, "delete_equipment.csv")
    with open(delete_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Id"])
        for eid in equip_ids_raw.strip().split("\n"):
            writer.writerow([eid.strip()])
    print(f"   Written: {delete_path} (235 rows)")

    # CSV 3: New equipment with correct warehouses
    print("\n7. Generating Equipment_Vehicles_v2.csv...")
    warehouse_stats = {}
    v2_path = os.path.join(FIXES_DIR, "Equipment_Vehicles_v2.csv")
    with open(v2_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Name",
                "ohfy__Abbreviation__c",
                "ohfy__Type__c",
                "ohfy__Status__c",
                "ohfy__Tare_Weight__c",
                "ohfy__Key__c",
                "ohfy__Fulfillment_Location__c",
                "RecordTypeId",
            ]
        )
        for row in equipment_rows:
            key = row["ohfy__Key__c"]
            wh_code = truck_warehouse.get(key, DEFAULT_WAREHOUSE)
            location_id = WAREHOUSE_MAP.get(wh_code, WAREHOUSE_MAP[DEFAULT_WAREHOUSE])

            warehouse_stats[wh_code] = warehouse_stats.get(wh_code, 0) + 1

            # Map picklist values (same as audit noted)
            equip_type = "Motorized Vehicle" if row["ohfy__Type__c"] == "Truck" else row["ohfy__Type__c"]
            status = "Operational" if row["ohfy__Status__c"] == "Active" else row["ohfy__Status__c"]

            writer.writerow(
                [
                    row["Name"],
                    row["ohfy__Abbreviation__c"],
                    equip_type,
                    status,
                    row["ohfy__Tare_Weight__c"],
                    key,
                    location_id,
                    RT_MOTORIZED_VEHICLE,
                ]
            )

    print(f"   Written: {v2_path} (235 rows)")
    print("   Warehouse distribution:")
    wh_names = {
        "1": "Gulf Mobile",
        "2": "Milton",
        "5": "Jackson",
        "6": "Gulfport",
        "7": "Montgomery",
        "9": "Birmingham",
        "10": "Huntsville",
        "11": "ABC Board",
        "99": "AL Liquor",
    }
    for code in sorted(warehouse_stats.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        name = wh_names.get(code, code)
        print(f"     {name} (WH {code}): {warehouse_stats[code]} trucks")

    # CSV 4: Route driver fix (all 308 routes get Mobile Driver for delivery,
    # skip special routes)
    print("\n8. Generating fix_route_drivers.csv...")
    # Get ALL route IDs (both linked and unlinked)
    all_route_ids = {}
    for line in route_ids_raw.strip().split("\n"):
        rid, rkey = line.split(",")
        all_route_ids[rkey] = rid
    # Add unlinked routes
    for route in classified["Delivery"]:
        all_route_ids[route["key"]] = route["id"]
    for route in classified["Special"]:
        all_route_ids[route["key"]] = route["id"]

    driver_path = os.path.join(FIXES_DIR, "fix_route_drivers.csv")
    delivery_count = 0
    with open(driver_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Id", "ohfy__Driver__c"])

        # All linked routes (211) are delivery routes
        for line in route_ids_raw.strip().split("\n"):
            rid, rkey = line.split(",")
            writer.writerow([rid, MOBILE_DRIVER_ID])
            delivery_count += 1

        # Unlinked delivery routes also get driver
        for route in classified["Delivery"]:
            writer.writerow([route["id"], MOBILE_DRIVER_ID])
            delivery_count += 1

    print(f"   Written: {driver_path} ({delivery_count} delivery routes)")
    print(f"   Skipped: {len(classified['Special'])} special routes (no driver)")

    # Write route classification report
    print("\n9. Writing route_classification.csv...")
    class_path = os.path.join(FIXES_DIR, "route_classification.csv")
    with open(class_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Route_Key", "Route_Name", "Category", "Has_Vehicle", "Gets_Driver"])
        # Linked delivery routes
        for line in route_ids_raw.strip().split("\n"):
            rid, rkey = line.split(",")
            writer.writerow([rkey, f"Route {rkey}", "Delivery", "Yes", "Yes"])
        # Unlinked delivery routes
        for route in classified["Delivery"]:
            writer.writerow([route["key"], route["name"], "Delivery (no truck match)", "No", "Yes"])
        # Special routes
        for route in classified["Special"]:
            writer.writerow([route["key"], route["name"], route["category"], "No", "No"])

    print(f"   Written: {class_path}")

    print("\n=== Done! Generated files: ===")
    print(f"  1. {clear_path}")
    print(f"  2. {delete_path}")
    print(f"  3. {v2_path}")
    print(f"  4. {driver_path}")
    print(f"  5. {class_path}")
    print("\n=== Load sequence: ===")
    print("  Step 1: sf data update bulk --file clear_route_vehicles.csv --sobject ohfy__Route__c --line-ending CRLF")
    print("  Step 2: sf data delete bulk --file delete_equipment.csv --sobject ohfy__Equipment__c --line-ending CRLF")
    print(
        "  Step 3: sf data import bulk --file Equipment_Vehicles_v2.csv --sobject ohfy__Equipment__c --line-ending CRLF"
    )
    print("  Step 4: Query new equipment IDs, generate relink CSV")
    print("  Step 5: sf data update bulk --file relink_route_vehicles.csv --sobject ohfy__Route__c --line-ending CRLF")
    print("  Step 6: sf data update bulk --file fix_route_drivers.csv --sobject ohfy__Route__c --line-ending CRLF")


if __name__ == "__main__":
    generate_csvs()
