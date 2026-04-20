import csv
from pathlib import Path

OUTPUT_PATH = Path(
    "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/classes/Data Science/16 Thesis/thesis_main/Data/raw/bank_ropa_cebu.csv"
)

HEADER = [
    "bank",
    "bm_code",
    "city",
    "property_type",
    "project_name",
    "address",
    "lot_area_sqm",
    "floor_area_sqm",
    "price",
    "description",
]


def parse_number(value: str):
    text = value.strip()
    if text == "":
        return ""
    if "." in text:
        return float(text)
    return int(text)


def parse_block_rows(bank: str, block: str):
    rows = []
    for raw_line in block.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 9:
            raise ValueError(f"Expected 9 fields in line, got {len(parts)}: {line}")
        bm_code, city, property_type, project_name, address, lot_area, floor_area, price, description = parts
        rows.append(
            [
                bank,
                bm_code,
                city,
                property_type,
                project_name,
                address,
                parse_number(lot_area),
                parse_number(floor_area),
                parse_number(price),
                description,
            ]
        )
    return rows


def build_south_hills_rows(block: str):
    rows = []
    for raw_line in block.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 5:
            raise ValueError(f"Expected 5 fields in South Hills line, got {len(parts)}: {line}")
        tct, lot_desc, lot_area, price, description_note = parts
        note = description_note.lower()
        has_improvement = "improvement" in note or "4-storey" in note or "bldg" in note
        property_type = "Residential - House and Lot" if has_improvement else "Residential - Vacant Lot"
        description = "residential lot with improvement" if has_improvement else "residential vacant lot"
        address = f"{lot_desc} South Hills Subd Brgy Buhisan Cebu City"
        rows.append(
            [
                "Bank of Commerce",
                tct,
                "Cebu City",
                property_type,
                "South Hills Subd",
                address,
                parse_number(lot_area),
                0,
                parse_number(price),
                description,
            ]
        )
    return rows


