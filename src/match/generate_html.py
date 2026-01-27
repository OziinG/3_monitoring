#!/usr/bin/env python3
"""
data.txt를 읽어서 HTML 파일을 자동 생성하는 스크립트
사용법: python3 generate_html.py
"""

import os
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # 3_monitoring/
DATA_FILE = os.path.join(SCRIPT_DIR, "data.txt")
HTML_FILE = os.path.join(PROJECT_DIR, "match.html")


def parse_data():
    """data.txt 파싱"""
    data = defaultdict(list)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split('|')
            if len(parts) != 4:
                continue

            date, name, op_type, match = parts
            data[date].append({
                'name': name,
                'type': op_type if op_type else None,
                'match': match == 'O'
            })

    return dict(data)


def generate_html(data):
    """HTML 생성"""
    js_data_items = []
    for date in sorted(data.keys()):
        items = data[date]
        item_strs = []
        for item in items:
            type_str = f'"{item["type"]}"' if item['type'] else 'null'
            match_str = 'true' if item['match'] else 'false'
            item_strs.append(
                f'{{ name: "{item["name"]}", type: {type_str}, match: {match_str} }}'
            )
        js_data_items.append(
            f'            "{date}": [\n                ' +
            ',\n                '.join(item_strs) +
            '\n            ]'
        )

    js_data = '{\n' + ',\n'.join(js_data_items) + '\n        }'
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>컬리/R 차량 매칭 현황</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }}
        .summary {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .header-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .date-selector {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .date-selector select {{
            padding: 10px 20px;
            font-size: 16px;
            font-weight: 600;
            border: 2px solid #5B5BD6;
            border-radius: 8px;
            background: white;
            color: #333;
            cursor: pointer;
            min-width: 160px;
            margin-right: 8px;
        }}
        .nav-btn {{
            width: 36px;
            height: 36px;
            border: 2px solid #5B5BD6;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            color: #5B5BD6;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .stat-card {{
            background: white;
            padding: 20px 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 36px;
            font-weight: bold;
            color: #5B5BD6;
        }}
        .stat-card.match .number {{
            color: #22c55e;
        }}
        .stat-card.nomatch .number {{
            color: #ef4444;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #5B5BD6;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-match {{
            background: #dcfce7;
            color: #166534;
        }}
        .badge-nomatch {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .badge-company {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .badge-subscription {{
            background: #f3e8ff;
            color: #6b21a8;
        }}
        .badge-sales {{
            background: #fef3c7;
            color: #92400e;
        }}
        .badge-owner {{
            background: #d1fae5;
            color: #065f46;
        }}
        .badge-other {{
            background: #f1f5f9;
            color: #475569;
        }}
        .update-time {{
            text-align: center;
            color: #999;
            margin-top: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>컬리/R 차량 매칭 현황</h1>
    <p class="summary">Fleet ID: 29 | 근태 출근자 기준</p>

    <div class="header-row">
        <div class="date-selector">
            <select id="dateSelect" onchange="selectDate(this.value)"></select>
            <button class="nav-btn" id="prevBtn" onclick="prevDate()">&#9664;</button>
            <button class="nav-btn" id="nextBtn" onclick="nextDate()">&#9654;</button>
        </div>
        <div class="stats" id="stats"></div>
    </div>

    <table>
        <thead>
            <tr>
                <th>날짜</th>
                <th>근태자</th>
                <th>운영구분</th>
                <th>차량매칭</th>
            </tr>
        </thead>
        <tbody id="tableBody"></tbody>
    </table>

    <p class="update-time">마지막 업데이트: {now_str}</p>
</div>

<script>
const data = {js_data};
const sortedDates = Object.keys(data).sort().reverse();
let currentDate = sortedDates[0];

function getTypeLabel(type) {{
    const labels = {{
        'COMPANY_OWNED': '직영',
        'SUBSCRIPTION': '구독',
        'SALES': '판매',
        'OWNER_OPERATOR': '지입',
        'OTHER': '기타'
    }};
    return labels[type] || type;
}}

function getTypeBadgeClass(type) {{
    const classes = {{
        'COMPANY_OWNED': 'badge-company',
        'SUBSCRIPTION': 'badge-subscription',
        'SALES': 'badge-sales',
        'OWNER_OPERATOR': 'badge-owner',
        'OTHER': 'badge-other'
    }};
    return classes[type] || 'badge-other';
}}

function formatDateLabel(dateStr) {{
    const date = new Date(dateStr);
    const days = ['일','월','화','수','목','금','토'];
    return `${{date.getMonth()+1}}월 ${{date.getDate()}}일 (${{days[date.getDay()]}})`;
}}

function renderDateNav() {{
    const select = document.getElementById('dateSelect');
    select.innerHTML = sortedDates.map(d =>
        `<option value="${{d}}" ${{d === currentDate ? 'selected' : ''}}>${{formatDateLabel(d)}}</option>`
    ).join('');

    const idx = sortedDates.indexOf(currentDate);
    document.getElementById('prevBtn').disabled = idx >= sortedDates.length - 1;
    document.getElementById('nextBtn').disabled = idx <= 0;
}}

function renderStats(date) {{
    const items = data[date] || [];
    const total = items.length;
    const matched = items.filter(i => i.match).length;
    const notMatched = total - matched;
    const rate = total ? Math.round(matched / total * 100) : 0;

    document.getElementById('stats').innerHTML = `
        <div class="stat-card"><div class="number">${{total}}</div><div class="label">총 출근자</div></div>
        <div class="stat-card match"><div class="number">${{matched}}</div><div class="label">매칭 완료</div></div>
        <div class="stat-card nomatch"><div class="number">${{notMatched}}</div><div class="label">미매칭</div></div>
        <div class="stat-card"><div class="number">${{rate}}%</div><div class="label">매칭률</div></div>
    `;
}}

function renderTable(date) {{
    const items = data[date] || [];
    const sorted = [...items].sort((a,b) => {{
        if (a.match !== b.match) return b.match - a.match;
        return a.name.localeCompare(b.name,'ko');
    }});

    document.getElementById('tableBody').innerHTML = sorted.map(item => `
        <tr>
            <td>${{date}}</td>
            <td>${{item.name}}</td>
            <td>${{item.type ? `<span class="badge ${{getTypeBadgeClass(item.type)}}">${{getTypeLabel(item.type)}}</span>` : '-'}}</td>
            <td><span class="badge ${{item.match ? 'badge-match' : 'badge-nomatch'}}">${{item.match ? 'O' : 'X'}}</span></td>
        </tr>
    `).join('');
}}

function selectDate(date) {{
    currentDate = date;
    renderDateNav();
    renderStats(date);
    renderTable(date);
}}

function prevDate() {{
    const i = sortedDates.indexOf(currentDate);
    if (i < sortedDates.length - 1) selectDate(sortedDates[i + 1]);
}}

function nextDate() {{
    const i = sortedDates.indexOf(currentDate);
    if (i > 0) selectDate(sortedDates[i - 1]);
}}

renderDateNav();
renderStats(currentDate);
renderTable(currentDate);
</script>
</body>
</html>'''

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML 생성 완료: {HTML_FILE}")


def main():
    if not os.path.exists(DATA_FILE):
        print(f"데이터 파일이 없습니다: {DATA_FILE}")
        return

    data = parse_data()
    if not data:
        print("파싱된 데이터가 없습니다")
        return

    generate_html(data)


if __name__ == '__main__':
    main()
