import pandas as pd
import streamlit as st
from fpdf import FPDF

# Function to generate the ticket report
def generate_ticket_report(file):
    # Read the uploaded CSV file
    data = pd.read_csv(file)
    
    # Group by first and last name, count tickets, and list seat assignments
    aggregated_data = data.groupby(['First Name', 'Last Name']).agg(
        Tickets_Ordered=('Ticket I.D.', 'count'),
        Seats=('Seat', lambda x: ', '.join(x.unique().astype(str)))
    ).reset_index()
    
    return aggregated_data

# Function to generate a PDF with checkboxes for each patron
def generate_pdf(report):
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, 'Patron Check-in List', ln=True, align='C')
    
    # Add column headers
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Patron Name', border=1)
    pdf.cell(30, 10, 'Tickets', border=1)
    pdf.cell(120, 10, 'Seats', border=1)
    pdf.cell(0, 10, '', ln=True)  # Move to next line
    
    # Add a line for each patron with checkboxes
    pdf.set_font('Arial', '', 12)
    for index, row in report.iterrows():
        # Add a checkbox for each patron
        pdf.cell(10, 10, '[ ]', border=0)  # Checkbox
        
        # Add patron name, ticket count, and seats
        name = f"{row['First Name']} {row['Last Name']}"
        pdf.cell(40, 10, name, border=1)
        pdf.cell(30, 10, str(row['Tickets_Ordered']), border=1)
        pdf.cell(120, 10, row['Seats'], border=1)
        pdf.cell(0, 10, '', ln=True)  # Move to next line
    
    return pdf

# Streamlit app starts here
st.title("🎟️ Ticket Order Aggregator with PDF Check-in List")
st.write("""
This app allows you to upload a CSV file containing ticket orders, 
aggregate the data by name, and generate a PDF with a check-in list for patrons.
""")

# Sidebar for file upload
st.sidebar.header("Upload your file here:")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Display instructions if no file is uploaded
if uploaded_file is None:
    st.warning("Please upload a CSV file to start.")

# Main processing block when file is uploaded
if uploaded_file is not None:
    # Display the uploaded file name
    st.sidebar.success(f"File uploaded: {uploaded_file.name}")
    
    # Call the processing function
    try:
        report = generate_ticket_report(uploaded_file)
        
        # Show the aggregated report as a table
        st.write("### Aggregated Ticket Report:")
        st.dataframe(report)
        
        # Add a button to allow users to download the aggregated report as CSV
        csv = report.to_csv(index=False)
        st.download_button(
            label="📥 Download report as CSV",
            data=csv,
            file_name='Aggregated_Ticket_Report.csv',
            mime='text/csv'
        )

        # Generate and download the PDF
        if st.button('📄 Generate PDF with Checkboxes'):
            pdf = generate_pdf(report)
            pdf_output = pdf.output(dest='S').encode('latin1')  # Get PDF as binary data
            st.download_button(
                label="📥 Download Check-in List as PDF",
                data=pdf_output,
                file_name="Patron_Checkin_List.pdf",
                mime="application/pdf"
            )
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Footer information
st.markdown("""
---
*Created with Streamlit*  
If you encounter any issues, please contact support.
""")