BPI_BLOCK = """
02210-CEB-045|Liloan|Residential - Vacant Lot|Primavera Hills|Lots 14 and 15 Block 13 Along Teasel Street Primavera Hills Barangay Yati Liloan Cebu|540|0|3000000|vacant lot
03627-CEB-072|Cebu City|Residential - Condominium Unit|Palaciego Uno Condominium|Unit 7-A 7th Floor Palaciego Uno Condominium Barangay Camputhaw Cebu City|0|74.93|4875000|condominium unit
04455-CEB-098|Cebu City|Residential - Townhouse|NLC Residence|Unit 8295-1 NLC Residence Barangay San Roque Cebu City|52.7|90|2800000|townhouse
05053-CEB-137|Cebu City|Residential - Condominium Unit|Xavierville City Condominium|Unit 301 Xavierville City Condominium Echavez Extension St Barangay Lorega San Miguel Cebu City|0|124.19|6700000|condominium unit
05054-CEB-137|Cebu City|Residential - Condominium Unit|Xavierville City Condominium|Unit 302 Xavierville City Condominium Echavez Extension St Barangay Lorega San Miguel Cebu City|0|102.45|5600000|condominium unit
05055-CEB-137|Cebu City|Residential - Condominium Unit|Xavierville City Condominium|Unit 303 Xavierville City Condominium Echavez Extension St Barangay Lorega San Miguel Cebu City|0|113.17|6200000|condominium unit
05056-CEB-137|Cebu City|Residential - Condominium Unit|Xavierville City Condominium|Unit 304 Xavierville City Condominium Echavez Extension St Barangay Lorega San Miguel Cebu City|0|118.32|6100000|condominium unit
05058-CEB-137|Cebu City|Residential - Condominium Unit|Xavierville City Condominium|Unit 403 Xavierville City Condominium Echavez Extension St Barangay Lorega San Miguel Cebu City|0|112.99|6100000|condominium unit
05084-CEB-137|Cebu City|Residential - Condominium Unit|Xavierville City Condominium|Unit 402 Xavierville City Condominium Echavez Extension St Barangay Lorega San Miguel Cebu City|0|102.45|5600000|condominium unit
05094-CEB-138|Cebu City|Residential - Townhouse||Lot 74 G and F Wilson Street Barangay Lahug Cebu City|130|184|6500000|townhouse
05546-CEB-174|Cebu City|Residential - Townhouse|South Glades Subd|Lot 6149-A-1-D South Glades Subd Lawaan Street Sitio Tambis Labangon Cebu City|76|82|3800000|townhouse
05561-CEB-176|Talisay City|Residential - House and Lot|NLC Residences 2|Unit C Lot 387-B-3 NLC Residences 2 Uldog St Carmen Cansojong Talisay City|39.4|39.4|3700000|house and lot
05571-CEB-180|Cebu City|Residential - House and Lot|Kirei Residences|Unit 5 Lot 10399-C-5 Hi-Way 77 Kirei Residences Cadahuan Talamban Cebu City|85|128|7500000|house and lot
05648-CEB-187|Cebu City|Residential - House and Lot|Rose Crest Residences|Lot 32 Rose Crest Residences San Jose Cebu City|80|137|6600000|house and lot
05699-CEB-192|Cebu City|Residential - House and Lot|The Rosepike at Forest Hills|Lot 6447-E-5 Unit C Phase 2 The Rosepike at Forest Hills Barangay Guadalupe Cebu City|68.5|206|11000000|house and lot
05701-CEB-194|Cebu City|Residential - House and Lot|Forest Hills Subdivision|Lot 6448 C4 and C5 Planas Street Forest Hills Subdivision Barangay Guadalupe Cebu City|1714|1819|93000000|house and lot
05876-CEB-212|Cebu City|Residential - House and Lot|Eggling Subdivision|Lot 8-K-4-D-4-B Cebu Trancentral Highway Eggling Subdivision Barangay Busay Cebu City|62|123|6800000|house and lot
05913-CEB-219|Cebu City|Residential - House and Lot|Sunrise Village|Lot 4270-B-6 R Abellanosa Street corner Sunrise Village Road Sunrise Village Barangay Inayawan Cebu City|349|442|10000000|house and lot
06014-CEB-227|Cebu City|Residential - House and Lot|Saint Anthony Residences|Lot 1-K-6-A Highway 77 Saint Anthony Residences Barangay Talamban Cebu City|72|67|5300000|house and lot
06061-CEB-230|Minglanilla|Residential - House and Lot|Velmiro Heights Subdivision|Lot 3 Block 12 Myrtle Street Velmiro Heights Subdivision Barangay Tunghaan Minglanilla|150|82.57|5500000|house and lot
06062-CEB-231|Minglanilla|Residential - House and Lot|Kamalaya II Residences|Lot 3 Block 4 Kamalaya II Residences Phase 1 Barangay Tunghaan Minglanilla|75|61|4200000|house and lot
06063-CEB-232|Minglanilla|Residential - House and Lot|Belmont Village|Lot 24 Block 1 Peace Street Belmont Village Barangay Pakigne Minglanilla|192|201|6600000|house and lot
06064-CEB-233|Minglanilla|Residential - House and Lot|Modena Subdivision|Lot 8 Block 8 Modena Subdivision Barangay Tunghaan Minglanilla|60|83|4200000|house and lot
06086-CEB-234|Cebu City|Residential - House and Lot|Maryville Subdivision|Lot 11297-C Dahlia Street Maryville Subdivision Phase 3 Barangay Talamban Cebu City|218|177.5|11300000|house and lot
06801-CEB-242|Cebu City|Residential - Townhouse|Naya Village|Lot 3-C 2nd Street Naya Village Barangay Tisa Cebu City|80|102|5500000|townhouse
06802-CEB-243|Cebu City|Residential - Townhouse|Tonito Homes|Lot 7014-C-3-B Unit 2 Tonito Homes Abi Abi Street Sun Valley Subdivision Barangay Calamba Cebu City|110|180|9700000|townhouse
06824-CEB-246|Cebu City|Residential - Condominium Unit|Horizons 101|Unit T1R27P 27th Floor Horizons 101 Tower 1 General Maxilom Avenue Barangay Central Poblacion Cebu City|0|60.3|11500000|condominium unit
06883-CEB-248|Cebu City|Residential - Condominium Unit|Azalea Place|Unit 220 22nd Floor Azalea Place Gorordo Avenue Barangay Lahug Cebu City|0|48|6800000|condominium unit
06884-CEB-249|Cebu City|Residential - Condominium Unit|Myvan Cityscape Tower II|Unit 1407 Myvan Cityscape Tower II Uptown Juana Osmena Street Barangay Camputhaw Cebu City|0|20.15|2950000|condominium unit
07005-CEB-250|Cebu City|Residential - Condominium Unit|Avida Towers Riala|Unit 2909 29th Floor Avida Towers Riala Tower 1 Jose Maria del Mar Street Cebu Asia IT Park Barangay Apas Cebu City|0|23.51|4500000|condominium unit
07016-CEB-252|Cebu City|Residential - House and Lot|North Belleza Subdivision|Lot 2 Block 1 North Belleza Subdivision Barangay San Jose Cebu City|99|111|7200000|house and lot
07020-CEB-255|Cebu City|Residential - Condominium Unit|Mivesa Garden Residences|Unit 609 Mivesa Garden Residences Building 2 Barangay Lahug Cebu City|0|20|3450000|condominium unit
07023-CEB-256|Cebu City|Residential - Condominium Unit|The Persimmon|Unit 6-C The Persimmon North Tower Barangay Mabolo Cebu City|0|41.32|6800000|condominium unit
04847-CEB-124|Consolacion|Residential - Townhouse|Pueblo El Grande Subdivision|Lot 69 Block 2 Pueblo El Grande Subdivision Phase 3 Barangay Tayud Consolacion|120|112|4950000|townhouse
05721-CEB-198|Consolacion|Residential - House and Lot|El Monteverde de Cebu|Lot 2 Block 1 New Orleans Street El Monteverde de Cebu Subdivision Barangay Lamac Consolacion|150|198|5800000|house and lot
05194-CEB-160|Consolacion|Residential - Townhouse|Villa Solana Subdivision|Lot 3 Block 2 Villa Solana Subdivision Phase 1 Barangay Tugbongan Consolacion|79|65|2400000|townhouse
04551-CEB-107|Lapu-Lapu City|Residential - House and Lot|White Sand Villas|Lot 3954-B1 to B-3 Paseo de Sta Ana corner unnamed road White Sand Villas Barangay Maribago Lapu-lapu City|732|785|15200000|house and lot
05131-CEB-154|Lapu-Lapu City|Residential - Townhouse|Bayswater Subdivision|Lot 7 Block 18 Orchidia Street Bayswater Subdivision Barangay Marigondon Lapu-lapu City|97|84.6|6400000|townhouse
05453-CEB-169|Lapu-Lapu City|Residential - Townhouse|Modena Subdivision|Lot 2 Caterina Street Modena Subdivision Barangay Basak Lapu-lapu City|90|78.9|5600000|townhouse
05545-CEB-173|Lapu-Lapu City|Residential - Townhouse|CKL Homes|Lot 10 Block 6 CKL Homes Barangay Agus Lapu-Lapu City|32|48|1600000|townhouse
05621-CEB-184|Lapu-Lapu City|Residential - House and Lot|Juanita Residences|Lot 15 PSD-07-073954 Juanita Residences Buaya Lapu-Lapu City|80.2|58|3400000|house and lot
05647-CEB-186|Lapu-Lapu City|Residential - House and Lot|Goldmine Residences|Lot 6 Block 3 Goldmine Residences Phase 1 Soong 1 Mactan Lapu-lapu City|55|75|3700000|house and lot
05765-CEB-203|Lapu-Lapu City|Residential - Townhouse|CKL Homes Subdivision|Lot 4 Block 3 CKL Homes Subdivision Barangay Agus Lapu-Lapu City|32|43|1600000|townhouse
05877-CEB-213|Lapu-Lapu City|Residential - House and Lot|Acasys Homes|Lot 2880-B-1 Acasys Homes Tirso Manus Road Barangay Basak Lapu-lapu City|68|135|6000000|house and lot
06123-CEB-235|Lapu-Lapu City|Residential - House and Lot|Acasys Homes|Lot 2880-B-4 Tirso Manus Road Acasys Homes Barangay Basak Lapu-lapu City|60|122|4500000|house and lot
06822-CEB-247|Lapu-Lapu City|Residential - Townhouse|Juanita Residences|Lot 5 Juanita Residences Barangay Buaya Lapu-lapu City|58|64|3050000|townhouse
07026-CEB-257|Lapu-Lapu City|Residential - Townhouse|Juanita Residences|Lot 7 Juanita Residences Barangay Buaya Lapu-lapu City|58|68|3300000|townhouse
01664-CEB-014|Liloan|Residential - Vacant Lot||Lot 958 Brgy Road Brgy Calero Liloan Cebu|7189|0|4560000|vacant lot
04850-CEB-127|Liloan|Residential - Townhouse|Northgate Subdivision|Lot 27 Block 2 Northgate Subdivision Barangay Poblacion Liloan|59|77|2660000|townhouse
06819-CEB-244|Liloan|Residential - House and Lot|Eastland Estate Subdivision|Lot 1 Gardenia Street Eastland Estate Subdivision Barangay Yati Liloan|87|62|4670000|house and lot
04553-CEB-108|Mandaue City|Residential - Townhouse|Dreamhomes Executive Village II|Lot 2 Block 2 Dreamhomes Executive Village II Barangay Basak Mandaue City|131|108|5300000|townhouse
05392-CEB-168|Mandaue City|Residential - Townhouse|Karls Town 1|Lot 1944-A-6-A-7 Karls Town 1 Jagobiao Mandaue City|55|78|3400000|townhouse
05718-CEB-197|Mandaue City|Residential - House and Lot|Karls Town II|Unit 28 Lot 16 Block 2 Karls Town II Barangay Maguikay Mandaue City|54|75|3700000|house and lot
06787-CEB-240|Mandaue City|Residential - Townhouse|Pereville Subdivision|Lot 3 Block 17 Pereville Subdivision Barangay Pagsabungan Mandaue City|50|80|5000000|townhouse
06820-CEB-245|Mandaue City|Residential - Condominium Unit|Amaia Steps North Tower|Unit 221 2nd Floor Amaia Steps North Tower Barangay Alang-alang Mandaue City|0|24.01|3270000|condominium unit
07019-CEB-254|Mandaue City|Residential - Condominium Unit|Midpoint Residences|Unit 2003 20th Floor Midpoint Residences Tower 1 AS Fortuna Barangay Banilad Mandaue City|0|24.35|3750000|condominium unit
05189-CEB-159|Minglanilla|Residential - Townhouse|Lucena Homes Subdivision|Lot 27 Block 1 Lucena Homes Subdivision Barangay Lower Pakigne Minglanilla|46|55|2000000|townhouse
05837-CEB-208|Minglanilla|Residential - House and Lot|Modena Subdivision Phase 2|Lot 4 Block 2 Modena Subdivision Phase 2 Barangay Tunghaan Minglanilla|60|73|3500000|house and lot
05879-CEB-214|Minglanilla|Residential - House and Lot|Monte Carlo Subdivision|Lot 5 Block 9 Monte Carlo Subdivision Barangay Vito Minglanilla|80|54|3000000|house and lot
05885-CEB-217|Minglanilla|Residential - Townhouse|Modena Subdivision Phase 4|Lot 1 Block 4 Modena Subdivision Phase 4 Barangay Tunghaan Minglanilla|85|72|4500000|townhouse
05036-CEB-136|Talisay City|Residential - Townhouse|NLC Residences 2|Lot 387-B-7 Unit G NLC Residences 2 Carmen Barangay Cansojong Talisay City|53.5|77.04|4000000|townhouse
05109-CEB-146|Talisay City|Residential - Townhouse|NLC Residences 2|Unit E Lot 387-B-5 NLC Residences 2 Carmen Barangay Cansojong Talisay City|39.4|87|3150000|townhouse
05562-CEB-178|Talisay City|Residential - Townhouse|Alberlyn Box Hill Residences|Lot 40 Block 1 Alberlyn Box Hill Residences Mohon Talisay City|70|65|3800000|townhouse
05744-CEB-200|Talisay City|Residential - House and Lot|Amber Homes|Lot 5-D Base Street Amber Homes Barangay Cansojong Talisay City|58|86|3300000|house and lot
05753-CEB-201|Talisay City|Residential - House and Lot|Amber Homes Phase 1|Lot 5-E Base Street Amber Homes Phase 1 Barangay Cansojong Talisay City|56|86|3300000|house and lot
05899-CEB-218|Talisay City|Residential - House and Lot|Bayswater Subdivision|Lot 21 Block 8 Bayswater Subdivision Barangay Pooc Talisay City|42|60|3500000|house and lot
05914-CEB-220|Talisay City|Residential - House and Lot|Alberlyn Box Hill Residences|Lot 2 Block 8 Alberlyn Box Hill Residences Barangay Mohon Talisay City|75|65|5000000|house and lot
06246-CEB-238|Talisay City|Residential - House and Lot|Alberlyn Box Hill Residences|Lot 34 Block 1 Alberlyn Box Hill Residences Barangay Mohon Talisay City|68|65|4170000|house and lot
07017-CEB-253|Talisay City|Residential - House and Lot|South Covina Subdivision|Lot 12 Block 2 South Covina Subdivision Barangay Dumlog Talisay City|70|68|4600000|house and lot
"""

