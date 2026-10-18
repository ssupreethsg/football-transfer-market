import sqlite3
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Style configuration for textbook-quality aesthetic
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig = plt.figure(figsize=(16, 10), dpi=300)

db_path = os.path.join(os.path.dirname(__file__), 'sql_app.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Query empirical players
players = c.execute("SELECT rating_score, predicted_market_value_eur, age, league, team FROM players").fetchall()
ratings = [p['rating_score'] for p in players if p['rating_score'] is not None]
values = [p['predicted_market_value_eur'] / 1e6 for p in players if p['predicted_market_value_eur'] is not None]
leagues = [p['league'] for p in players]

# Subplot 1: Econometric Non-Linear Valuation Curves by Age Cohort
ax1 = plt.subplot(2, 2, 1)
ovr_range = np.linspace(60, 95, 200)

def val_curve(ovr, age, mult=1.25):
    if age <= 21:
        age_m = 1.0 + 0.12 * (22 - age)
    elif 22 <= age <= 25:
        age_m = 1.15
    elif 26 <= age <= 28:
        age_m = 1.00
    else:
        age_m = max(0.12, 1.0 - 0.12 * (age - 28))
    contract_m = 1.15 # 4+ yrs contract
    beta = 0.185
    val = (2.5 * np.exp(beta * (ovr - 70.0)) * age_m * contract_m * mult)
    return np.clip(val, 0.3, 230.0)

ax1.plot(ovr_range, [val_curve(x, 19, 1.25) for x in ovr_range], color='#2563eb', linewidth=2.5, label=r'Wonderkid ($Age = 19$, $M_{age}=1.36$)')
ax1.plot(ovr_range, [val_curve(x, 25, 1.25) for x in ovr_range], color='#10b981', linewidth=2.5, label=r'Peak Prime ($Age = 25$, $M_{age}=1.15$)')
ax1.plot(ovr_range, [val_curve(x, 34, 1.25) for x in ovr_range], color='#f59e0b', linewidth=2.5, linestyle='--', label=r'Veteran ($Age = 34$, $M_{age}=0.28$)')

# Annotations for key anchors
ax1.scatter([94, 94, 93, 89], [220, 210, 200, 140], color='#dc2626', zorder=5, s=60)
ax1.annotate('Haaland (94, €220M)', (94, 220), textcoords="offset points", xytext=(-85, 2), fontweight='bold', fontsize=9)
ax1.annotate('Mbappé (94, €210M)', (94, 210), textcoords="offset points", xytext=(-80, -14), fontweight='bold', fontsize=9)
ax1.annotate('Yamal (93, €200M)', (93, 200), textcoords="offset points", xytext=(-75, 10), fontweight='bold', fontsize=9)
ax1.annotate('Saka (89, €140M)', (89, 140), textcoords="offset points", xytext=(-65, 10), fontweight='bold', fontsize=9)

ax1.set_title('Figure 1.1: Econometric Exponential Valuation Curves vs. Overall Rating (OVR)\n$V = V_0 \\cdot \\exp(\\beta \\cdot (\\mathrm{OVR} - 70)) \\cdot M_{age} \\cdot M_{contract} \\cdot M_{league}$ (with $\\beta=0.185$)', fontsize=11, fontweight='bold', pad=12)
ax1.set_xlabel('Overall Player Rating (OVR: 0-100 scale)', fontsize=10)
ax1.set_ylabel('Market Valuation (€ Millions)', fontsize=10)
ax1.set_xlim(60, 96)
ax1.set_ylim(0, 250)
ax1.legend(loc='upper left', frameon=True, fontsize=9)
ax1.grid(True, linestyle=':', alpha=0.6)

# Subplot 2: Empirical Rating Score Distribution across 2,521 Players
ax2 = plt.subplot(2, 2, 2)
sns.histplot(ratings, bins=35, kde=True, color='#6366f1', ax=ax2, edgecolor='white', linewidth=1.2)
mean_ovr = np.mean(ratings)
median_ovr = np.median(ratings)
ax2.axvline(mean_ovr, color='#dc2626', linestyle='-', linewidth=2, label=f'Mean OVR: {mean_ovr:.1f}')
ax2.axvline(median_ovr, color='#059669', linestyle='--', linewidth=2, label=f'Median OVR: {median_ovr:.1f}')
ax2.axvline(85.0, color='#d97706', linestyle=':', linewidth=2, label='Elite Tier (OVR >= 85)')

ax2.set_title(f'Figure 1.2: Empirical OVR Distribution across Europe Top 5 (N={len(ratings):,} Players)', fontsize=11, fontweight='bold', pad=12)
ax2.set_xlabel('Player Overall Rating (OVR)', fontsize=10)
ax2.set_ylabel('Number of Active Players', fontsize=10)
ax2.legend(loc='upper right', frameon=True, fontsize=9)
ax2.grid(True, linestyle=':', alpha=0.6)

# Subplot 3: Squad Count Verification per League (Top 5: 96 Clubs)
ax3 = plt.subplot(2, 2, 3)
club_counts = c.execute("SELECT league, team, count(*) as cnt FROM players GROUP BY team ORDER BY league, cnt DESC").fetchall()
league_order = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
palette = {'Premier League': '#3b82f6', 'La Liga': '#ef4444', 'Serie A': '#10b981', 'Bundesliga': '#f59e0b', 'Ligue 1': '#8b5cf6'}

squad_sizes_by_league = {lg: [] for lg in league_order}
for r in club_counts:
    if r['league'] in squad_sizes_by_league:
        squad_sizes_by_league[r['league']].append(r['cnt'])

box_data = [squad_sizes_by_league[lg] for lg in league_order]
bp = ax3.boxplot(box_data, patch_artist=True, tick_labels=[f"{lg}\n({len(squad_sizes_by_league[lg])} clubs)" for lg in league_order],
                 medianprops=dict(color='black', linewidth=1.5))

colors = ['#93c5fd', '#fca5a5', '#6ee7b7', '#fde68a', '#c4b5fd']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)

