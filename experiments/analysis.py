import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path("experiments")

df_normal = pd.read_csv(BASE_DIR / "experiments_normal_all.csv")
df_incorrect = pd.read_csv(BASE_DIR / "experiments_incorrect_all.csv")

df_inj = df_incorrect[df_incorrect["is_injection_point"]].copy()
TOTAL_INJECTIONS = len(df_inj)

df_detected = df_inj[df_inj["detected_error"] != "None"].copy()

print("\nВНЕСЕННЫЕ ОШИБКИ")
injected_stats = df_inj["injected_error"].value_counts()

injected_df = pd.DataFrame({
    "count": injected_stats,
    "percent": (injected_stats / TOTAL_INJECTIONS * 100).round(2)
}).sort_values("count", ascending=False)

print(injected_df)

print("\nВСЕ НАЙДЕННЫЕ ОШИБКИ")
detected_stats = df_detected["detected_error"].value_counts()

detected_df = pd.DataFrame({
    "count": detected_stats,
    "percent": (detected_stats / TOTAL_INJECTIONS * 100).round(2)
}).sort_values("count", ascending=False)

print(detected_df)

print("\nКОЛИЧЕСТВО НАЙДЕННЫХ ОШИБОК ПО БИБЛИОТЕКАМ")
detected_by_library = df_detected.groupby("library").size()

detected_lib_df = pd.DataFrame({
    "count": detected_by_library,
    "percent": (
        detected_by_library
        / df_inj.groupby("library").size()
        * 100
    ).round(2)
}).sort_values("count", ascending=False)

print(detected_lib_df)

print("\nТАБЛИЦА НАЙДЕННЫХ ОШИБОК (БИБЛИОТЕКА × КЛАСС ОШИБКИ)")
detected_table = (
    df_detected
    .groupby(["library", "detected_error"])
    .size()
    .unstack(fill_value=0)
)
print(detected_table)

summary = pd.DataFrame({
    "injected": df_inj.groupby("library").size(),
    "detected": df_detected.groupby("library").size()
}).fillna(0).astype(int)

summary["detected_percent"] = (
    summary["detected"] / summary["injected"] * 100
).round(2)

print("\nОБЩАЯ СТАТИСТИКА (ВНЕСЕННЫЕ vs НАЙДЕННЫЕ)")
print(summary)

time_stats = (
    pd.concat([df_normal, df_incorrect])
    .groupby("library")["time_sec"]
    .agg(["mean", "std", "min", "max"])
    .round(6)
)

print("\nВРЕМЯ ВЫПОЛНЕНИЯ ПО БИБЛИОТЕКАМ (сек)")
print(time_stats)

sns.set(style="whitegrid")

plt.figure(figsize=(8, 5))
sns.barplot(
    x=injected_df.index,
    y=injected_df["percent"]
)
plt.title("Распределение внесенных ошибок")
plt.ylabel("Процент, %")
plt.xlabel("Класс ошибки")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(BASE_DIR / "injected_errors_distribution.png")
plt.close()

plt.figure(figsize=(8, 5))
sns.barplot(
    x=detected_df.index,
    y=detected_df["percent"]
)
plt.title("Распределение найденных ошибок")
plt.ylabel("Процент, %")
plt.xlabel("Класс ошибки")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(BASE_DIR / "detected_errors_distribution.png")
plt.close()

plt.figure(figsize=(8, 5))
sns.barplot(
    data=detected_lib_df.reset_index(),
    x="library",
    y="percent"
)
plt.title("Процент найденных ошибок по библиотекам")
plt.ylabel("Процент, %")
plt.xlabel("Библиотека")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(BASE_DIR / "detected_errors_by_library.png")
plt.close()

plt.figure(figsize=(10, 6))
sns.heatmap(
    detected_table,
    annot=True,
    fmt="d",
    cmap="Blues"
)
plt.title("Найденные ошибки (Библиотека × Класс ошибки)")
plt.ylabel("Библиотека")
plt.xlabel("Класс ошибки")
plt.tight_layout()
plt.savefig(BASE_DIR / "detected_errors_heatmap.png")
plt.close()

summary_plot = summary.reset_index().melt(
    id_vars="library",
    value_vars=["injected", "detected"],
    var_name="type",
    value_name="count"
)

plt.figure(figsize=(8, 5))
sns.barplot(
    data=summary_plot,
    x="library",
    y="count",
    hue="type"
)
plt.title("Внесенные vs найденные ошибки по библиотекам")
plt.ylabel("Количество")
plt.xlabel("Библиотека")
plt.tight_layout()
plt.savefig(BASE_DIR / "injected_vs_detected_by_library.png")
plt.close()

plt.figure(figsize=(8, 5))
sns.barplot(
    data=summary.reset_index(),
    x="library",
    y="detected_percent"
)
plt.title("Доля найденных ошибок по библиотекам")
plt.ylabel("Процент, %")
plt.xlabel("Библиотека")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(BASE_DIR / "detected_percent_by_library.png")
plt.close()

plt.figure(figsize=(8, 5))
sns.barplot(
    data=time_stats.reset_index(),
    x="library",
    y="mean",
    errorbar="sd"
)
plt.title("Среднее время выполнения (+- std)")
plt.ylabel("Время, сек")
plt.xlabel("Библиотека")
plt.tight_layout()
plt.savefig(BASE_DIR / "time_by_library.png")
plt.close()

print("\nАНАЛИЗ ЗАВЕРШЕН")