METROBANK_BLOCK = """
10000000004428|Lapu-Lapu City|Residential - Condominium Unit|Mactan Oasis Garden|Bldg 9 Unit No 108 Mactan Oasis Garden Mactan Lapu-Lapu City|0|36.56|878000|condominium unit
10000000004429|Lapu-Lapu City|Residential - Condominium Unit|Mactan Oasis Garden|Bldg 9 Unit No 109 Mactan Oasis Garden Mactan Lapu-Lapu City|0|36.56|878000|condominium unit
10828000003220|Mandaue City|Residential - Townhouse|AGR Residences|Lot 4 Unit 4 AGR Residences Brgy Cubacub Mandaue City|110|165|5834000|townhouse
10828000003696|Mandaue City|Residential - House and Lot|Florentina 1 Townhomes|Lot 1619-A-2-B Florentina 1 Townhomes Canduman-Tawason Road Barangay Canduman Mandaue City|70|80|2949000|house and lot
10828000003810|Cebu City|Residential - Condominium Unit|San Remo Oasis Building 3|Unit U3301 3rd Floor San Remo Oasis Building 3 South Road Properties Cebu City|0|30.17|3651000|condominium unit
10828000003852|Cebu City|Residential - Condominium Unit|Sundance Residences Tower 1|Unit 11U 11th Floor Sundance Residences Tower 1 Barangay Guadalupe Cebu City|0|31.99|3775000|condominium unit
10828000003892|Cordova|Residential - House and Lot|Ajoya Subdivision|Lot 5 Block 16 Along Road Lot 24 Ajoya Subdivision Barangay Gabi Cordova|80|44|2788000|house and lot
10828000003897|Lapu-Lapu City|Residential - House and Lot|Villa del Rio Mactan Subdivision|Lot 33 Block 1 Villa del Rio Mactan Subdivision Barangay Babag 1 Lapu-Lapu City|120|296|7188000|house and lot
10828000003927|Mandaue City|Residential - Townhouse|Northwoods Residences|Lot 6 Block 4 Northwoods Residences Barangay Canduman Mandaue City|86|95|4674000|townhouse
10828000003928|Minglanilla|Residential - House and Lot|Midori Plains Subdivision|Lot 4 Block 6 Midori Plains Subdivision Barangay Tungkop Minglanilla|149|52|3923000|house and lot
10828000003930|Minglanilla|Residential - House and Lot|Fonte Versailles Subdivision|Lot 2 Block 7 Fonte Versailles Subdivision Phase 1 Barangay Tulay Minglanilla|203|189|6437000|house and lot
10828000003931|Lapu-Lapu City|Residential - House and Lot|Portville Mactan Subdivision|Lot 5 Block 8 Portville Mactan Subdivision Barangay Buaya Lapu-Lapu City|42|48|1694000|house and lot
10828000003932|Lapu-Lapu City|Residential - House and Lot|Portville Mactan Subdivision|Lot 24 Block 8 Portville Mactan Subdivision Barangay Buaya Lapu-Lapu City|42|48|1659000|house and lot
10828000003979|Minglanilla|Residential - House and Lot|Hacienda San Agustin Subdivision|Lot 1 Block 4 Hacienda San Agustin Subdivision Barangay Lower Calajo-an Minglanilla|294|166|7019000|house and lot
10828000003640|Cebu City|Residential - House and Lot||Lot 7545-B-1 Legaspi Street Barangay Sto Nino Cebu City|72|225|6788775|house and lot with improvement
10828000003644|Cebu City|Residential - House and Lot|Espina Village|Nos 095-A and 095-B 2nd Street Espina Village Barangay Guadalupe Cebu City|1000|581|38682225|house and lot
"""

