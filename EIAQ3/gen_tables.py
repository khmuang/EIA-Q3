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
    '3': '3 Patch Update', '4': '4 Antivirus', '5': '5 Firewall',
    '6': '6 Client join domain', '7': '7 Privileged User', '8': '8 Document Request'
}

def get_status_class(pct):
    if pct >= 75: return 'color: #10b981; font-weight: bold;'
    if pct >= 40: return 'color: #f59e0b; font-weight: bold;'
    return 'color: #f43f5e; font-weight: bold;'

html_tables = """<div class="summary-info-card" style="grid-column: 1 / -1;">
<style>
.detailed-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.8rem; color: #fff; background: rgba(0, 0, 0, 0.2); border-radius: 8px; overflow: hidden; margin-bottom: 25px; }
.detailed-table th { background: rgba(255, 255, 255, 0.1); padding: 8px 10px; text-align: left; font-weight: 600; font-size: 0.75rem; }
.detailed-table td { padding: 8px 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
.detailed-table tr:hover { background: rgba(255, 255, 255, 0.05); }
.team-summary-box { display: flex; align-items: center; justify-content: space-between; margin-top: 5px; flex-wrap: wrap; gap: 10px; }
.team-stats { display: flex; gap: 10px; font-size: 0.85rem; }
.stat-badge { padding: 4px 10px; border-radius: 6px; font-weight: bold; }
.team-desc { font-size: 0.85rem; color: var(--text-dim); width: 100%; margin-top: 5px; }
.toggle-q1-btn { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; margin-left: 10px; transition: 0.2s; }
.toggle-q1-btn:hover { background: rgba(255,255,255,0.2); }
</style>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h4 style="font-size: 1.2rem; margin: 0;">📊 สรุปความคืบหน้าและข้อมูลเจาะลึกรายทีม (Team Performance & Deep Dive)</h4>
        <button class="toggle-q1-btn" onclick="toggleQ1()">👁️ Show/Hide Q1</button>
    </div>
    <script>
    function toggleQ1() {
        const q1Cols = document.querySelectorAll('.col-q1');
        q1Cols.forEach(col => {
            col.style.display = (col.style.display === 'none' || col.style.display === '') ? 'table-cell' : 'none';
        });
    }
    </script>

"""

def get_bg_color(pct):
    if pct >= 90: return 'rgba(16,185,129,0.15)'
    elif pct >= 70: return 'rgba(59,130,246,0.15)'
    elif pct >= 50: return 'rgba(245,158,11,0.15)'
    else: return 'rgba(244,63,94,0.15)'

def get_text_color(pct):
    if pct >= 90: return 'var(--accent-emerald)'
    elif pct >= 70: return 'var(--accent-blue)'
    elif pct >= 50: return 'var(--accent-amber)'
    else: return 'var(--accent-rose)'

