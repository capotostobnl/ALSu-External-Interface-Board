# flake8: noqa E501
"""This module manages ReportLab Report Generation
for External Interface Board Testing

M. Capotosto
3/25/2025
NSLS-II Diagnostics and Instrumentation
"""
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, \
    Paragraph, Image, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color
from reportlab.lib import colors


PAGE_WIDTH, PAGE_HEIGHT = letter  # Page size!
styles = getSampleStyleSheet()


def plot_pdf(dut_info, report_path):
    """Generate the PDF using data from the dictionary and save it to the
    provided report path."""
    # Create the document object
    print(report_path)
    doc = SimpleDocTemplate(report_path, pagesize=letter)

    # Create a Story list to hold the content
    Story = []
#############################################################################
# ******Paragraph Styles******
#############################################################################
    # Define the title style (24pt font, centered)
    title_style = ParagraphStyle(
        "TitleStyle",
        fontName="Helvetica-Bold",  # Font name
        fontSize=18,                # Font size
        leading=22,                 # Paragraph spacing
        alignment=1,                # Center the title
        spaceAfter=12               # Space after the title
    )

    # Define the Name Subheading Style
    name_style = ParagraphStyle(
        "NameStyle",
        fontName="Helvetica-Bold",  # Font name
        fontSize=12,                # Font size
        alignment=0,                # Center the title
        leading=12,               # Line spacing on CR
        spaceAfter=12               # Space after the title
    )

    # Title style for the table (size 14, left-aligned)
    table_title_style = ParagraphStyle(
        "TableTitleStyle",
        fontName="Helvetica",
        fontSize=14,
        alignment=1,  # Centered
        spaceAfter=6,
        textColor=colors.black
    )

    # Create a custom style for bold and colored text
    bold_green = ParagraphStyle(
        "BoldGreen",
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=0,
        spaceAfter=6,
        textColor=colors.green,
    )

    bold_red = ParagraphStyle(
        "BoldRed",
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=0,
        spaceAfter=6,
        textColor=colors.red,
    )
#############################################################################

#############################################################################
# ******Titles and Subheadings******
#############################################################################
    # Create the title paragraph
    title = Paragraph(dut_info["Title"], title_style)

    # Add title to the story
    Story.append(title)

    # Add space after the title
    Story.append(Spacer(1, 0.3*inch))  # Adds space after title

    # Add Pass/Fail Status
    if dut_info['overall_test_passfail']:
        Story.append(Paragraph("Overall Test Status: Passed!", bold_green))
    else: 
        Story.append(Paragraph("Overall Test Status: Failed!", bold_red))
    # Add other details (Technician, Life, Date, Time)
    Story.append(Paragraph(f"Technician: {dut_info['Technician']}, \
                           Life #: {dut_info['Life']}", name_style))
    Story.append(Paragraph(f"Test performed: {dut_info['Date']}, \
                            {dut_info['Time']}", name_style))

#############################################################################


# Add space before the table title
    Story.append(Spacer(1, 18))

    # Add the table title
    table_title = Paragraph("PSC I/O and MPS 5069 PLC I/O Test Results",
                            table_title_style)
    Story.append(table_title)

    # Add space after the table title
    Story.append(Spacer(1, 12))

    # Add Visual LED Test Statuts
    if dut_info['Visual_LED_PassFail']:
        Story.append(Paragraph("<para align='center'>Visual LED Status Test: Passed!</para>", bold_green))
    else: 
        Story.append(Paragraph("<para align='center'>Visual LED Status Test: Failed!</para>", bold_red))    

    # Prepare table data with headers
    # Output OFF Test Results Table
    output_data = [
        ["I/O Port", "Voltage", "Pass/Fail"]
    ]
    for io_port, (voltage, result) in dut_info['TestData'].items():
        if io_port == "Visual_LED": continue  # Skip "Visual_LED"
        if result:
            output_data.append([io_port, f"{voltage} V", "Pass"])
        else:
            output_data.append([io_port, f"{voltage} V", "Fail"])


    # Add the tables to the Story
    Story.append(Spacer(1, 12))

    # Style for tables
    table_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header bg color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center text
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
        ('BACKGROUND', (1, 1), (-1, -1), colors.white),  # Default row bg
    ])

    # Define colors with transparency
    red = Color(1, 0, 0, alpha=0.5)  # Red (Fail)
    green = Color(0, 1, 0, alpha=0.5)  # Green (Pass)

    # Output OFF Table
    output_table = Table(output_data)

    # Define row styles in a list to apply later
    row_styles = []

    # Loop through rows (skip header) to apply background color
    for row_idx, row in enumerate(output_data[1:], start=1):  # Skip header
        status = row[2]  # Get "Status" value (Pass/Fail)
        
        # Apply the color for the entire row (start from column 0 to last column)
        if status == "Fail":
            row_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), red))  # Red background for "Fail"
        elif status == "Pass":
            row_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), green))  # Green background for "Pass"

    # Add row styles to table
    output_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header bg color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center text
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
        ('BACKGROUND', (1, 1), (-1, -1), colors.white),  # Default row bg
    ] + row_styles))  # Add dynamic row background styles

    Story.append(output_table)
    Story.append(Spacer(1, 12))

