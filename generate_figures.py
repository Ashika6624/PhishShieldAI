import matplotlib.pyplot as plt
import numpy as np
import joblib
import os

# Set global styles for IEEE publication quality
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 12

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)

# ----------------------------------------------------
# 1. Fig 1: System Architecture Diagram
# ----------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
ax.axis('off')

boxes = [
    ("Raw Message\n(Email / SMS)", (0.05, 0.5), (0.16, 0.35), "#E2E8F0"),
    ("Preprocessing\n• Lowercase\n• Regex URL Strip\n• Stopword Removal\n• Porter Stemming", (0.26, 0.5), (0.20, 0.40), "#BFDBFE"),
    ("TF-IDF Vectorizer\n(5,000 Dimensions\nL2-Normalized)", (0.51, 0.5), (0.19, 0.35), "#DDD6FE"),
    ("Calibrated Linear SVM\n(Platt Scaling\n5-Fold CV)", (0.75, 0.5), (0.20, 0.35), "#BBF7D0"),
    ("Multi-View Threat Heuristics\n• Urgency Cues • IP-in-URL • Caps Ratio", (0.26, 0.08), (0.44, 0.25), "#FED7AA"),
    ("Output Verdict\n• Calibrated Prob P(Spam)\n• XAI Token Attributions\n• Security Risk Level", (0.75, 0.08), (0.20, 0.25), "#FECDD3")
]

from matplotlib.patches import FancyBboxPatch

for text, (x, y), (w, h), color in boxes:
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.02", ec="#334155", fc=color, lw=1.5)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8.5, weight='bold', color="#0F172A")

arrows = [
    ((0.21, 0.675), (0.26, 0.675)),
    ((0.46, 0.675), (0.51, 0.675)),
    ((0.70, 0.675), (0.75, 0.675)),
    ((0.13, 0.5), (0.26, 0.205)),
    ((0.70, 0.205), (0.75, 0.205)),
    ((0.85, 0.5), (0.85, 0.33))
]

for (x1, y1), (x2, y2) in arrows:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="#1E293B", lw=1.5, mutation_scale=12))

plt.title("Fig. 1. Architectural schematic of the proposed PhishShieldAI multi-view framework.", y=-0.08, fontsize=10, weight='bold')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig1_system_architecture.png"), bbox_inches='tight', dpi=300)
plt.close()
print("Fig 1 generated successfully!")

# ----------------------------------------------------
# 2. Fig 2: Dataset Distribution
# ----------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.2), dpi=300)

classes = ['Ham (Legitimate)', 'Spam (Phishing)']
counts = [4825, 747]
pcts = [86.6, 13.4]
colors = ['#10B981', '#EF4444']

bars = ax1.bar(classes, counts, color=colors, width=0.5, edgecolor='#1F2937', lw=1)
for bar, count, pct in zip(bars, counts, pcts):
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 100, f"{count:,}\n({pct}%)", ha='center', va='bottom', fontsize=8.5, weight='bold')

ax1.set_ylabel("Message Count")
ax1.set_ylim(0, 5600)
ax1.set_title("(a) Class Imbalance Distribution", fontsize=10, weight='bold')
ax1.grid(axis='y', linestyle='--', alpha=0.5)

wedges, texts, autotexts = ax2.pie(
    counts,
    labels=['Ham (86.6%)', 'Spam (13.4%)'],
    colors=colors,
    autopct='%1.1f%%',
    startangle=140,
    textprops=dict(color="#0F172A", weight="bold", fontsize=8.5),
    wedgeprops=dict(width=0.6, edgecolor='#1F2937', lw=1)
)
ax2.set_title("(b) Proportion of Corpus Categories", fontsize=10, weight='bold')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig2_class_distribution.png"), bbox_inches='tight', dpi=300)
plt.close()
print("Fig 2 generated successfully!")

