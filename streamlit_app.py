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
    
    # Sort by last name
    aggregated_data = aggregated_data.sort_values(by=['Last Name', 'First Name'])
    
    return aggregated_data

# Function to generate a PDF with checkboxes for each patron using MultiCell for seat wrapping
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(200, 10, 'Patron Check-in List', ln=True, align='C')

    def add_table_row(self, name, tickets, seats):
        # Add checkbox
        self.cell(10, 10, '[ ]', border=1, ln=False)
        
        # Add patron name (Last Name, First Name)
        self.cell(60, 10, name, border=1, ln=False)
        
        # Add tickets ordered
        self.cell(20, 10, str(tickets), border=1, ln=False)
        
        # Add seats with MultiCell for text wrapping
        x, y = self.get_x(), self.get_y()  # Save the current position for MultiCell alignment
        self.multi_cell(100, 10, seats, border=1)
        self.set_xy(x + 100, y)  # Reset position to the end of MultiCell
    
# Function to generate the PDF document
def generate_pdf(report):
    pdf = PDF()
    pdf.add_page()

    # Add column headers
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(10, 10, '', border=0)  # Checkbox column
    pdf.cell(60, 10, 'Last Name, First Name', border=1)
    pdf.cell(20, 10, 'Tickets', border=1)
    pdf.cell(100, 10, 'Seats', border=1)
    pdf.cell(0, 10, '', ln=True)  # End of header

    # Add rows for each patron
    pdf.set_font('Arial', '', 12)
    for index, row in report.iterrows():
        name = f"{row['Last Name']}, {row['First Name']}"
        tickets = row['Tickets_Ordered']
        seats = row['Seats']
        pdf.add_table_row(name, tickets, seats)
    
    # Return the PDF as binary data
    return bytes(pdf.output(dest='S'))

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
            st.download_button(
                label="📥 Download Check-in List as PDF",
                data=pdf,
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