SOUTH_HILLS_BLOCK = """
163050|Lot 12 Blk 14|150|3150000|residential vacant lot
163332|Lot 14 Blk 14|150|3150000|residential lot with 4-storey bldg
163333|Lot 15 Blk 14|150|3150000|residential lot with 4-storey bldg
163334|Lot 16 Blk 14|150|3150000|residential vacant lot
163335|Lot 17 Blk 14|150|3150000|residential vacant lot
163336|Lot 18 Blk 14|150|3150000|residential vacant lot
163338|Lot 20 Blk 14|150|3150000|residential vacant lot
163588|Lot 48 Blk 13|150|3150000|residential vacant lot
163590|Lot 50 Blk 13|150|3150000|residential vacant lot
163591|Lot 51 Blk 13|150|3150000|residential vacant lot
163740|Lot 3 Blk 31|300|4980000|residential vacant lot
163741|Lot 4 Blk 31|150|2490000|residential vacant lot
163742|Lot 5 Blk 31|150|2490000|residential vacant lot
163743|Lot 6 Blk 31|150|2490000|residential vacant lot
163744|Lot 7 Blk 31|150|2490000|residential vacant lot
163745|Lot 8 Blk 31|150|2490000|residential vacant lot
163746|Lot 9 Blk 31|150|2490000|residential vacant lot
163747|Lot 10 Blk 31|150|2490000|residential vacant lot
163749|Lot 12 Blk 31|150|2490000|residential vacant lot
163768|Lot 13 Blk 31|150|2490000|residential vacant lot
163771|Lot 16 Blk 31|150|2490000|residential vacant lot
163774|Lot 19 Blk 31|123|2041000|residential vacant lot
163775|Lot 23 Blk 31|150|2490000|residential vacant lot
163776|Lot 24 Blk 31|150|2490000|residential vacant lot
163782|Lot 43 Blk 1|150|2490000|residential vacant lot
164017|Lot 44 Blk 1|98|1627000|residential vacant lot
164018|Lot 45 Blk 1|150|2490000|residential vacant lot
164019|Lot 46 Blk 1|150|2490000|residential vacant lot
164020|Lot 47 Blk 1|150|2490000|residential vacant lot
164021|Lot 48 Blk 1|150|2490000|residential vacant lot
164022|Lot 49 Blk 1|150|2490000|residential vacant lot
164023|Lot 50 Blk 1|150|2490000|residential vacant lot
164024|Lot 51 Blk 1|150|2490000|residential vacant lot
164025|Lot 52 Blk 1|150|2490000|residential vacant lot
164026|Lot 53 Blk 1|150|2490000|residential vacant lot
164027|Lot 54 Blk 1|150|2490000|residential vacant lot
164028|Lot 55 Blk 1|150|2490000|residential vacant lot
164029|Lot 56 Blk 1|150|2490000|residential vacant lot
164030|Lot 57 Blk 1|150|2490000|residential vacant lot
164031|Lot 58 Blk 1|150|2490000|residential vacant lot
164033|Lot 2 Blk 31|300|4980000|residential vacant lot
164034|Lot 1 Blk 31|300|4980000|residential vacant lot
164035|Lot 27 Blk 31|150|2490000|residential vacant lot
164036|Lot 28 Blk 31|150|2490000|residential vacant lot
164037|Lot 29 Blk 31|150|2490000|residential vacant lot
164038|Lot 30 Blk 31|150|2490000|residential vacant lot
164039|Lot 31 Blk 31|150|2490000|residential vacant lot
164041|Lot 33 Blk 31|150|2490000|residential vacant lot
164042|Lot 34 Blk 31|150|2490000|residential vacant lot
164043|Lot 35 Blk 31|150|2490000|residential vacant lot
164044|Lot 36 Blk 31|150|2490000|residential vacant lot
164129|Lot 18 Blk 3|150|3150000|residential lot with 4-storey bldg
164130|Lot 36 Blk 24|243|5103000|residential vacant lot
164131|Lot 35 Blk 24|142|2982000|residential vacant lot
164132|Lot 34 Blk 24|142|2982000|residential vacant lot
164133|Lot 31 Blk 24|143|3003000|residential vacant lot
164134|Lot 30 Blk 24|142|2982000|residential vacant lot
164135|Lot 28 Blk 24|142|2982000|residential vacant lot
164136|Lot 29 Blk 24|143|3003000|residential vacant lot
164137|Lot 27 Blk 24|143|3003000|residential vacant lot
164138|Lot 26 Blk 24|142|2982000|residential vacant lot
164139|Lot 25 Blk 24|143|3003000|residential vacant lot
164140|Lot 24 Blk 24|142|3003000|residential vacant lot
164141|Lot 23 Blk 24|675|14175000|residential vacant lot
164148|Lot 22 Blk 23|150|3150000|residential vacant lot
164157|Lot 28 Blk 21|358|7518000|residential vacant lot
164509|Lot 4 Blk 3|178|3738000|residential vacant lot
164513|Lot 4 Blk 2|302|6342000|residential vacant lot
164517|Lot 10 Blk 32|150|2490000|residential vacant lot
164518|Lot 9 Blk 32|150|2490000|residential vacant lot
164519|Lot 8 Blk 32|150|2490000|residential vacant lot
164520|Lot 7 Blk 32|150|2490000|residential vacant lot
164521|Lot 6 Blk 32|150|2490000|residential vacant lot
164522|Lot 5 Blk 32|150|2490000|residential vacant lot
164523|Lot 4 Blk 32|150|2490000|residential vacant lot
164524|Lot 3 Blk 32|150|2490000|residential vacant lot
164525|Lot 2 Blk 32|150|2490000|residential vacant lot
164526|Lot 1 Blk 32|150|2490000|residential vacant lot
164723|Lot 24 Blk 8|168|3528000|residential vacant lot
164725|Lot 26 Blk 8|244|5124000|residential vacant lot
164727|Lot 2 Blk 9|160|3360000|residential vacant lot
164728|Lot 3 Blk 9|366|7686000|residential vacant lot
164729|Lot 4 Blk 9|242|5082000|residential vacant lot
164730|Lot 5 Blk 9|166|3486000|residential vacant lot
164731|Lot 6 Blk 9|146|3066000|residential vacant lot
164734|Lot 9 Blk 9|188|3948000|residential vacant lot
164735|Lot 10 Blk 9|119|2499000|residential vacant lot
164736|Lot 11 Blk 9|141|2961000|residential vacant lot
164737|Lot 12 Blk 9|150|3150000|residential vacant lot
164738|Lot 13 Blk 9|150|3150000|residential vacant lot
164991|Lot 22 Blk 9|300|6300000|residential vacant lot
164992|Lot 23 Blk 9|200|4200000|residential vacant lot
164993|Lot 24 Blk 9|200|4200000|residential vacant lot
164996|Lot 27 Blk 9|200|4200000|residential vacant lot
164998|Lot 29 Blk 9|150|3150000|residential vacant lot
164999|Lot 30 Blk 9|150|3150000|residential vacant lot
165000|Lot 31 Blk 9|150|3150000|residential vacant lot
165001|Lot 32 Blk 9|150|3150000|residential vacant lot
165002|Lot 33 Blk 9|200|4200000|residential vacant lot
165003|Lot 34 Blk 9|231|4851000|residential vacant lot
165011|Lot 1 Blk 10|156|3276000|residential vacant lot
165012|Lot 2 Blk 10|187|3927000|residential vacant lot
165013|Lot 3 Blk 10|200|4200000|residential vacant lot
165205|Lot 4 Blk 10|200|4200000|residential vacant lot
165206|Lot 5 Blk 10|200|4200000|residential vacant lot
165207|Lot 6 Blk 10|150|3150000|residential vacant lot
165208|Lot 7 Blk 10|150|3150000|residential vacant lot
165209|Lot 8 Blk 10|150|3150000|residential vacant lot
165210|Lot 9 Blk 10|187|3927000|residential vacant lot
165211|Lot 10 Blk 10|191|4011000|residential vacant lot
165212|Lot 12 Blk 10|174|3654000|residential vacant lot
165213|Lot 13 Blk 10|150|3150000|residential vacant lot
165214|Lot 14 Blk 10|150|3150000|residential vacant lot
165498|Lot 36 Blk 10|172|2856000|residential vacant lot
165499|Lot 37 Blk 10|150|2490000|residential vacant lot
165502|Lot 40 Blk 10|333|5528000|residential vacant lot
165503|Lot 41 Blk 10|164|2723000|residential vacant lot
165504|Lot 42 Blk 10|173|2872000|residential vacant lot
165505|Lot 43 Blk 10|156|2590000|residential vacant lot
165506|Lot 44 Blk 10|200|3320000|residential vacant lot
165507|Lot 45 Blk 10|200|3320000|residential vacant lot
165650|Lot 46 Blk 10|199|3304000|residential vacant lot
165651|Lot 47 Blk 10|213|3536000|residential vacant lot
165652|Lot 48 Blk 10|244|4051000|residential vacant lot
165653|Lot 49 Blk 10|274|4549000|residential vacant lot
165654|Lot 50 Blk 10|411|6823000|residential vacant lot
165655|Lot 35 Blk 10|150|2490000|residential vacant lot
165656|Lot 51 Blk 10|403|6690000|residential vacant lot
165657|Lot 52 Blk 10|373|6192000|residential vacant lot
165658|Lot 53 Blk 10|544|9031000|residential vacant lot
165659|Lot 4 Blk 15|150|3150000|residential vacant lot
166008|Lot 5 Blk 15|150|3150000|residential vacant lot
166009|Lot 1 Blk 29|380|6308000|residential vacant lot
166010|Lot 1 Blk 30|150|2490000|residential vacant lot
166011|Lot 2 Blk 30|150|2490000|residential vacant lot
166012|Lot 3 Blk 30|150|2490000|residential vacant lot
166013|Lot 15 Blk 10|224|4704000|residential vacant lot
166014|Lot 16 Blk 10|150|3150000|residential vacant lot
166015|Lot 17 Blk 10|128|2688000|residential vacant lot
166016|Lot 18 Blk 10|151|3171000|residential vacant lot
166130|Lot 20 Blk 10|150|3150000|residential vacant lot
166131|Lot 21 Blk 10|150|3150000|residential vacant lot
166132|Lot 22 Blk 10|150|3150000|residential vacant lot
166133|Lot 23 Blk 10|150|3150000|residential vacant lot
166134|Lot 24 Blk 10|150|3150000|residential vacant lot
166135|Lot 25 Blk 10|209|4389000|residential vacant lot
166136|Lot 26 Blk 10|287|6027000|residential vacant lot
166137|Lot 27 Blk 10|308|5113000|residential vacant lot
166138|Lot 28 Blk 10|233|3868000|residential vacant lot
166139|Lot 29 Blk 10|150|2490000|residential vacant lot
166216|Lot 34 Blk 10|165|2739000|residential vacant lot
166217|Lot 33 Blk 10|150|2490000|residential vacant lot
166218|Lot 32 Blk 10|150|2490000|residential vacant lot
166219|Lot 31 Blk 10|150|2490000|residential vacant lot
166220|Lot 30 Blk 10|150|2490000|residential vacant lot
166221|Lot 22 Blk 30|150|2490000|residential vacant lot
166222|Lot 21 Blk 30|150|2490000|residential vacant lot
166223|Lot 20 Blk 30|150|2490000|residential vacant lot
166224|Lot 19 Blk 30|254|4217000|residential vacant lot
166390|Lot 16 Blk 30|150|2490000|residential vacant lot
166391|Lot 15 Blk 30|150|2490000|residential vacant lot
166392|Lot 14 Blk 30|150|2490000|residential vacant lot
166393|Lot 13 Blk 30|150|2490000|residential vacant lot
166394|Lot 12 Blk 30|150|2490000|residential vacant lot
166395|Lot 11 Blk 30|150|2490000|residential vacant lot
166398|Lot 8 Blk 30|150|2490000|residential vacant lot
166683|Lot 7 Blk 30|150|2490000|residential vacant lot
166684|Lot 6 Blk 30|150|2490000|residential vacant lot
166686|Lot 4 Blk 30|150|2490000|residential vacant lot
166688|Lot 12 Blk 5|262|6000000|residential vacant lot
166689|Lot 12 Blk 4|327|6867000|residential vacant lot
166691|Lot 23 Blk 30|150|2490000|residential vacant lot
166692|Lot 24 Blk 30|150|2490000|residential vacant lot
166693|Lot 25 Blk 30|150|2490000|residential vacant lot
"""