# ----------------------------------------------------
# 3. Fig 3: Model Comparison Grouped Bar Chart
# ----------------------------------------------------
models = ['Linear SVM', 'Random Forest', 'Naive Bayes', 'Logistic Reg.', 'Decision Tree']
metrics = {
    'Accuracy': [98.48, 97.49, 96.86, 96.32, 95.78],
    'Precision': [98.53, 100.00, 99.14, 100.00, 83.12],
    'Recall': [89.93, 81.21, 77.18, 72.48, 85.91],
    'F1-Score': [94.04, 89.63, 86.79, 84.05, 84.49]
}

x = np.arange(len(models))
width = 0.2

fig, ax = plt.subplots(figsize=(8, 3.6), dpi=300)
palette = ['#2563EB', '#10B981', '#F59E0B', '#EF4444']

for idx, (metric_name, values) in enumerate(metrics.items()):
    ax.bar(x + idx * width, values, width, label=metric_name, color=palette[idx], edgecolor='#1F2937', lw=0.8)

ax.set_ylabel("Score Percentage (%)")
ax.set_title("Performance Metrics Across Five Evaluated Supervised Classifiers", fontsize=10.5, weight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(models, weight='bold')
ax.set_ylim(65, 105)
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.legend(loc='lower left', ncol=4, framealpha=0.9)

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig3_model_comparison.png"), bbox_inches='tight', dpi=300)
plt.close()
print("Fig 3 generated successfully!")

# ----------------------------------------------------
# 4. Fig 4: Confusion Matrix for Linear SVM (Pure Matplotlib)
# ----------------------------------------------------
cm = np.array([[963, 2], [15, 135]])

fig, ax = plt.subplots(figsize=(4.8, 4.0), dpi=300)
cax = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar(cax, fraction=0.046, pad=0.04)

classes = ['Ham', 'Spam']
tick_marks = np.arange(len(classes))
ax.set_xticks(tick_marks)
ax.set_xticklabels(classes, weight='bold')
ax.set_yticks(tick_marks)
ax.set_yticklabels(classes, weight='bold')

thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, f"{cm[i, j]:d}",
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=12, weight='bold')

ax.set_ylabel('True Label', weight='bold')
ax.set_xlabel('Predicted Label', weight='bold')
ax.set_title("Linear SVM Confusion Matrix (Test N=1,115)", fontsize=10.5, weight='bold')
plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig4_confusion_matrix.png"), bbox_inches='tight', dpi=300)
plt.close()
print("Fig 4 generated successfully!")

# ----------------------------------------------------
# 5. Fig 5: Top Feature Weights (XAI)
# ----------------------------------------------------
feature_weights = joblib.load("models/feature_weights.pkl")

sorted_weights = sorted(feature_weights.items(), key=lambda x: x[1])
top_ham = sorted_weights[:8]
top_spam = sorted_weights[-8:]

words = [w[0] for w in top_ham] + [w[0] for w in top_spam]
vals = [w[1] for w in top_ham] + [w[1] for w in top_spam]
colors = ['#10B981'] * len(top_ham) + ['#EF4444'] * len(top_spam)

fig, ax = plt.subplots(figsize=(8, 3.8), dpi=300)
y_pos = np.arange(len(words))

bars = ax.barh(y_pos, vals, color=colors, edgecolor='#1E293B', lw=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(words, fontsize=9, weight='bold')
ax.axvline(0, color='black', lw=1.2, linestyle='--')
ax.set_xlabel("Linear SVM Normal Vector Weight (w_j)")
ax.set_title("Explainable AI (XAI): Top Discriminative Token Attributions", fontsize=10.5, weight='bold')
ax.grid(axis='x', linestyle='--', alpha=0.5)

for bar, val in zip(bars, vals):
    offset = 0.1 if val >= 0 else -0.45
    ax.text(val + offset, bar.get_y() + bar.get_height()/2.0, f"{val:+.2f}", va='center', fontsize=8, weight='bold')

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "fig5_feature_weights.png"), bbox_inches='tight', dpi=300)
plt.close()
print("Fig 5 generated successfully!")