#############################################################################
# ******Build the PDF******
#############################################################################
    # Build the document (this automatically handles page creation)
    doc.build(Story)
#############################################################################

if __name__ == "__main__":
    import os
    # Sample test data for the report


    OUTx_PSC_FAIL_THRES_OFF = 4.5  # Make sure output is >4.5V
    INx_PSC_FAIL_THRES_OFF = 0.1  # Make sure output is <100mV

    OUTx_PSC_FAIL_THRES_ON = 0.3  # Make sure output is <= 300mV
    INx_PSC_FAIL_THRES_ON = 15  # Make sure input is >15VDC

    io_voltage_op_off = [5.0, 0.0, 3.3, 4.0, 1.2, 6, 7, 8]  # Voltage values for output OFF test (in volts)
    io_voltage_op_on = [5.0, 5.1, 0.0, 4.8, 4.9, 3, 8, 9, 7]  # Voltage values for output ON test (in volts)
    io_op_off_results = [False] * len(io_voltage_op_off)
    io_op_on_results = [False] * len(io_voltage_op_on)

    # Check output OFF Values
    for i in range(4):
        if io_voltage_op_off[i] >= OUTx_PSC_FAIL_THRES_OFF:
            # For J1-6 to J1-9 OFF, TB1-1, 5 TB2-1, 5 should be >=4.5V
            io_op_off_results[i] = True 
        else:
            io_op_off_results[i] = False  # Failed!

    for i in range(4, 8):
        if io_voltage_op_off[i] <= INx_PSC_FAIL_THRES_OFF:
            io_op_off_results[i] = True  
        else:
            io_op_off_results[i] = False  # Failed!

    # Check output ON values
    for i in range(4):
        if io_voltage_op_on[i] >= OUTx_PSC_FAIL_THRES_ON:
            # For J1-6 to J1-9 OFF, TB1-1, 5 TB2-1, 5 should be >=4.5V
            io_op_on_results[i] = True
        else:
            io_op_on_results[i] = False  # Failed!

    for i in range(4, 8):
        if io_voltage_op_on[i] <= INx_PSC_FAIL_THRES_ON:
            io_op_on_results[i] = True
        else:
            io_op_on_results[i] = False  # Failed!

    # Check 24V PSU
    if io_voltage_op_on[8] >= 23:
        # If 24V PS Passthrough is >= 23V
        io_op_on_results[8] = True
    else:
        io_op_on_results[8] = False  # Fail!

    test_data = {
        "OUT1-PSC OFF": (io_voltage_op_off[0], io_op_off_results[0]),
        "OUT1-PSC ON": (io_voltage_op_on[0], io_op_on_results[0]),
        "OUT2-PSC OFF": (io_voltage_op_off[1], io_op_off_results[1]),
        "OUT2-PSC ON": (io_voltage_op_on[1], io_op_on_results[1]),
        "OUT3-PSC OFF": (io_voltage_op_off[2], io_op_off_results[2]),
        "OUT3-PSC ON": (io_voltage_op_on[2], io_op_on_results[2]),
        "OUT4-PSC OFF": (io_voltage_op_off[3], io_op_off_results[3]),
        "OUT4-PSC ON": (io_voltage_op_on[3], io_op_on_results[3]),

        "IN1-PSC OFF": (io_voltage_op_off[4], io_op_off_results[4]),
        "IN1-PSC ON": (io_voltage_op_on[4], io_op_on_results[4]),
        "IN2-PSC OFF": (io_voltage_op_off[5], io_op_off_results[5]),
        "IN2-PSC ON": (io_voltage_op_on[5], io_op_on_results[5]),
        "IN3-PSC OFF": (io_voltage_op_off[6], io_op_off_results[6]),
        "IN3-PSC ON": (io_voltage_op_on[6], io_op_on_results[6]),
        "IN4-PSC OFF": (io_voltage_op_off[7], io_op_off_results[7]),
        "IN4-PSC ON": (io_voltage_op_on[7], io_op_on_results[7]),

        "24V_PS": (io_voltage_op_on[8], io_op_on_results[8])
    }

    dut_info = {
        "Title": "Test Report for PSC I/O and MPS 5069 PLC I/O",
        "Technician": "John Doe",
        "Life": "12345",
        "Date": "2025-03-24",
        "Time": "14:30",
        "overall_test_passfail": False,  # True means the test passed
        "TestData": test_data,
        "io_op_off_results": [True, False, True, True, False],  # Pass/Fail results for output OFF test
        "io_op_on_results": [True, True, False, True, True],  # Pass/Fail results for output ON test

    }


    # Path where the generated report will be saved
    report_path = "test_report.pdf"

    # Call the function to generate the PDF report
    plot_pdf(dut_info, report_path)
    os.startfile(report_path)

    print(f"Test report has been generated and saved as {report_path}.")