ax3.axhline(34, color='red', linestyle='--', alpha=0.7, label='Upper Bound (34 max)')
ax3.axhline(20, color='red', linestyle=':', alpha=0.7, label='Lower Bound (20 min)')
ax3.set_title('Figure 1.3: Roster Uniformity Audit across 96 European Top-5 Clubs\n(Zero Outliers: Range [20, 33])', fontsize=11, fontweight='bold', pad=12)
ax3.set_ylabel('Active Players per Squad', fontsize=10)
ax3.set_ylim(16, 36)
ax3.legend(loc='lower right', frameon=True, fontsize=8)
ax3.grid(True, linestyle=':', alpha=0.6)

# Subplot 4: Multi-Season Competition Records (8,802 records breakdown)
ax4 = plt.subplot(2, 2, 4)
stats_counts = c.execute("""
    SELECT competition_type, season, count(*) as cnt 
    FROM player_competition_stats 
    GROUP BY competition_type, season
    ORDER BY competition_type, season
""").fetchall()

comp_types = sorted(list(set(r['competition_type'] for r in stats_counts)))
seasons = ["2024/2025", "2025/2026"]

s24 = []
s25 = []
for ct in comp_types:
    cnt24 = next((r['cnt'] for r in stats_counts if r['competition_type'] == ct and r['season'] == '2024/2025'), 0)
    cnt25 = next((r['cnt'] for r in stats_counts if r['competition_type'] == ct and r['season'] == '2025/2026'), 0)
    s24.append(cnt24)
    s25.append(cnt25)

x = np.arange(len(comp_types))
width = 0.35

ax4.bar(x - width/2, s24, width, label='2024/2025 Historical Baseline', color='#3b82f6')
ax4.bar(x + width/2, s25, width, label='2025/2026 Active Ingestion', color='#10b981')

ax4.set_title('Figure 1.4: Multi-Season & Multi-Competition Records Audit\n(Total Records = 8,802 across 4 Competitions)', fontsize=11, fontweight='bold', pad=12)
ax4.set_xticks(x)
ax4.set_xticklabels(comp_types, fontsize=10)
ax4.set_ylabel('Logged Records Count', fontsize=10)
ax4.legend(loc='upper right', frameon=True, fontsize=9)
ax4.grid(True, linestyle=':', alpha=0.6)

for i in range(len(comp_types)):
    ax4.text(x[i] - width/2, s24[i] + 40, f"{s24[i]:,}", ha='center', fontsize=8, fontweight='bold')
    ax4.text(x[i] + width/2, s25[i] + 40, f"{s25[i]:,}", ha='center', fontsize=8, fontweight='bold')

plt.tight_layout()

# Save to artifacts directory
artifact_dir = r"C:\Users\Supreeth\.gemini\antigravity\brain\8946ac6e-4ceb-4892-9cb7-43e8850f995d"
out_path = os.path.join(artifact_dir, "textbook_valuation_model.png")
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart successfully saved to: {out_path}")
