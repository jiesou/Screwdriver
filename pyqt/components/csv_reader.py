import csv
from typing import List, Dict

def parse_csv(filepath: str) -> List[Dict]:
    screws = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                screws.append({
                    "tag": str(row.get('标签', i+1)),
                    "status": "等待中",
                    "position": {
                        "x": float(row.get('X位置(m)', 0)),
                        "y": float(row.get('Y位置(m)', 0)), 
                        "allowOffset": float(row.get('允许误差', 0.1))
                    }
                })
            except ValueError as e:
                print(f"Error parsing row {i}: {e}")
                continue
    return screws

def export_csv(filepath: str, screws: List[Dict]):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['标签', 'X位置(m)', 'Y位置(m)', '允许误差'])
        for screw in screws:
            writer.writerow([
                screw['tag'],
                screw['position']['x'],
                screw['position']['y'],
                screw['position']['allowOffset']
            ])
