import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Color palette
    c_start = '#27ae60'       # Green
    c_end = '#e74c3c'         # Red
    c_client = '#fef9e7'      # Light yellow/gold
    c_client_edge = '#f39c12'
    c_gateway = '#e8f8f5'     # Soft teal
    c_gateway_edge = '#1abc9c'
    c_regex = '#ebf5fb'       # Soft blue
    c_regex_edge = '#3498db'
    c_decision = '#fcf3cf'    # Soft yellow
    c_decision_edge = '#f1c40f'
    c_ml = '#f4ecf7'          # Soft purple
    c_ml_edge = '#9b59b6'
    c_dl = '#fadbd8'          # Soft red/pink
    c_dl_edge = '#e74c3c'
    c_db = '#eaeded'          # Soft gray
    c_db_edge = '#7f8c8d'
    c_target = '#eaf2f8'      # Ice blue
    c_target_edge = '#2980b9'
    c_soc = '#d4efdf'         # Soft mint green
    c_soc_edge = '#27ae60'

    # Helper function for drawing rounded boxes
    def draw_box(x, y, w, h, text, facecolor, edgecolor, fontsize=9.5, bold=True, subtext=None):
        box = patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.12,rounding_size=0.15",
            facecolor=facecolor, edgecolor=edgecolor, linewidth=1.8, zorder=2
        )
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.15, text, ha='center', va='center', fontsize=fontsize, fontweight='bold' if bold else 'normal', color='#2c3e50', zorder=3)
            ax.text(x, y - 0.2, subtext, ha='center', va='center', fontsize=fontsize - 2, color='#566573', zorder=3)
        else:
            ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, fontweight='bold' if bold else 'normal', color='#2c3e50', zorder=3)

    # Helper function for drawing diamonds (decisions)
    def draw_diamond(x, y, r, text, facecolor, edgecolor, fontsize=9):
        pts = [[x, y + r], [x + r*1.2, y], [x, y - r], [x - r*1.2, y]]
        poly = patches.Polygon(pts, closed=True, facecolor=facecolor, edgecolor=edgecolor, linewidth=1.8, zorder=2)
        ax.add_patch(poly)
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, fontweight='bold', color='#2c3e50', zorder=3)

    # Helper function for drawing arrows
    def draw_arrow(x1, y1, x2, y2, label=None, label_pos=(0.5, 0.5), label_offset=(0, 0.15), style='->', color='#34495e', lw=1.5, ls='-'):
        ax.annotate(
            '', xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle=style, color=color, lw=lw, linestyle=ls, shrinkA=3, shrinkB=3),
            zorder=1
        )
        if label:
            lx = x1 + (x2 - x1) * label_pos[0] + label_offset[0]
            ly = y1 + (y2 - y1) * label_pos[1] + label_offset[1]
            ax.text(lx, ly, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2980b9',
                    bbox=dict(boxstyle='square,pad=0.15', facecolor='#ffffff', edgecolor='none', alpha=0.85), zorder=4)

    # 1. Start node (circle)
    start_circle = patches.Circle((0.8, 6.8), 0.45, facecolor='#2ecc71', edgecolor='#27ae60', lw=2, zorder=2)
    ax.add_patch(start_circle)
    ax.text(0.8, 6.8, 'Start', ha='center', va='center', fontsize=10, fontweight='bold', color='#ffffff', zorder=3)

    # 2. Client HTTP Request
    draw_box(2.6, 6.8, 1.8, 0.9, 'Client\nRequest', c_client, c_client_edge, subtext='HTTP GET/POST')
    draw_arrow(1.25, 6.8, 1.7, 6.8)

    # 3. FastAPI Gateway / Reverse Proxy
    draw_box(5.0, 6.8, 2.0, 1.0, 'FastAPI Gateway', c_gateway, c_gateway_edge, subtext='Reverse Proxy / Ingest')
    draw_arrow(3.5, 6.8, 4.0, 6.8, label='Sends')

    # 4. Request Validation & Normalization
    draw_box(5.0, 5.0, 2.0, 0.85, 'Request Validation', c_gateway, c_gateway_edge, subtext='URL & Hex Decode')
    draw_arrow(5.0, 6.3, 5.0, 5.42, label='Forwards')

    # 5. Regex / Signature Fast-Path
    draw_box(5.0, 3.4, 2.0, 0.9, 'Signature Triage', c_regex, c_regex_edge, subtext='Known CVE / RegEx')
    draw_arrow(5.0, 4.58, 5.0, 3.85, label='Validates')

    # 6. Diamond: Known Attack?
    draw_diamond(7.5, 3.4, 0.65, 'Signature\nHit?', c_decision, c_decision_edge, fontsize=8.5)
    draw_arrow(6.0, 3.4, 6.7, 3.4, label='Checks')

    # Branch: If Hit -> Immediate Block
    draw_box(7.5, 1.5, 1.8, 0.8, 'Immediate Drop', c_end, '#c0392b', subtext='HTTP 403 Forbidden')
    draw_arrow(7.5, 2.75, 7.5, 1.9, label='Yes (Hit)', color='#c0392b')

    # Branch: If No -> Feature Extraction
    draw_box(10.0, 3.4, 2.0, 0.9, 'Feature Extractor', c_regex, c_regex_edge, subtext='42 Lexical/Entropy')
    draw_arrow(8.3, 3.4, 9.0, 3.4, label='No (Clean)', color='#27ae60')

    # 7. Fast ML Classifier Tier
    draw_box(10.0, 5.0, 2.0, 0.9, 'Fast ML Tier', c_ml, c_ml_edge, subtext='Random Forest/XGB')
    draw_arrow(10.0, 3.85, 10.0, 4.55, label='Extracts')

    # 8. Diamond: Risk Score Threshold
    draw_diamond(12.5, 5.0, 0.7, 'Risk Score\nTriage', c_decision, c_decision_edge, fontsize=8.5)
    draw_arrow(11.0, 5.0, 11.65, 5.0, label='Infers')

    # Three Branches from ML Decision:
    # A) High Risk (> 0.65) -> Drop / Block
    draw_box(12.5, 1.5, 1.8, 0.8, 'Block Request', c_end, '#c0392b', subtext='HTTP 403 Block')
    draw_arrow(12.5, 4.3, 12.5, 1.9, label='Risk > 0.65', color='#c0392b', label_offset=(0.6, 0))

    # B) Ambiguous (0.35 - 0.65) -> Deep Learning Inspection
    draw_box(12.5, 6.8, 2.0, 0.9, 'Deep Learning Tier', c_dl, c_dl_edge, subtext='Bi-LSTM Sequence')
    draw_arrow(12.5, 5.7, 12.5, 6.35, label='0.35 ≤ Risk ≤ 0.65', color='#e67e22', label_offset=(-0.85, 0))

    # C) Low Risk (< 0.35) -> Pass / Target Application
    draw_box(14.8, 5.0, 1.8, 0.9, 'Target App', c_target, c_target_edge, subtext='Mock Origin / API')
    draw_arrow(13.35, 5.0, 13.9, 5.0, label='Risk < 0.35', color='#27ae60')

    # From Deep Learning Tier -> Decision
    # DL allows to Target App or blocks
    draw_arrow(13.5, 6.8, 14.8, 5.45, label='DL Clean', color='#27ae60', label_offset=(0.2, 0.2))
    draw_arrow(13.5, 6.5, 13.2, 1.9, label='DL Threat', color='#c0392b', ls='--')

    # End Node
    end_circle = patches.Circle((14.8, 3.4), 0.45, facecolor='#27ae60', edgecolor='#229954', lw=2, zorder=2)
    ax.add_patch(end_circle)
    ax.text(14.8, 3.4, 'End', ha='center', va='center', fontsize=10, fontweight='bold', color='#ffffff', zorder=3)
    draw_arrow(14.8, 4.55, 14.8, 3.85, label='Delivers')

    # Central Logging & Database Layer
    draw_box(8.5, 7.3, 2.4, 0.9, 'Telemetry & Logging', c_db, c_db_edge, subtext='SQLite / PostgreSQL')
    
    # Arrows to Database
    draw_arrow(6.0, 6.8, 7.3, 7.3, label='Logs', ls=':', color='#7f8c8d')
    draw_arrow(10.0, 5.45, 9.5, 6.85, label='Logs', ls=':', color='#7f8c8d')
    draw_arrow(11.5, 6.8, 9.7, 7.3, label='Logs', ls=':', color='#7f8c8d')

    # Real-Time SOC Dashboard (Streamlit)
    draw_box(8.5, 8.2, 3.2, 0.55, 'Streamlit Live SOC Telemetry Dashboard', c_soc, c_soc_edge, fontsize=9)
    draw_arrow(8.5, 7.75, 8.5, 7.92, label='Streams', ls='-', color='#27ae60')

    # Title box at top left
    ax.text(0.5, 8.25, 'Figure 1: AI-WAF Gateway & Multi-Tier Cascaded System Architecture', 
            fontsize=12, fontweight='bold', color='#1a5276', ha='left', va='center')

    plt.tight_layout()
    os.makedirs('reports/figures', exist_ok=True)
    out_path = 'reports/figures/architecture_flowchart.png'
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'[SUCCESS] Architectural flowchart saved to: {out_path}')

if __name__ == '__main__':
    create_architecture_diagram()
