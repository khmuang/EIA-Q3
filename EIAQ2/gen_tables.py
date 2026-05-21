import json
import re

html_file = 'index_preview_detailed.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

with open('data.js', 'r', encoding='utf-8') as f:
    data_content = f.read()
json_str = re.search(r'const DASHBOARD_DATA = ({.*?});', data_content, re.DOTALL).group(1)
data = json.loads(json_str)

topic_order = ['1.1', '1.2', '2', '3', '4', '5', '6', '7', '8']
topic_names = {
    '1.1': '1.1 IT Asset', '1.2': '1.2 GLPI agent', '2': '2 Update OS',
    '3': '3 Require Restart', '4': '4 Antivirus', '5': '5 Firewall',
    '6': '6 Client join domain', '7': '7 Privileged User', '8': '8 Document Request'
}

def get_status_class(pct):
    if pct >= 75: return 'color: #10b981; font-weight: bold;'
    if pct >= 40: return 'color: #f59e0b; font-weight: bold;'
    return 'color: #f43f5e; font-weight: bold;'

html_tables = """
<style>
.detailed-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.8rem; color: #fff; background: rgba(0, 0, 0, 0.2); border-radius: 8px; overflow: hidden; margin-bottom: 25px; }
.detailed-table th { background: rgba(255, 255, 255, 0.1); padding: 8px 10px; text-align: left; font-weight: 600; font-size: 0.75rem; }
.detailed-table td { padding: 8px 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.detailed-table tr:hover { background: rgba(255, 255, 255, 0.05); }
.team-summary-box { display: flex; align-items: center; justify-content: space-between; margin-top: 5px; flex-wrap: wrap; gap: 10px; }
.team-stats { display: flex; gap: 10px; font-size: 0.85rem; }
.stat-badge { padding: 4px 10px; border-radius: 6px; font-weight: bold; }
.team-desc { font-size: 0.85rem; color: var(--text-dim); width: 100%; margin-top: 5px; }
</style>
<div class="summary-info-card" style="grid-column: 1 / -1;">
    <h4 style="margin-bottom: 20px; font-size: 1.2rem;">📊 สรุปความคืบหน้าและข้อมูลเจาะลึกรายทีม (Team Performance & Deep Dive)</h4>
"""

team_summaries = {
    'HO': {
        'medal': '🥇', 'all': '42%', 'q1': '16%', 'q2': '88% (Excellent)',
        'q1_bg': 'rgba(244,63,94,0.15)', 'q1_c': 'var(--accent-rose)',
        'q2_bg': 'rgba(16,185,129,0.15)', 'q2_c': 'var(--accent-emerald)',
        'desc': '🌟 เคลียร์งานใหม่ใน Phase Q2 ได้อย่างสมบูรณ์แบบ ถือเป็นมาตรฐานผู้นำ'
    },
    'DC': {
        'medal': '🥈', 'all': '22%', 'q1': '9%', 'q2': '63% (High Growth)',
        'q1_bg': 'rgba(244,63,94,0.15)', 'q1_c': 'var(--accent-rose)',
        'q2_bg': 'rgba(16,185,129,0.15)', 'q2_c': 'var(--accent-emerald)',
        'desc': '🚀 มีอัตราการเติบโตแบบก้าวกระโดด สามารถรับมือกับเฟส Q2 ได้ดีมาก'
    },
    'Branch': {
        'medal': '🥉', 'all': '9%', 'q1': '3%', 'q2': '23% (Progressing)',
        'q1_bg': 'rgba(244,63,94,0.15)', 'q1_c': 'var(--accent-rose)',
        'q2_bg': 'rgba(59,130,246,0.15)', 'q2_c': 'var(--accent-blue)',
        'desc': '📈 แม้มีปริมาณงานหน้าสาขาจำนวนมหาศาล แต่เริ่มเห็นพัฒนาการในเฟส Q2'
    }
}

