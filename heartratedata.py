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
