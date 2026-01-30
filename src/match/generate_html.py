#!/usr/bin/env python3
"""
data.txt를 읽어서 HTML 파일을 자동 생성하는 스크립트
EVNSOLUTION 차량 매칭 현황
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
    """data.txt 파싱 (차량 기준)"""
    data = defaultdict(list)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split('|')
            if len(parts) < 5:
                continue

            date, vehicle, op_type, driver = parts[:4]
            start_time = parts[4] if len(parts) > 4 else ''
            end_time = parts[5] if len(parts) > 5 else ''
            fleet = parts[6] if len(parts) > 6 else ''

            data[date].append({
                'vehicle': vehicle,
                'type': op_type if op_type else None,
                'driver': driver if driver else None,
                'start': start_time if start_time else None,
                'end': end_time if end_time else None,
                'fleet': fleet if fleet else None
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
            driver_str = f'"{item["driver"]}"' if item['driver'] else 'null'
            start_str = f'"{item["start"]}"' if item['start'] else 'null'
            end_str = f'"{item["end"]}"' if item['end'] else 'null'
            fleet_str = f'"{item["fleet"]}"' if item['fleet'] else 'null'
            item_strs.append(
                f'{{ vehicle: "{item["vehicle"]}", type: {type_str}, driver: {driver_str}, start: {start_str}, end: {end_str}, fleet: {fleet_str} }}'
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
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>EVNSOLUTION 차량 매칭 현황</title>
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
        .time-range {{
            font-size: 13px;
            color: #666;
            font-family: monospace;
        }}
        .driver-cell {{
            font-weight: 600;
            background: #f8fafc;
            vertical-align: middle;
        }}
        .group-first td {{
            border-top: 2px solid #ddd;
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
    <h1>EVNSOLUTION 차량 매칭 현황</h1>
    <p class="summary">배송원 기준 차량 매칭</p>

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
                <th>배송원</th>
                <th>플릿</th>
                <th>차량번호</th>
                <th>운영구분</th>
                <th>매칭시간</th>
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

function formatTimeRange(start, end) {{
    if (!start && !end) return '-';
    if (start && end) return `${{start}} - ${{end}}`;
    if (start) return `${{start}} -`;
    return `- ${{end}}`;
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
    const matchedVehicles = [...new Set(items.map(i => i.vehicle))];
    const matched = matchedVehicles.length;
    const uniqueDrivers = [...new Set(items.filter(i => i.driver).map(i => i.driver))];
    const driverCount = uniqueDrivers.length;

    document.getElementById('stats').innerHTML = `
        <div class="stat-card match"><div class="number">${{matched}}</div><div class="label">배정 차량</div></div>
        <div class="stat-card match"><div class="number">${{driverCount}}</div><div class="label">배정 인원</div></div>
    `;
}}

function renderTable(date) {{
    const items = data[date] || [];

    // 플릿 → 배송원 → 차량 순으로 정렬
    const sorted = [...items].sort((a,b) => {{
        const fleetA = a.fleet || '';
        const fleetB = b.fleet || '';
        if (fleetA !== fleetB) return fleetA.localeCompare(fleetB, 'ko');
        const driverA = a.driver || '';
        const driverB = b.driver || '';
        if (driverA !== driverB) return driverA.localeCompare(driverB, 'ko');
        return a.vehicle.localeCompare(b.vehicle, 'ko');
    }});

    // 배송원별 그룹화
    const grouped = {{}};
    sorted.forEach(item => {{
        const key = item.driver || '-';
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(item);
    }});

    let html = '';
    let isFirst = true;
    Object.keys(grouped).forEach(driver => {{
        const driverItems = grouped[driver];
        driverItems.forEach((item, idx) => {{
            const rowClass = idx === 0 ? 'group-first' : '';
            html += `<tr class="${{rowClass}}">`;
            if (idx === 0) {{
                html += `<td class="driver-cell" rowspan="${{driverItems.length}}">${{driver}}</td>`;
            }}
            html += `
                <td>${{item.fleet || '-'}}</td>
                <td>${{item.vehicle}}</td>
                <td>${{item.type ? `<span class="badge ${{getTypeBadgeClass(item.type)}}">${{getTypeLabel(item.type)}}</span>` : '-'}}</td>
                <td class="time-range">${{formatTimeRange(item.start, item.end)}}</td>
            </tr>`;
        }});
        isFirst = false;
    }});

    document.getElementById('tableBody').innerHTML = html;
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
