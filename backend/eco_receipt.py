import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import datetime

def calculate_trees_saved(receipts_count):
    TREES_PER_RECEIPT = 0.0002
    trees_saved = receipts_count * TREES_PER_RECEIPT
    return round(trees_saved, 4)

def estimate_carbon_avoided(receipts_count):
    CO2_PER_RECEIPT_GRAMS = 2.5
    total_grams = receipts_count * CO2_PER_RECEIPT_GRAMS
    total_kg = total_grams / 1000
    return round(total_kg, 3)

def get_tree_saving_stats(items):
    receipts_count = 1
    trees = calculate_trees_saved(receipts_count)
    carbon = estimate_carbon_avoided(receipts_count)
    return {
        'receipts_issued': receipts_count,
        'trees_saved': trees,
        'co2_avoided_kg': carbon
    }

def generate_pdf_receipt(receipt_id, items, total, stats, customer_number="", served_by="Don Kelvin", payment_method="Cash"):
    buffer = io.BytesIO()
    width, height = 80 * mm, 200 * mm
    p = canvas.Canvas(buffer, pagesize=(width, height))
    y = height - 10 * mm
    # Header
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(width/2, y, "🧾 StarSon POS")
    y -= 6 * mm
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, y, "Bright Arm Enterprise")
    y -= 7 * mm
    p.setFont("Helvetica", 9)
    p.drawString(7*mm, y, f"Receipt No: #SR-{receipt_id:06d}")
    y -= 5 * mm
    if customer_number:
        p.drawString(7*mm, y, f"Client: {customer_number}")
        y -= 5 * mm
    p.drawString(7*mm, y, f"Served by: {served_by}")
    y -= 5 * mm
    p.drawString(7*mm, y, f"Date: {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}")
    y -= 5 * mm
    p.drawString(7*mm, y, f"Payment Method: {payment_method}")
    y -= 6 * mm
    p.line(5*mm, y, width-5*mm, y)
    y -= 5 * mm
    # Items
    p.setFont("Helvetica", 9)
    for item in items:
        p.drawString(7*mm, y, f"{item['name']} x {item['qty']} - KES {item['price']*item['qty']:.2f}")
        y -= 5 * mm
    y -= 2 * mm
    p.line(5*mm, y, width-5*mm, y)
    y -= 5 * mm
    # Subtotal, VAT, Total
    subtotal = total / 1.16
    vat = total - subtotal
    p.setFont("Helvetica-Bold", 9)
    p.drawString(7*mm, y, "Subtotal:")
    p.drawRightString(width-7*mm, y, f"KES {subtotal:.2f}")
    y -= 5 * mm
    p.setFont("Helvetica", 9)
    p.drawString(7*mm, y, "VAT (16%):")
    p.drawRightString(width-7*mm, y, f"KES {vat:.2f}")
    y -= 5 * mm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(7*mm, y, "Total:")
    p.drawRightString(width-7*mm, y, f"KES {total:.2f}")
    y -= 8 * mm
    # Eco Impact
    p.setFont("Helvetica-Bold", 9)
    p.setFillColor(colors.darkgreen)
    p.drawString(7*mm, y, f"🌱 Eco Impact: You saved {int(stats['co2_avoided_kg']*1000)}g of carbon/paper waste.")
    y -= 5 * mm
    p.drawString(7*mm, y, f"Trees saved: {stats['trees_saved']}")
    p.setFillColor(colors.black)
    y -= 7 * mm
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(7*mm, y, "This is a digital, paperless receipt.")
    y -= 5 * mm
    p.drawString(7*mm, y, "Thank you for supporting a greener future 🌍")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def generate_eco_receipt_footer(receipts_count):
    trees = calculate_trees_saved(receipts_count)
    carbon = estimate_carbon_avoided(receipts_count)
    
    footer = (
        f"🌱 Eco Receipt Summary 🌍\n"
        f"Receipts issued: {receipts_count}\n"
        f"Trees saved: {trees}\n"
        f"CO₂ avoided: {carbon} kg\n"
        f"Thank you for going green with StarSon POS 💚"
    )
    return footer

# Example for one receipt
if __name__ == "__main__":
    print(generate_eco_receipt_footer(1))