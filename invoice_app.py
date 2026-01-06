import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import os
from datetime import date

# --- CONFIGURATION ---
COMPANY_NAME = "Elite Hand Mulch LLC"
COMPANY_ADDR = "2131 Dawn Heights Dr"
COMPANY_CITY = "Lakeland, FL 33801-9367"

class PDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path

    def header(self):
        # --- LOGO SECTION ---
        if self.logo_path:
            try:
                # Add logo at top left (x=10, y=8, width=33)
                self.image(self.logo_path, 10, 8, 33)
            except:
                pass 
            
        # Move cursor to the right so text doesn't overlap logo
        self.set_y(10)
        self.set_x(50) 

        # --- COMPANY INFO ---
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'INVOICE', 0, 1, 'R')
        
        self.set_x(50) # Align text to right of logo
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, COMPANY_NAME, 0, 1, 'L')
        
        self.set_x(50)
        self.set_font('Arial', '', 10)
        self.cell(0, 5, COMPANY_ADDR, 0, 1, 'L')
        
        self.set_x(50)
        self.cell(0, 5, COMPANY_CITY, 0, 1, 'L')
        
        # Line break to separate header from body
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(client_name, client_addr, invoice_num, items_df, tax_rate, logo_file, invoice_date=None):
    # Handle Logo File
    logo_path = None
    # Prefer uploaded logo; fall back to repository asset if available
    default_logo = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
    if logo_file is not None:
        # Save uploaded logo to a temp file so PDF library can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(logo_file.read())
            logo_path = tmp.name
    elif os.path.exists(default_logo):
        logo_path = default_logo

    pdf = PDF(logo_path)
    pdf.add_page()
    pdf.set_font('Arial', '', 11)

    # --- Client & Invoice Info ---
    # Draw a line separator
    pdf.line(10, 45, 200, 45)
    pdf.ln(10)
    
    pdf.cell(100, 5, f"Bill To: {client_name}", 0, 0)
    pdf.cell(90, 5, f"Date: {invoice_date.strftime('%B %d, %Y')}", 0, 1, 'R')
    
    pdf.cell(100, 5, f"Address: {client_addr}", 0, 0)
    pdf.cell(90, 5, f"Invoice #: {invoice_num}", 0, 1, 'R')
    pdf.ln(15)

    # --- Table Header ---
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240) # Light gray background
    pdf.cell(100, 8, 'Description', 1, 0, 'L', 1)
    pdf.cell(25, 8, 'Qty', 1, 0, 'C', 1)
    pdf.cell(35, 8, 'Unit Price', 1, 0, 'R', 1)
    pdf.cell(30, 8, 'Total', 1, 1, 'R', 1)

    # --- Table Rows ---
    pdf.set_font('Arial', '', 10)
    subtotal = 0
    
    for index, row in items_df.iterrows():
        if row['Description']: 
            desc = str(row['Description'])
            qty = float(row['Qty'])
            price = float(row['Price'])
            total = qty * price
            subtotal += total

            pdf.cell(100, 8, desc, 1)
            pdf.cell(25, 8, str(qty), 1, 0, 'C')
            pdf.cell(35, 8, f"${price:,.2f}", 1, 0, 'R')
            pdf.cell(30, 8, f"${total:,.2f}", 1, 1, 'R')

    # --- Totals ---
    pdf.ln(5)
    tax_amount = subtotal * (tax_rate / 100)
    grand_total = subtotal + tax_amount

    pdf.set_font('Arial', '', 10)
    pdf.cell(160, 6, 'Subtotal:', 0, 0, 'R')
    pdf.cell(30, 6, f"${subtotal:,.2f}", 0, 1, 'R')
    
    pdf.cell(160, 6, f'Tax ({tax_rate}%):', 0, 0, 'R')
    pdf.cell(30, 6, f"${tax_amount:,.2f}", 0, 1, 'R')
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(160, 8, 'TOTAL DUE:', 0, 0, 'R')
    pdf.cell(30, 8, f"${grand_total:,.2f}", 0, 1, 'R')

    # --- Payment Info ---
    pdf.ln(15)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 190, 15, 'F') # Adjusted height since we removed a line
    
    pdf.set_xy(15, pdf.get_y() + 5)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, 'Payment Instructions:', 0, 1)
    
    pdf.set_x(15)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, 'Make checks payable to: Elite Hand Mulch LLC', 0, 1)

    # Cleanup temp logo file
    if logo_path:
        os.remove(logo_path)

    out = pdf.output(dest='S')
    if isinstance(out, str):
        return out.encode('latin-1')
    return out

# --- STREAMLIT UI ---
st.set_page_config(page_title="Elite Hand Mulch Invoicer", layout="wide")

st.title("🚜 Invoice Generator")
st.markdown("---")

# Sidebar for Logo and Settings
with st.sidebar:
    st.header("Company Branding")
    logo_file = st.file_uploader("Upload Company Logo", type=['png', 'jpg', 'jpeg'])
    st.caption("Upload your logo here. It will appear at the top-left of the PDF.")
    # Show the permanent repo logo when no custom upload provided
    try:
        if logo_file is None:
            st.image('assets/logo.png', width=150)
    except Exception:
        pass
    
    st.markdown("---")
    st.header("Tax Settings")
    tax_rate = st.number_input("Tax Rate (%)", value=0.0, step=0.1)

# Main Form
col1, col2 = st.columns(2)

with col1:
    st.subheader("Bill To (Client)")
    client_name = st.text_input("Client Name", placeholder="e.g. John Smith")
    client_addr = st.text_area("Client Address", placeholder="123 Palm Tree Ln...")

with col2:
    st.subheader("Invoice Details")
    invoice_num = st.text_input("Invoice Number", value="1001")
    invoice_date = st.date_input("Invoice Date", value=date.today())

st.markdown("### Line Items")

# Data Editor
default_data = pd.DataFrame([
    {"Description": "Mulch Installation", "Qty": 0, "Price": 0.0},
    {"Description": "Premium Mulch Materials", "Qty": 0, "Price": 0.0},
    {"Description": "Delivery Fee", "Qty": 1, "Price": 0.0},
])

edited_df = st.data_editor(
    default_data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Price": st.column_config.NumberColumn(format="$%.2f"),
        "Qty": st.column_config.NumberColumn(format="%.1f")
    }
)

st.markdown("---")

if st.button("Generate Invoice PDF", type="primary", use_container_width=True):
    if not client_name:
        st.error("Please enter a Client Name.")
    else:
        pdf_bytes = generate_pdf(client_name, client_addr, invoice_num, edited_df, tax_rate, logo_file, invoice_date)
        
        st.success("✅ Invoice Generated Successfully!")
        st.download_button(
            label="Download Invoice PDF",
            data=pdf_bytes,
            file_name=f"Invoice_{invoice_num}_{client_name}.pdf",
            mime="application/pdf"
        )