BOC_NON_SOUTH_BLOCK = """
151764 & 151765|Cebu City|Residential - House and Lot||Lots 8 and 3 Blk 2 Bontores St Brgy Basak Cebu City|463|0|8064000|house and lot with improvement
107-2018007636|Cebu City|Residential - Condominium Unit|Mivesa Garden Residences|Unit 202 2/F Mivesa Garden Residences Building 4 Southwest Salinas Drive Extension Cebu City|0|27.57|2868000|condominium unit
111-2019001634|Consolacion|Residential - Townhouse|Anami Homes North Subd|Lot 12 Blk 6 Road Lot 8 Anami Homes North Subd Brgy Jugan Consolacion Cebu|55|0|3116000|townhouse
111-2021001527|Mandaue City|Residential - House and Lot||Lot 243-F-1 Brgy Looc Mandaue Cebu|252|0|7476000|residential lot with 2-storey bldg
111-2023003372|Mandaue City|Residential - Condominium Unit|Amaia Steps Mandaue|Unit 532 Tower 1 Amaia Steps Mandaue Plaridel Street Corner UN Avenue Barangay Alangalang Mandaue City|0|32.84|3613000|condominium unit
41211|Lapu-Lapu City|Residential - House and Lot|Villa Verna Subd|Lot 27 Blk4 Villa Verna Subd Bgy Marigondon Lapu-Lapu City|732|0|7833000|residential lot with improvement
62510|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 29 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|130|0|1339000|residential vacant lot
62511|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 30 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|128|0|1319000|residential vacant lot
62512|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 31 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|145|0|1494000|residential vacant lot
62513|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 32 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|182|0|1875000|residential vacant lot
62514|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 33 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|58|0|598000|residential vacant lot
62515|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 34 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|382|0|3935000|residential vacant lot
62516|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 36 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|40|0|412000|residential vacant lot
62517|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 35 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|220|0|2266000|residential vacant lot
62523|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 42 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|140|0|1442000|residential vacant lot
62524|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 43 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|130|0|1339000|residential vacant lot
62527|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 46 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|130|0|1339000|residential vacant lot
62532|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 51 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|289|0|3122000|residential vacant lot
62533|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 52 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|265|0|2862000|residential vacant lot
62534|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 53 Blk 3 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|260|0|2678000|residential vacant lot
62539|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 4 Blk 4 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|134|0|1381000|residential vacant lot
62542|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 7 Blk 4 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|124|0|1439000|residential vacant lot
62556|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 1 Blk 5 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|273|0|4095000|residential vacant lot
62581|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 13 Blk 9 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|176|0|1812000|residential vacant lot
62582|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 14 Blk 9 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|217|0|2236000|residential vacant lot
62594|Lapu-Lapu City|Residential - House and Lot|Villa Illuminada Subd|Lot 7 Blk 8 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|125|0|2922000|residential lot with improvement
62618|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 25 Blk 9 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|135|0|1391000|residential vacant lot
62620|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 26 Blk 9 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|136|0|1578000|residential vacant lot
62621|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 27 Blk 9 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|136|0|1578000|residential vacant lot
62622|Lapu-Lapu City|Residential - Vacant Lot|Villa Illuminada Subd|Lot 28 Blk 9 Villa Illuminada Subd Brgy Pajac Lapu-Lapu City|136|0|1578000|residential vacant lot
110-2021001083|Lapu-Lapu City|Residential - Condominium Unit|8 Newtown Boulevard|Unit 9C Cluster 4 9/F 8 Newtown Boulevard Mactan Newtown Brgy Mactan Lapu-Lapu City|0|49.6|7490000|condominium unit
110-2013003030|Lapu-Lapu City|Residential - Townhouse|BF Homes|Lot 16 Blk 5 BF Homes Fuentes Road Agus Pajac Lapu-Lapu City|44|0|2997000|townhouse
91958|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|3620-R Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
91960|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|3620-T Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
91964|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|3620-X Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
91972|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|3620-FF Villa Verna Subdivision Bo Bulacao Talisay City|150|0|1875000|residential vacant lot
91973|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|3620-GG Villa Verna Subdivision Bo Bulacao Talisay City|149|0|1863000|residential vacant lot
91978|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|3620-LL Villa Verna Subdivision Brgy Bulacao Talisay City|110|0|1375000|residential vacant lot
91980|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|3620-NN Villa Verna Subdivision Bo Bulacao Talisay City|161|0|2013000|residential vacant lot
92264|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 1 Blk 1 Villa Verna Subdivision Bo Bulacao Talisay City|1043|0|13038000|residential vacant lot
92306|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 4 Blk 4 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92315|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 13 Blk 4 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92329|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 11 Blk 5 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92330|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 12 Blk 5 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92366|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 8 Blk 8 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92372|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 2 Blk 9 Villa Verna Subdivision Bo Bulacao Talisay City|112|0|1501000|residential vacant lot
92373|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 3 Blk 9 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92374|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 4 Blk 9 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92375|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 5 Blk 9 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92376|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 6 Blk 9 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92381|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 11 Blk 9 Villa Verna Subdivision Bo Bulacao Talisay City|119|0|1595000|residential vacant lot
92383|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 1 Blk 10 Villa Verna Subdivision Bo Bulacao Talisay City|132|0|1769000|residential vacant lot
92385|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 3 Blk 10 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92394|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 12 Blk 10 Villa Verna Subdivision Bo Bulacao Talisay City|134|0|1675000|residential vacant lot
92396|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 14 Blk 10 Villa Verna Subdivision Bo Bulacao Talisay City|112|0|1400000|residential vacant lot
92402|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 5 Blk 11 Villa Verna Subdivision Bo Bulacao Talisay City|100|0|1250000|residential vacant lot
92404|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 7 Blk 11 Villa Verna Subdivision Bo Bulacao Talisay City|149|0|1997000|residential vacant lot
92408|Talisay City|Residential - Vacant Lot|Villa Verna Subdivision|Lot 11 Blk 11 Villa Verna Subdivision Bo Bulacao Talisay City|99|0|1238000|residential vacant lot
T-54021|Minglanilla|Residential - Vacant Lot||Lot 9205 Sitio Abono Hills Brgy Tunghaan Minglanilla Cebu|9049.29|0|22493000|agri-residential vacant lot
T-54022|Minglanilla|Residential - Vacant Lot||Lot 10649 Brgy Pitago 2 Minglanilla Cebu|3811|0|5717000|residential vacant lot
"""


