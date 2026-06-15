"""Data-integrity EDA passes for the stratified Metro Cebu ABTs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


STRATA = {
    "Condo": "abt_condo.csv",
    "Houses": "abt_houses.csv",
    "Lot": "abt_lot.csv",
}
MASTER_NAME = "Master"
MASTER_FILE = "abt_clean.csv"
MCRAI_COLS = [
    "mcrai_education",
    "mcrai_grocery",
    "mcrai_health",
    "mcrai_hospitals",
    "mcrai_recreation",
    "mcrai_security",
    "mcrai_tourism",
    "mcrai_retail_density",
    "mcrai_composite",
]
LGU_ORDER = [
    "Cebu City",
    "Mandaue City",
    "Lapu-Lapu City",
    "Talisay City",
    "Minglanilla",
    "Consolacion",
]
DATE_TOKENS = ("date", "time", "year", "vintage", "listed", "scraped", "timestamp", "created", "updated")
SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
DATA_DIR = THESIS_DIR / "Data" / "processed"
RAW_LAMUDI_PATH = THESIS_DIR / "Data" / "webscraping-lamudi" / "lamudi_cebu_full.csv"
OUTPUT_DIR = THESIS_DIR / "EDA" / "plots" / "09_data_integrity"
TABLES_DIR = THESIS_DIR / "EDA" / "tables"
WRITTEN_FILES: list[Path] = []


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def configure_plotting() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.dpi"] = 150


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150, format="png")
    plt.close(fig)
    WRITTEN_FILES.append(path)
    print(f"Saved -> {path}")


def save_table(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False)
    WRITTEN_FILES.append(path)
    print(f"Saved -> {path}")


def save_text(text: str, path: Path) -> None:
    path.write_text(text, encoding="utf-8")
    WRITTEN_FILES.append(path)
    print(f"Saved -> {path}")


def print_written_files() -> None:
    section_header("FILES WRITTEN")
    for path in WRITTEN_FILES:
        print(path)


def staggered_horizontal_labels(labels: list[str]) -> list[str]:
    return [f"{label}\n" if index % 2 == 0 else f"\n{label}" for index, label in enumerate(labels)]


def section_header(title: str) -> None:
    print(f"\n{'=' * 88}")
    print(title)
    print(f"{'=' * 88}")


def format_float_table(frame: pd.DataFrame, digits: int = 4) -> str:
    return frame.to_string(
        index=False,
        float_format=lambda value: f"{value:,.{digits}f}" if pd.notna(value) else "nan",
    )


def load_main_datasets() -> dict[str, pd.DataFrame]:
    datasets: dict[str, pd.DataFrame] = {}
    for label, filename in {**STRATA, MASTER_NAME: MASTER_FILE}.items():
        path = DATA_DIR / filename
        frame = pd.read_csv(path)
        datasets[label] = frame.copy()
        print(f"Loaded {label:<7} -> {path} ({len(frame):,} rows x {frame.shape[1]} cols)")
    return datasets


def order_lgus(values: pd.Index | pd.Series | list[str]) -> list[str]:
    if isinstance(values, pd.Series):
        candidates = values.dropna().astype(str).tolist()
    else:
        candidates = [str(value) for value in values if pd.notna(value)]
    ordered = [city for city in LGU_ORDER if city in candidates]
    remainder = sorted(city for city in candidates if city not in LGU_ORDER)
    return ordered + remainder


def group_coordinate_clusters(df: pd.DataFrame, decimals: int = 6) -> pd.DataFrame:
    coords = df.copy()
    coords["lat_round"] = coords["latitude"].round(decimals)
    coords["lon_round"] = coords["longitude"].round(decimals)
    grouped = (
        coords.groupby(["lat_round", "lon_round"], dropna=False)
        .agg(
            cluster_size=("property_id", "size"),
            cities=("city", lambda values: ", ".join(sorted(pd.Series(values).dropna().astype(str).unique()))),
        )
        .reset_index()
        .sort_values(by=["cluster_size", "lat_round", "lon_round"], ascending=[False, True, True])
        .reset_index(drop=True)
    )
    return grouped


def cluster_row_share(cluster_sizes: pd.Series, lower: int | None = None, upper: int | None = None) -> float:
    mask = pd.Series(True, index=cluster_sizes.index)
    if lower is not None:
        mask &= cluster_sizes >= lower
    if upper is not None:
        mask &= cluster_sizes <= upper
    return float(cluster_sizes.loc[mask].sum())


def pass2_geocoding_precision(datasets: dict[str, pd.DataFrame]) -> dict[str, dict[str, object]]:
    section_header("PASS 2 - GEOCODING PRECISION AUDIT")
    summary: dict[str, dict[str, object]] = {}

    for label, df in datasets.items():
        clusters = group_coordinate_clusters(df, decimals=6)
        cluster_sizes = clusters["cluster_size"]
        cluster_distribution = (
            cluster_sizes.value_counts()
            .rename_axis("cluster_size")
            .reset_index(name="coordinate_cluster_count")
            .sort_values("cluster_size")
            .reset_index(drop=True)
        )
        cluster_distribution["rows_in_clusters"] = (
            cluster_distribution["cluster_size"] * cluster_distribution["coordinate_cluster_count"]
        )
        largest_clusters = clusters.head(25).rename(
            columns={
                "lat_round": "latitude",
                "lon_round": "longitude",
            }
        )
        save_table(
            cluster_distribution,
            TABLES_DIR / f"eda_09_coordinate_cluster_size_distribution_{label.lower()}.csv",
        )
        save_table(
            largest_clusters,
            TABLES_DIR / f"eda_09_largest_coordinate_clusters_{label.lower()}.csv",
        )
        total_rows = int(len(df))
        unique_rows = cluster_row_share(cluster_sizes, lower=1, upper=1)
        rows_2_4 = cluster_row_share(cluster_sizes, lower=2, upper=4)
        rows_5_plus = cluster_row_share(cluster_sizes, lower=5)
        rows_10_plus = cluster_row_share(cluster_sizes, lower=10)
        largest = clusters.iloc[0]

        print(f"\n[{label}] Geocoding cluster summary")
        print(f"Total unique coordinates: {len(clusters):,}")
        print(f"Total rows: {total_rows:,}")
        print(f"% of rows at unique coords: {100 * unique_rows / total_rows:,.2f}%")
        print(f"% of rows in clusters of 2-4: {100 * rows_2_4 / total_rows:,.2f}%")
        print(f"% of rows in clusters of 5+: {100 * rows_5_plus / total_rows:,.2f}%")
        print(f"% of rows in clusters of 10+: {100 * rows_10_plus / total_rows:,.2f}%")
        print("\nTop 10 most populated coordinate clusters")
        print(
            clusters.head(10).rename(
                columns={
                    "lat_round": "latitude",
                    "lon_round": "longitude",
                    "cluster_size": "cluster_size",
                    "cities": "cities",
                }
            ).to_string(index=False)
        )
        print(
            "Interpretation: any cluster with more than 10 properties at the same coordinate suggests "
            "geocoding fallback to a barangay or city centroid, making those rows spatially indistinguishable to the model."
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        bins = np.arange(0.5, cluster_sizes.max() + 1.5, 1)
        ax.hist(cluster_sizes, bins=bins, color="#4c78a8", edgecolor="white")
        ax.set_yscale("log")
        ax.set_title(f"{label}: Geocoding cluster size distribution")
        ax.set_xlabel("Number of properties at a single coord")
        ax.set_ylabel("Number of coordinate clusters (log scale)")
        save_figure(fig, OUTPUT_DIR / f"{label}_geocoding_clusters.png")

        summary[label] = {
            "unique_coords": int(len(clusters)),
            "total_rows": total_rows,
            "largest_cluster_size": int(largest["cluster_size"]),
            "largest_cluster_lat": float(largest["lat_round"]),
            "largest_cluster_lon": float(largest["lon_round"]),
        }

    return summary


def find_date_like_columns(columns: pd.Index) -> list[str]:
    return [column for column in columns if any(token in column.lower() for token in DATE_TOKENS)]


def summarize_date_like_column(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    series = frame[column]
    parsed = pd.to_datetime(series, errors="coerce")
    usable = parsed.dropna()

    if usable.empty and pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            return pd.DataFrame(
                [
                    {
                        "column": column,
                        "dtype": str(series.dtype),
                        "null_rate_pct": series.isna().mean() * 100,
                        "min": "nan",
                        "p25": "nan",
                        "p50": "nan",
                        "p75": "nan",
                        "max": "nan",
                    }
                ]
            )
        stats = numeric.quantile([0.25, 0.5, 0.75])
        return pd.DataFrame(
            [
                {
                    "column": column,
                    "dtype": str(series.dtype),
                    "null_rate_pct": series.isna().mean() * 100,
                    "min": numeric.min(),
                    "p25": stats.loc[0.25],
                    "p50": stats.loc[0.5],
                    "p75": stats.loc[0.75],
                    "max": numeric.max(),
                }
            ]
        )

    if usable.empty:
        non_null = series.dropna().astype(str)
        return pd.DataFrame(
            [
                {
                    "column": column,
                    "dtype": str(series.dtype),
                    "null_rate_pct": series.isna().mean() * 100,
                    "min": non_null.min() if not non_null.empty else "nan",
                    "p25": "unparsed",
                    "p50": "unparsed",
                    "p75": "unparsed",
                    "max": non_null.max() if not non_null.empty else "nan",
                }
            ]
        )

    stats = usable.quantile([0.25, 0.5, 0.75])
    return pd.DataFrame(
        [
            {
                "column": column,
                "dtype": str(series.dtype),
                "null_rate_pct": series.isna().mean() * 100,
                "min": usable.min(),
                "p25": stats.loc[0.25],
                "p50": stats.loc[0.5],
                "p75": stats.loc[0.75],
                "max": usable.max(),
            }
        ]
    )


def build_vintage_search_report(search_hits: dict[str, list[str]]) -> str:
    lines = ["Listing vintage search results:"]
    for label, matches in search_hits.items():
        if matches:
            lines.append(f"- {label}: {', '.join(matches)}")
        else:
            lines.append(f"- {label}: NO MATCHING COLUMNS")
    return "\n".join(lines) + "\n"


def pass3_listing_vintage(datasets: dict[str, pd.DataFrame]) -> dict[str, object]:
    section_header("PASS 3 - LISTING VINTAGE / SCRAPE DATE CHECK")
    search_hits: dict[str, list[str]] = {label: find_date_like_columns(df.columns) for label, df in datasets.items()}
    raw_hits: list[str] = []

    if RAW_LAMUDI_PATH.exists():
        raw_columns = pd.read_csv(RAW_LAMUDI_PATH, nrows=0).columns
        raw_hits = find_date_like_columns(raw_columns)
        search_hits["lamudi_cebu_full"] = raw_hits
    else:
        search_hits["lamudi_cebu_full"] = []

    vintage_found = any(search_hits.values())
    vintage_summary: dict[str, object] = {"found": vintage_found, "search_hits": search_hits}

    for label, matches in search_hits.items():
        print(f"\n[{label}] matching date-like columns: {matches if matches else 'None'}")

    if not vintage_found:
        message = "NO LISTING VINTAGE COLUMN FOUND - scrape window must be documented externally."
        print(f"\n{message}")
        placeholder = OUTPUT_DIR / "listing_vintage_NOT_FOUND.txt"
        save_text(build_vintage_search_report(search_hits), placeholder)
        vintage_summary["message"] = message
        return vintage_summary

    plotted = False
    plot_column: str | None = None
    plot_ranges: dict[str, tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]] = {}

    for label, matches in search_hits.items():
        if label == "lamudi_cebu_full":
            if not matches:
                continue
            raw_df = pd.read_csv(RAW_LAMUDI_PATH, usecols=matches)
            for column in matches:
                print(f"\n[{label}] {column}")
                print(summarize_date_like_column(raw_df, column).to_string(index=False))
            continue

        df = datasets[label]
        for column in matches:
            print(f"\n[{label}] {column}")
            print(summarize_date_like_column(df, column).to_string(index=False))

    for candidate_label in STRATA:
        candidate_matches = search_hits.get(candidate_label, [])
        for column in candidate_matches:
            parsed_all = {
                label: pd.to_datetime(datasets[label][column], errors="coerce")
                for label in STRATA
                if column in datasets[label].columns
            }
            if len(parsed_all) == len(STRATA) and all(series.notna().any() for series in parsed_all.values()):
                fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=False)
                for ax, label in zip(axes, STRATA.keys()):
                    values = parsed_all[label].dropna()
                    sns.histplot(values, bins=30, ax=ax, color="#4c78a8")
                    ax.set_title(f"{label} - {column}")
                    ax.set_xlabel("Listing date")
                    ax.set_ylabel("Count")
                    plot_ranges[label] = (values.min(), values.quantile(0.5), values.max())
                save_figure(fig, OUTPUT_DIR / "listing_vintage_distribution.png")
                plot_column = column
                plotted = True
                break
        if plotted:
            break

    if not plotted:
        placeholder = OUTPUT_DIR / "listing_vintage_NOT_FOUND.txt"
        save_text(build_vintage_search_report(search_hits), placeholder)
        print("Date-like columns were found, but none propagated as a usable per-stratum distribution for plotting.")

    vintage_summary["plot_column"] = plot_column
    vintage_summary["plot_ranges"] = plot_ranges
    return vintage_summary


def pass4_mcrai_parity(datasets: dict[str, pd.DataFrame]) -> dict[str, int]:
    section_header("PASS 4 - PER-LGU MCRAI FEATURE PARITY")
    flagged_counts: dict[str, int] = {}

    for label in STRATA:
        df = datasets[label]
        mean_table = df.groupby("city")[MCRAI_COLS].mean()
        mean_table = mean_table.reindex(order_lgus(mean_table.index))
        zero_rate = df.groupby("city")[MCRAI_COLS].apply(lambda frame: (frame == 0).mean() * 100)
        zero_rate = zero_rate.reindex(mean_table.index)
        save_table(mean_table.reset_index(), TABLES_DIR / f"eda_09_mcrai_mean_by_lgu_{label.lower()}.csv")
        save_table(zero_rate.reset_index(), TABLES_DIR / f"eda_09_mcrai_zero_rate_by_lgu_{label.lower()}.csv")

        print(f"\n[{label}] Mean MCRAI by LGU")
        print(format_float_table(mean_table.reset_index(), digits=4))
        print(f"\n[{label}] Zero-rate (%) by LGU")
        print(format_float_table(zero_rate.reset_index(), digits=2))

        column_means = mean_table.mean(axis=0)
        flag_rows: list[dict[str, object]] = []
        for city, row in mean_table.iterrows():
            for column in MCRAI_COLS:
                value = row[column]
                baseline = column_means[column]
                if pd.isna(value) or pd.isna(baseline) or baseline == 0:
                    continue
                if value > 3 * baseline or value < baseline / 3:
                    flag_rows.append(
                        {
                            "city": city,
                            "mcrai_category": column,
                            "value": value,
                            "across_lgu_mean": baseline,
                            "ratio_to_mean": value / baseline,
                        }
                    )

        flagged = pd.DataFrame(flag_rows)
        if flagged.empty:
            flagged = pd.DataFrame(columns=["city", "mcrai_category", "value", "across_lgu_mean", "ratio_to_mean"])
        save_table(flagged, TABLES_DIR / f"eda_09_mcrai_parity_flags_{label.lower()}.csv")
        flagged_counts[label] = int(len(flagged))
        if flagged.empty:
            print(f"\n[{label}] No LGU x category cells outside the 3x band.")
        else:
            print(f"\n[{label}] Flagged LGU x category cells outside the 3x band")
            print(format_float_table(flagged, digits=4))

        if mean_table.empty:
            print(f"\n[{label}] No MCRAI rows available for heatmap.")
        else:
            centered = mean_table.subtract(column_means, axis=1)
            fig, ax = plt.subplots(figsize=(14, 6))
            sns.heatmap(
                centered,
                annot=mean_table,
                fmt=".2f",
                cmap="coolwarm",
                center=0,
                linewidths=0.4,
                cbar_kws={"label": "Deviation from across-LGU mean"},
                ax=ax,
            )
            ax.set_title(f"{label} - Mean MCRAI by LGU (column-centered)")
            ax.set_xlabel("MCRAI category", labelpad=22)
            ax.set_ylabel("LGU")
            ax.set_xticklabels(staggered_horizontal_labels(list(centered.columns)), rotation=0, ha="center")
            ax.tick_params(axis="x", length=0, pad=8)
            save_figure(fig, OUTPUT_DIR / f"{label}_mcrai_by_lgu_heatmap.png")

    return flagged_counts


def duplicate_group_counts(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    usable = df.dropna(subset=group_cols).copy()
    grouped = (
        usable.groupby(group_cols, dropna=False)
        .agg(group_size=("property_id", "size"))
        .reset_index()
    )
    return grouped[grouped["group_size"] > 1].sort_values(by="group_size", ascending=False).reset_index(drop=True)


def hard_duplicate_examples(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    working["lat_round_5"] = working["latitude"].round(5)
    working["lon_round_5"] = working["longitude"].round(5)
    group_cols = ["city", "lat_round_5", "lon_round_5", "area_sqm", "price_php"]
    usable = working.dropna(subset=group_cols).copy()

    grouped = (
        usable.groupby(group_cols, dropna=False)
        .agg(
            group_size=("property_id", "size"),
            property_ids=("property_id", lambda values: ", ".join(str(value) for value in sorted(values))),
            property_name=("property_name", lambda values: " | ".join(pd.Series(values).dropna().astype(str).unique())),
        )
        .reset_index()
    )
    grouped = grouped[grouped["group_size"] > 1].sort_values(by="group_size", ascending=False).reset_index(drop=True)
    return grouped.head(5)[["property_ids", "property_name", "city", "area_sqm", "price_php", "group_size"]]


def pass5_duplicate_detection(datasets: dict[str, pd.DataFrame]) -> dict[str, dict[str, int]]:
    section_header("PASS 5 - DUPLICATE LISTING DETECTION")
    counts_summary: dict[str, dict[str, int]] = {}
    plot_rows: list[dict[str, object]] = []

    for label, df in datasets.items():
        working = df.copy()
        working["lat_round_5"] = working["latitude"].round(5)
        working["lon_round_5"] = working["longitude"].round(5)

        soft = duplicate_group_counts(working, ["city", "address"])
        coord = duplicate_group_counts(working, ["lat_round_5", "lon_round_5"])
        hard = duplicate_group_counts(working, ["city", "lat_round_5", "lon_round_5", "area_sqm", "price_php"])

        counts_summary[label] = {
            "soft": int(len(soft)),
            "coord": int(len(coord)),
            "hard": int(len(hard)),
        }

        print(f"\n[{label}] Duplicate group counts")
        print(f"Soft match groups: {len(soft):,}")
        print(f"Coordinate match groups: {len(coord):,}")
        print(f"Hard match groups: {len(hard):,}")

        print(f"\n[{label}] Top 5 hard-match duplicate groups")
        top5 = hard_duplicate_examples(df)
        save_table(top5, TABLES_DIR / f"eda_09_duplicate_hard_examples_{label.lower()}.csv")
        if top5.empty:
            print("No hard-match duplicate groups found.")
        else:
            print(top5.to_string(index=False))

        for strictness, count in counts_summary[label].items():
            plot_rows.append({"dataset": label, "strictness": strictness, "duplicate_groups": count})

    plot_df = pd.DataFrame(plot_rows)
    save_table(plot_df, TABLES_DIR / "eda_09_duplicate_counts.csv")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=plot_df, x="dataset", y="duplicate_groups", hue="strictness", ax=ax)
    ax.set_title("Duplicate listing groups by strictness")
    ax.set_xlabel("Dataset")
    ax.set_ylabel("Duplicate group count")
    save_figure(fig, OUTPUT_DIR / "duplicate_listings_by_strictness.png")

    return counts_summary


def print_final_summary(
    geocode_summary: dict[str, dict[str, object]],
    vintage_summary: dict[str, object],
    mcrai_flags: dict[str, int],
    duplicate_counts: dict[str, dict[str, int]],
) -> None:
    section_header("FINAL SUMMARY")
    print("PASS 2 - Geocoding clusters:")
    for label in STRATA:
        row = geocode_summary[label]
        print(
            f"  {label}: {row['unique_coords']:,} unique coords / {row['total_rows']:,} rows; "
            f"largest cluster = {row['largest_cluster_size']:,} props at "
            f"({row['largest_cluster_lat']:.6f}, {row['largest_cluster_lon']:.6f})"
        )

    print("\nPASS 3 - Listing vintage:")
    if not vintage_summary["found"]:
        print("  Not found.")
    elif vintage_summary.get("plot_column") and vintage_summary.get("plot_ranges"):
        column = vintage_summary["plot_column"]
        ranges = vintage_summary["plot_ranges"]
        mins = [values[0] for values in ranges.values()]
        medians = [values[1] for values in ranges.values()]
        maxs = [values[2] for values in ranges.values()]
        print(
            f"  Found ({column}). date range = [{min(mins).date()}, {max(maxs).date()}], "
            f"median = {pd.Series(medians).sort_values().iloc[len(medians) // 2].date()}"
        )
    else:
        print("  Found in schema search, but not as a usable per-stratum plotted field.")

    print("\nPASS 4 - Per-LGU MCRAI parity:")
    for label in STRATA:
        print(f"  {label}: {mcrai_flags[label]:,} flagged (LGU x category) cells outside 3x band")

    print("\nPASS 5 - Duplicate listings:")
    for label in STRATA:
        row = duplicate_counts[label]
        print(f"  {label}: soft={row['soft']:,}, coord={row['coord']:,}, hard={row['hard']:,}")

    print("\nData integrity audit complete. Review printed flags before deciding on row drops, merges, or feature additions.")


def main() -> None:
    ensure_output_dir()
    configure_plotting()
    datasets = load_main_datasets()
    geocode_summary = pass2_geocoding_precision(datasets)
    vintage_summary = pass3_listing_vintage(datasets)
    mcrai_flags = pass4_mcrai_parity(datasets)
    duplicate_counts = pass5_duplicate_detection(datasets)
    print_final_summary(geocode_summary, vintage_summary, mcrai_flags, duplicate_counts)
    print_written_files()


if __name__ == "__main__":
    main()
