from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path("experiments")
NORMAL_CSV = BASE_DIR / "experiments_normal.csv"
INCORRECT_CSV = BASE_DIR / "experiments_incorrect.csv"

BASE_DIR.mkdir(exist_ok=True)

# Загрузка данных
df_normal = pd.read_csv(NORMAL_CSV)
df_incorrect = pd.read_csv(INCORRECT_CSV)

df = pd.concat([df_normal, df_incorrect], ignore_index=True)

# Базовые метрики
df["total"] = df["passed"] + df["failed"]
df["pass_rate"] = df["passed"] / df["total"]

# Агрегация (mean / std)
agg = (
    df.groupby(["dataset", "library", "function"])
    .agg(
        pass_rate_mean=("pass_rate", "mean"),
        pass_rate_std=("pass_rate", "std"),
        failed_mean=("failed", "mean"),
        failed_std=("failed", "std"),
        time_mean=("time_sec", "mean"),
        time_std=("time_sec", "std"),
        time_min=("time_sec", "min"),
        time_max=("time_sec", "max"),
        runs=("run_id", "count"),
    )
    .reset_index()
)

# Сводка по библиотекам

print("\nСРЕДНИЙ PASS-RATE ПО БИБЛИОТЕКАМ\n")
print(
    agg.groupby(["dataset", "library"])["pass_rate_mean"]
    .mean()
    .unstack()
    .round(3)
)

pivot = agg.pivot_table(
    index=["library", "function"],
    columns="dataset",
    values="pass_rate_mean"
).reset_index()

pivot["degradation"] = pivot["normal"] - pivot["incorrect"]

pivot_std = agg.pivot_table(
    index=["library", "function"],
    columns="dataset",
    values="pass_rate_std"
).reset_index()

pivot["degradation_std"] = (
    (pivot_std["normal"] ** 2 + pivot_std["incorrect"] ** 2) ** 0.5
)

print("\nСРЕДНЯЯ ДЕГРАДАЦИЯ КАЧЕСТВА\n")
print(
    pivot.groupby("library")["degradation"]
    .mean()
    .sort_values(ascending=False)
    .round(3)
)

print("\nSTD PASS-RATE ПО БИБЛИОТЕКАМ\n")
print(
    agg.groupby(["dataset", "library"])["pass_rate_std"]
    .mean()
    .unstack()
    .round(4)
)

print("\nSTD ДЕГРАДАЦИИ ПО БИБЛИОТЕКАМ\n")
print(
    pivot.groupby("library")["degradation_std"]
    .mean()
    .sort_values(ascending=False)
    .round(4)
)

print("\nSTD ДЕГРАДАЦИИ ПО ФУНКЦИЯМ\n")
print(
    pivot.groupby("function")["degradation_std"]
    .mean()
    .sort_values(ascending=False)
    .round(4)
)

print("\nСАМЫЕ ХРУПКИЕ ФУНКЦИИ\n")
print(
    pivot.groupby("function")["degradation"]
    .mean()
    .sort_values(ascending=False)
    .round(3)
)

print("\nВРЕМЯ ВЫПОЛНЕНИЯ ПО БИБЛИОТЕКАМ (сек)\n")
time_stats = (
    agg.groupby("library")
    .agg(
        mean_time=("time_mean", "mean"),
        std_time=("time_mean", "std"),
        min_time=("time_min", "min"),
        max_time=("time_max", "max"),
    )
    .round(4)
)

print(time_stats)


# Построение графиков
sns.set(style="whitegrid")

# 1. Pass-rate по библиотекам
plt.figure(figsize=(8, 5))
sns.barplot(
    data=agg,
    x="library",
    y="pass_rate_mean",
    hue="dataset"
)
plt.title("Средний pass-rate по библиотекам")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig(BASE_DIR / "passrate_by_library.png")
plt.close()

# 2. Pass-rate по функциям
plt.figure(figsize=(10, 5))
sns.barplot(
    data=agg,
    x="function",
    y="pass_rate_mean",
    hue="dataset"
)
plt.xticks(rotation=30)
plt.title("Средний pass-rate по функциям")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig(BASE_DIR / "passrate_by_function.png")
plt.close()

# 3. Heatmap деградации
heatmap_data = pivot.pivot(
    index="function",
    columns="library",
    values="degradation"
)

plt.figure(figsize=(8, 6))
sns.heatmap(
    heatmap_data,
    annot=True,
    cmap="Reds",
    fmt=".2f"
)
plt.title("Деградация качества (normal -> incorrect)")
plt.tight_layout()
plt.savefig(BASE_DIR / "degradation_heatmap.png")
plt.close()

# 4. Время выполнения (mean +- std)
plt.figure(figsize=(8, 5))
sns.barplot(
    data=agg,
    x="library",
    y="time_mean",
    errorbar="sd"
)
plt.title("Среднее время выполнения (+- std)")
plt.ylabel("Время, с")
plt.tight_layout()
plt.savefig(BASE_DIR / "time_by_library.png")
plt.close()

# 5. Стандартное отклонение деградации
plt.figure(figsize=(8, 5))
sns.barplot(
    data=pivot,
    x="library",
    y="degradation_std"
)
plt.title("Стандартное отклонение деградации качества")
plt.ylabel("STD деградации")
plt.tight_layout()
plt.savefig(BASE_DIR / "degradation_std_by_library.png")
plt.close()

print("\nГрафики и статистика сохранены в папке experiments/")