for team in ['HO', 'DC', 'Branch']:
    ts = team_summaries[team]
    html_tables += f"""
    <div class="ranking-item" style="{'border: 1px solid rgba(250,204,21,0.3);' if team=='HO' else ''}">
        <div class="rank-header">
            <span class="rank-name" style="font-size: 1.15rem;">{ts['medal']} ทีม {team}</span>
            <span class="rank-val" style="font-size: 1.1rem;">ภาพรวม {ts['all']}</span>
        </div>
        <div class="team-summary-box">
            <div class="team-stats">
                <div class="stat-badge" style="background: {ts['q1_bg']}; color: {ts['q1_c']};">Q1: {ts['q1']}</div>
                <div class="stat-badge" style="background: {ts['q2_bg']}; color: {ts['q2_c']};">Q2: {ts['q2']}</div>
            </div>
        </div>
        <div class="team-desc">{ts['desc']}</div>
        
        <table class="detailed-table">
            <thead>
                <tr>
                    <th>Topic</th>
                    <th>Phase Q1</th>
                    <th>Phase Q2</th>
                    <th>Overall</th>
                </tr>
            </thead>
            <tbody>
    """
    
    team_q1_t, team_q1_s = 0, 0
    team_q2_t, team_q2_s = 0, 0
    
    for tid in topic_order:
        phases = data.get(team, {}).get(tid, {})
        
        q1_t = phases.get('Q1', {}).get('total', 0)
        q1_s = phases.get('Q1', {}).get('success', 0)
        q1_pct = round((q1_s/q1_t)*100) if q1_t > 0 else 0
        q1_str = f'<span style="{get_status_class(q1_pct)}">{q1_s:,}/{q1_t:,} ({q1_pct}%)</span>' if q1_t > 0 else '-'
        
        q2_t = phases.get('Q2', {}).get('total', 0)
        q2_s = phases.get('Q2', {}).get('success', 0)
        q2_pct = round((q2_s/q2_t)*100) if q2_t > 0 else 0
        q2_str = f'<span style="{get_status_class(q2_pct)}">{q2_s:,}/{q2_t:,} ({q2_pct}%)</span>' if q2_t > 0 else '-'
        
        team_q1_t += q1_t
        team_q1_s += q1_s
        team_q2_t += q2_t
        team_q2_s += q2_s
        
        all_t = q1_t + q2_t
        all_s = q1_s + q2_s
        all_pct = round((all_s/all_t)*100) if all_t > 0 else 0
        all_str = f'<span style="{get_status_class(all_pct)}">{all_s:,}/{all_t:,} ({all_pct}%)</span>' if all_t > 0 else '-'
        
        html_tables += f"""
                <tr>
                    <td>Topic {topic_names[tid]}</td>
                    <td>{q1_str}</td>
                    <td>{q2_str}</td>
                    <td>{all_str}</td>
                </tr>
        """
        
    team_q1_pct = round((team_q1_s/team_q1_t)*100) if team_q1_t > 0 else 0
    team_q1_str = f'<span style="{get_status_class(team_q1_pct)}">{team_q1_s:,}/{team_q1_t:,} ({team_q1_pct}%)</span>' if team_q1_t > 0 else '-'
    
    team_q2_pct = round((team_q2_s/team_q2_t)*100) if team_q2_t > 0 else 0
    team_q2_str = f'<span style="{get_status_class(team_q2_pct)}">{team_q2_s:,}/{team_q2_t:,} ({team_q2_pct}%)</span>' if team_q2_t > 0 else '-'
    
    team_all_t = team_q1_t + team_q2_t
    team_all_s = team_q1_s + team_q2_s
    team_all_pct = round((team_all_s/team_all_t)*100) if team_all_t > 0 else 0
    team_all_str = f'<span style="{get_status_class(team_all_pct)}">{team_all_s:,}/{team_all_t:,} ({team_all_pct}%)</span>' if team_all_t > 0 else '-'
    
    html_tables += f"""
                <tr style="background: rgba(255, 255, 255, 0.1); border-top: 2px solid rgba(255, 255, 255, 0.2);">
                    <td style="font-weight: 800; font-size: 0.85rem;">Grand Total (ผลรวม)</td>
                    <td style="font-weight: 800; font-size: 0.85rem;">{team_q1_str}</td>
                    <td style="font-weight: 800; font-size: 0.85rem;">{team_q2_str}</td>
                    <td style="font-weight: 800; font-size: 0.85rem;">{team_all_str}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """

html_tables += '</div> <!-- End of Detailed Tables summary-info-card -->'

pattern = re.compile(r'<div class="summary-info-card" style="grid-column: 1 / -1;">\s*<h4 style="margin-bottom: 20px; font-size: 1.2rem;">📊 สรุปความคืบหน้าและข้อมูลเจาะลึกรายทีม.*?<!-- End of Detailed Tables summary-info-card -->', re.DOTALL)
new_html = pattern.sub(html_tables, html_content)

with open('index_preview_detailed.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('Success')
