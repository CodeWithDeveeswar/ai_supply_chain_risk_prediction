from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from flask import send_file
from datetime import datetime
import sqlite3
import os

def export_excel(db_path):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    # 🔥 HUMAN READABLE MAPS
    region_map = {
        0: "Asia", 1: "Europe", 2: "North America",
        3: "South America", 4: "Africa"
    }

    transport_map = {
        0: "Truck", 1: "Rail", 2: "Ship", 3: "Air"
    }

    weather_map = {
        0: "Clear", 1: "Rain", 2: "Storm",
        3: "Snow", 4: "Fog"
    }

    demand_map = {0: "Low", 1: "Medium", 2: "High"}
    traffic_map = {0: "Low", 1: "Medium", 2: "High"}
    port_map = {0: "No", 1: "Yes"}

    wb = Workbook()
    ws = wb.active
    ws.title = "Supply Chain Report"

    # 🎨 HEADER STYLE
    header_fill = PatternFill(start_color="1E3A8A", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    # ✅ CLEAN COLUMN NAMES
    clean_columns = [
        "ID", "Date", "Supplier", "Region", "Transport",
        "Delay (Days)", "Weather", "Demand",
        "Inventory", "Traffic", "Port Delay",
        "Order Value ($)", "Fuel Cost ($/unit)", "Risk"
    ]

    # HEADER
    for col_num, col_name in enumerate(clean_columns, 1):
        cell = ws.cell(row=1, column=col_num, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        cell.border = border

    # DATA
    for row_num, row in enumerate(rows, 2):

        row = list(row)

        # 🔥 CONVERT TO HUMAN READABLE
        row[3] = region_map.get(row[3], "Unknown")
        row[4] = transport_map.get(row[4], "Unknown")
        row[6] = weather_map.get(row[6], "Unknown")
        row[7] = demand_map.get(row[7], "Unknown")
        row[9] = traffic_map.get(row[9], "Unknown")
        row[10] = port_map.get(row[10], "No")

        for col_num, value in enumerate(row, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.alignment = Alignment(horizontal="center")
            cell.border = border

            # 🎨 RISK COLOR
            if columns[col_num - 1] == "risk":
                if value == "High":
                    cell.fill = PatternFill(start_color="FECACA", fill_type="solid")
                elif value == "Medium":
                    cell.fill = PatternFill(start_color="FED7AA", fill_type="solid")
                elif value == "Low":
                    cell.fill = PatternFill(start_color="BBF7D0", fill_type="solid")

    # AUTO WIDTH
    for col in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 4

    downloads_path = os.path.join(os.path.expanduser(""), "Downloads")
    filename = f"supply_chain_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = os.path.join(downloads_path, filename)
    wb.save(file_path)
    conn.close()

    return send_file(file_path, as_attachment=True)