for team in ['HO', 'DC', 'Branch']:
    # 1. First Pass: Calculate Totals
    team_q1_t, team_q1_s = 0, 0
    team_q2_t, team_q2_s = 0, 0
    team_q3_t, team_q3_s = 0, 0
    
    for tid in topic_order:
        phases = data.get(team, {}).get(tid, {})
        team_q1_t += phases.get('Q1', {}).get('total', 0)
        team_q1_s += phases.get('Q1', {}).get('success', 0)
        team_q2_t += phases.get('Q2', {}).get('total', 0)
        team_q2_s += phases.get('Q2', {}).get('success', 0)
        team_q3_t += phases.get('Q3', {}).get('total', 0)
        team_q3_s += phases.get('Q3', {}).get('success', 0)
        
    team_all_t = team_q1_t + team_q2_t + team_q3_t
    team_all_s = team_q1_s + team_q2_s + team_q3_s
    
    all_pct = round((team_all_s/team_all_t)*100) if team_all_t > 0 else 0
    q1_pct = round((team_q1_s/team_q1_t)*100) if team_q1_t > 0 else 0
    q2_pct = round((team_q2_s/team_q2_t)*100) if team_q2_t > 0 else 0
    q3_pct = round((team_q3_s/team_q3_t)*100) if team_q3_t > 0 else 0
    
    medal = '🥇' if team == 'HO' else ('🥈' if team == 'DC' else '🥉')
    
    # 2. Build HTML Header
    html_tables += f"""
    <div class="ranking-item" style="{'border: 1px solid rgba(250,204,21,0.3);' if team=='HO' else ''}">
        <div class="rank-header">
            <span class="rank-name" style="font-size: 1.15rem;">{medal} ทีม {team}</span>
            <span class="rank-val" style="font-size: 1.1rem;">ภาพรวม {all_pct}%</span>
        </div>
        <div class="team-summary-box">
            <div class="team-stats">
                <div class="stat-badge col-q1" style="background: {get_bg_color(q1_pct)}; color: {get_text_color(q1_pct)}; display:none;">Q1: {q1_pct}%</div>
                <div class="stat-badge" style="background: {get_bg_color(q2_pct)}; color: {get_text_color(q2_pct)};">Q2: {q2_pct}%</div>
                <div class="stat-badge" style="background: {get_bg_color(q3_pct)}; color: {get_text_color(q3_pct)};">Q3: {q3_pct}%</div>
            </div>
        </div>
        
        <table class="detailed-table">
            <thead>
                <tr>
                    <th>Topic</th>
                    <th class="col-q1" style="display:none;">Phase Q1</th>
                    <th>Phase Q2</th>
                    <th>Phase Q3</th>
                    <th>Overall</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # 3. Build Table Rows
    for tid in topic_order:
        phases = data.get(team, {}).get(tid, {})
        
        q1_t = phases.get('Q1', {}).get('total', 0)
        q1_s = phases.get('Q1', {}).get('success', 0)
        q1_pct_row = round((q1_s/q1_t)*100) if q1_t > 0 else 0
        q1_str = f'<span style="{get_status_class(q1_pct_row)}">{q1_s:,}/{q1_t:,} ({q1_pct_row}%)</span>' if q1_t > 0 else '-'
        
        q2_t = phases.get('Q2', {}).get('total', 0)
        q2_s = phases.get('Q2', {}).get('success', 0)
        q2_pct_row = round((q2_s/q2_t)*100) if q2_t > 0 else 0
        q2_str = f'<span style="{get_status_class(q2_pct_row)}">{q2_s:,}/{q2_t:,} ({q2_pct_row}%)</span>' if q2_t > 0 else '-'
        
        q3_t = phases.get('Q3', {}).get('total', 0)
        q3_s = phases.get('Q3', {}).get('success', 0)
        q3_pct_row = round((q3_s/q3_t)*100) if q3_t > 0 else 0
        q3_str = f'<span style="{get_status_class(q3_pct_row)}">{q3_s:,}/{q3_t:,} ({q3_pct_row}%)</span>' if q3_t > 0 else '-'
        
        all_t = q1_t + q2_t + q3_t
        all_s = q1_s + q2_s + q3_s
        all_pct_row = round((all_s/all_t)*100) if all_t > 0 else 0
        all_str = f'<span style="{get_status_class(all_pct_row)}">{all_s:,}/{all_t:,} ({all_pct_row}%)</span>' if all_t > 0 else '-'
        
        html_tables += f"""
                <tr>
                    <td>Topic {topic_names[tid]}</td>
                    <td class="col-q1" style="display:none;">{q1_str}</td>
                    <td>{q2_str}</td>
                    <td>{q3_str}</td>
                    <td>{all_str}</td>
                </tr>
        """
        
    team_q1_pct = round((team_q1_s/team_q1_t)*100) if team_q1_t > 0 else 0
    team_q1_str = f'<span style="{get_status_class(team_q1_pct)}">{team_q1_s:,}/{team_q1_t:,} ({team_q1_pct}%)</span>' if team_q1_t > 0 else '-'
    
    team_q2_pct = round((team_q2_s/team_q2_t)*100) if team_q2_t > 0 else 0
    team_q2_str = f'<span style="{get_status_class(team_q2_pct)}">{team_q2_s:,}/{team_q2_t:,} ({team_q2_pct}%)</span>' if team_q2_t > 0 else '-'
    
    team_q3_pct = round((team_q3_s/team_q3_t)*100) if team_q3_t > 0 else 0
    team_q3_str = f'<span style="{get_status_class(team_q3_pct)}">{team_q3_s:,}/{team_q3_t:,} ({team_q3_pct}%)</span>' if team_q3_t > 0 else '-'
    
    team_all_t = team_q1_t + team_q2_t + team_q3_t
    team_all_s = team_q1_s + team_q2_s + team_q3_s
    team_all_pct = round((team_all_s/team_all_t)*100) if team_all_t > 0 else 0
    team_all_str = f'<span style="{get_status_class(team_all_pct)}">{team_all_s:,}/{team_all_t:,} ({team_all_pct}%)</span>' if team_all_t > 0 else '-'
    
    # Calculate Total Y and Total N
    team_q1_y = team_q1_s
    team_q2_y = team_q2_s
    team_q3_y = team_q3_s
    team_all_y = team_all_s
    
    team_q1_n = team_q1_t - team_q1_s
    team_q2_n = team_q2_t - team_q2_s
    team_q3_n = team_q3_t - team_q3_s
    team_all_n = team_all_t - team_all_s
    
    html_tables += f"""
                <tr style="background: rgba(255, 255, 255, 0.1); border-top: 2px solid rgba(255, 255, 255, 0.2);">
                    <td style="font-weight: 800; font-size: 0.85rem;">Grand Total (ผลรวม)</td>
                    <td class="col-q1" style="font-weight: 800; font-size: 0.85rem; display:none;">{team_q1_str}</td>
                    <td style="font-weight: 800; font-size: 0.85rem;">{team_q2_str}</td>
                    <td style="font-weight: 800; font-size: 0.85rem;">{team_q3_str}</td>
                    <td style="font-weight: 800; font-size: 0.85rem;">{team_all_str}</td>
                </tr>
                <tr style="background: rgba(16, 185, 129, 0.1);">
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-emerald);">Total Y (สำเร็จ)</td>
                    <td class="col-q1" style="font-weight: 700; font-size: 0.8rem; color: var(--accent-emerald); display:none;">{team_q1_y:,}</td>
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-emerald);">{team_q2_y:,}</td>
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-emerald);">{team_q3_y:,}</td>
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-emerald);">{team_all_y:,}</td>
                </tr>
                <tr style="background: rgba(244, 63, 94, 0.1);">
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-rose);">Total N (รอดำเนินการ)</td>
                    <td class="col-q1" style="font-weight: 700; font-size: 0.8rem; color: var(--accent-rose); display:none;">{team_q1_n:,}</td>
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-rose);">{team_q2_n:,}</td>
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-rose);">{team_q3_n:,}</td>
                    <td style="font-weight: 700; font-size: 0.8rem; color: var(--accent-rose);">{team_all_n:,}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """

html_tables += '</div> <!-- End of Detailed Tables summary-info-card -->'

pattern = re.compile(r'<div class="summary-info-card" style="grid-column: 1 / -1;">.*?<!-- End of Detailed Tables summary-info-card -->', re.DOTALL)
new_html = pattern.sub(html_tables, html_content)

with open('index_preview_detailed.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('Success')
