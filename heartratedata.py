if missing_columns:
        raise ValueError(
            "CSV is missing required column(s): " + ", ".join(sorted(missing_columns))
        )

    data["heart_rate_bpm"] = pd.to_numeric(
        data["heart_rate_bpm"], errors="coerce"
    )

    if data["heart_rate_bpm"].isna().any():
        bad_rows = int(data["heart_rate_bpm"].isna().sum())
        raise ValueError(
            f"{bad_rows} heart-rate value(s) are blank or non-numeric. "
            "Correct them in heart_rate_data.csv and run the program again."
        )

    if (data["heart_rate_bpm"] <= 0).any():
        raise ValueError("Heart-rate values must be greater than zero.")

    if data.empty:
        raise ValueError("The CSV file has no data rows.")

    data["timestamp"] = pd.to_datetime(
        data["date"].astype(str) + " " + data["time"].astype(str),
        errors="coerce",
    )

    if data["timestamp"].isna().any():
        raise ValueError("Some date/time values could not be understood. Check the CSV.")

    return data.sort_values("timestamp").reset_index(drop=True)


def print_summary(data: pd.DataFrame) -> None:
    """Print overall and activity-wise statistics."""
    heart_rate = data["heart_rate_bpm"]

    print("\nHEART RATE DATA VISUALIZER")
    print("=" * 30)
    print(f"Number of readings : {len(data)}")
    print(f"Average heart rate : {heart_rate.mean():.1f} BPM")
    print(f"Minimum heart rate : {heart_rate.min():.0f} BPM")
    print(f"Maximum heart rate : {heart_rate.max():.0f} BPM")

    print("\nAverage heart rate by activity:")
    activity_summary = (
        data.groupby("activity")["heart_rate_bpm"]
        .agg(["count", "mean", "min", "max"])
        .sort_values("mean")
    )
    activity_summary = activity_summary.rename(
        columns={
            "count": "Readings",
            "mean": "Average BPM",
            "min": "Minimum BPM",
            "max": "Maximum BPM",
        }
    )
    print(activity_summary.round(1).to_string())


def create_charts(data: pd.DataFrame) -> None:
    """Create and save the time-series and activity-average charts."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Chart 1: individual readings over time
    plt.figure(figsize=(10, 5))
    plt.plot(
        data["timestamp"],
        data["heart_rate_bpm"],
        marker="o",
        linewidth=1.5,
    )
    plt.title("Heart Rate Over Time")
    plt.xlabel("Date and time")
    plt.ylabel("Heart rate (BPM)")
    plt.xticks(rotation=35, ha="right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "heart_rate_over_time.png", dpi=150)
    plt.close()

    # Chart 2: average reading for each activity
    activity_average = (
        data.groupby("activity")["heart_rate_bpm"]
        .mean()
        .sort_values()
    )

    plt.figure(figsize=(8, 5))
    plt.bar(activity_average.index, activity_average.values)
    plt.title("Average Heart Rate by Activity")
    plt.xlabel("Activity")
    plt.ylabel("Average heart rate (BPM)")
    plt.xticks(rotation=25, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "average_by_activity.png", dpi=150)
    plt.close()

    print(f"\nCharts saved in: {OUTPUT_DIR}")
    print("- heart_rate_over_time.png")
    print("- average_by_activity.png")


def main() -> int:
    try:
        data = load_data(DATA_FILE)
        print_summary(data)
        create_charts(data)
        print("\nDone! These charts are for educational data analysis only.")
        return 0
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
