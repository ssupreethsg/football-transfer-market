import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set textbook styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['axes.edgecolor'] = '#2D3748'

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

# ----------------- PANEL 1: PHYSICAL MINUTES BOUNDS & INVARIANT PARTITIONING -----------------
competitions = ['Domestic League\n(38 matches)', 'UEFA Champions League\n(13 matches)', 'Domestic Cups\n(6 matches)', 'International / NT\n(8 matches)']
theoretical_max = [3420, 1170, 540, 720]
erling_haaland_minutes = [2650, 810, 270, 450]
lamine_yamal_minutes = [2480, 790, 310, 540]

x = np.arange(len(competitions))
width = 0.25

rects0 = ax1.bar(x - width, theoretical_max, width, label='Theoretical Max Ceiling ($M_{c,\\max}$)', color='#E2E8F0', edgecolor='#718096', linestyle='--', linewidth=1.5)
rects1 = ax1.bar(x, erling_haaland_minutes, width, label='Erling Haaland (2024/25)', color='#3182CE', edgecolor='#2B6CB0')
rects2 = ax1.bar(x + width, lamine_yamal_minutes, width, label='Lamine Yamal (2024/25)', color='#ED8936', edgecolor='#DD6B20')

ax1.set_ylabel('Playing Minutes ($M_{i,s,c}$)', fontsize=11, fontweight='bold', color='#1A202C')
ax1.set_title(r'Competition Minutes Conservation & Physical Ceilings' + '\n' + r'$\sum_{c} M_{i,s,c} = M_{i,s}^{\mathrm{total}} \leq 5,850\,\mathrm{min}$', fontsize=12, fontweight='bold', color='#1A202C', pad=12)
ax1.set_xticks(x)
ax1.set_xticklabels(competitions, fontsize=9.5)
ax1.legend(frameon=True, facecolor='#F7FAFC', edgecolor='#CBD5E0', fontsize=9)
ax1.grid(axis='y', linestyle=':', alpha=0.6)
ax1.set_ylim(0, 4000)

# Annotate ceiling bounds
for i, m in enumerate(theoretical_max):
    ax1.text(i - width, m + 70, f'{m}m', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#4A5568')

# ----------------- PANEL 2: CAREER VS MULTI-SEASON HIERARCHICAL MODEL -----------------
seasons = ['2023/24 Season', '2024/25 Season', '2025/26 (Current)', 'Prior Career']
goals_breakdown = [38, 41, 14, 163]  # Example Haaland career ~256 goals
assists_breakdown = [6, 8, 4, 45]

bar_width = 0.5
bottom_goals = 0

colors_goals = ['#63B3ED', '#3182CE', '#2B6CB0', '#1A365D']
colors_assists = ['#FBD38D', '#F6AD55', '#DD6B20', '#7B341E']

y_pos = np.arange(2)
# Stacked horizontal bar for Haaland
categories = ['Career Goals\n(Total: 256)', 'Career Assists\n(Total: 63)']

# Plotting horizontal stacked
left_g = 0
left_a = 0
labels = ['2023/24', '2024/25', '2025/26 (Live)', 'Prior Seasons']
colors = ['#38A169', '#3182CE', '#805AD5', '#718096']

for i in range(len(seasons)):
    ax2.barh(categories[0], goals_breakdown[i], left=left_g, color=colors[i], edgecolor='white', height=0.45, label=labels[i] if i == 0 or True else "")
    ax2.text(left_g + goals_breakdown[i]/2, 0, f"{goals_breakdown[i]}", ha='center', va='center', color='white', fontweight='bold', fontsize=9)
    left_g += goals_breakdown[i]

    ax2.barh(categories[1], assists_breakdown[i], left=left_a, color=colors[i], edgecolor='white', height=0.45)
    ax2.text(left_a + assists_breakdown[i]/2, 1, f"{assists_breakdown[i]}", ha='center', va='center', color='white', fontweight='bold', fontsize=9)
    left_a += assists_breakdown[i]

ax2.set_xlabel('Total Count', fontsize=11, fontweight='bold', color='#1A202C')
ax2.set_title('Hierarchical Consistency: Career Aggregate = $\\sum$ Seasons\n$\\mathcal{T}_{\\mathrm{career}} = \\sum_{s \\in \\mathcal{S}} \\mathcal{T}_{s} + \\mathcal{T}_{\\mathrm{prior}}$', fontsize=12, fontweight='bold', color='#1A202C', pad=12)
ax2.legend(loc='lower right', frameon=True, facecolor='#F7FAFC', edgecolor='#CBD5E0', fontsize=9)
ax2.grid(axis='x', linestyle=':', alpha=0.6)
ax2.set_xlim(0, 280)

plt.tight_layout()
output_path = r'C:\Users\Supreeth\.gemini\antigravity\brain\8946ac6e-4ceb-4892-9cb7-43e8850f995d\textbook_career_and_competition_consistency.png'
plt.savefig(output_path, dpi=300)
print(f"Successfully generated textbook diagram at {output_path}")
