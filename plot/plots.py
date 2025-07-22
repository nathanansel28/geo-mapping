import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date


def plot_counts(df):
    # Drop rows with invalid datetime
    df = df.copy(deep=True).dropna(subset=['datetime'])

    # Preprocessing
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour

    # Set Seaborn style and palette
    sns.set_style("whitegrid", {'axes.grid': False})
    colors = sns.color_palette("Set2", 2)

    # === Plot by DATE ===
    daily_counts = df.groupby(['date', 'type']).size().unstack(fill_value=0)
    daily_counts = daily_counts[daily_counts.index >= date(2025, 1, 1)]

    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    daily_counts.plot(ax=ax, linewidth=2.2, marker='o', color=colors)

    ax.set_title("Photos and Videos Over Time", fontsize=16, weight='normal')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.legend(["Photos", "Videos"], fontsize=11)
    ax.grid(False)

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.tight_layout()
    plt.show()

    # === Plot by HOUR of Day ===
    hourly_counts = df.groupby(['hour', 'type']).size().unstack(fill_value=0)
    plt.figure(figsize=(10, 5))
    ax2 = plt.gca()

    hourly_counts.plot(ax=ax2, linewidth=2.2, marker='o', color=colors)

    ax2.set_title("Photos and Videos by Hour of Day", fontsize=16, weight='normal')
    ax2.set_xlabel("Hour of Day", fontsize=12)
    ax2.set_ylabel("Count", fontsize=12)
    ax2.set_xticks(range(0, 24))
    ax2.legend(["Photos", "Videos"], fontsize=11)
    ax2.grid(False)

    plt.tight_layout()
    plt.show()