LANDBANK_BLOCK = """
13050000000945|Cebu City|Residential - Vacant Lot|Ridgedale Subdivision|Saxophone corner Sapphire Streets Ridgedale Subdivision Barangay San Jose Talamban Cebu City|246|0|2977000|residential vacant lot
"""

CBS_BLOCK = """
|Cebu City|Residential - Vacant Lot|Pristine Grove Residences|1-A-4-C Pristine Grove Residences Talamban Cebu City|142|0|4850000|residential vacant lot
|Talisay City|Residential - House and Lot|Azienda Genova|Lot 47 Blk 2 Azienda Genova Brgy Maghaway Talisay City Cebu|88|65|2860000|residential house and lot
|Cebu City|Residential - House and Lot|Camella Riverwalk|Blk 4 Lot 24 Camella Riverwalk Talamban Cebu City|66|46|2600000|residential house and lot
|Lapu-Lapu City|Residential - House and Lot|La Aldea Del Sol|Blk 2B Lot 18 La Aldea Del Sol Brgy Bankal Lapu-lapu City|72|53.6|3400000|residential house and lot
|Compostela|Residential - House and Lot|AMOA Enclave 4|Lot 3 Blk 12 AM0500 AMOA Enclave 4 Tamiao Compostela Cebu|138|46|3400000|one storey residential
"""


def main():
    rows = []
    rows.extend(parse_block_rows("BPI", BPI_BLOCK))
    rows.extend(parse_block_rows("Metrobank", METROBANK_BLOCK))
    rows.extend(parse_block_rows("Bank of Commerce", BOC_NON_SOUTH_BLOCK))
    rows.extend(build_south_hills_rows(SOUTH_HILLS_BLOCK))
    rows.extend(parse_block_rows("Landbank", LANDBANK_BLOCK))
    rows.extend(parse_block_rows("China Bank Savings", CBS_BLOCK))
    rows.extend(parse_block_rows("Landbank", LANDBANK_BLOCK))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADER)
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
