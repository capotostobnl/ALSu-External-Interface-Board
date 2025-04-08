"""This module is the main module for testing ALSu
External Interface Board Modules.

M. Capotosto
3/21/2025
NSLS-II Diagnostics and Instrumentation"""

import csv
import sys
import os
from datetime import datetime
from time import sleep
from pylogix import PLC
from report_generator import plot_pdf
from instrument_modules.keithley_2100 import Keithley2100


OUTx_PSC_FAIL_THRES_OFF = 4.5  # Make sure output is >4.5V
INx_PSC_FAIL_THRES_OFF = 0.2  # Make sure output is <100mV

OUTx_PSC_FAIL_THRES_ON = 0.3  # Make sure output is <= 300mV
INx_PSC_FAIL_THRES_ON = 18  # Make sure input is >15VDC

# *************************************************************************
# ******Set Insturment IP Addresses******

PLC_IP_ADDRESS = "10.0.142.100"  # Set PLC IP Address here
DMM_ADDRESS = "USB0::0x05E6::0x2100::8020356::INSTR"
# *************************************************************************

# *************************************************************************
# ******Create Instrument Objects******
plc = PLC()
plc.IPAddress = '10.0.142.100'
dmm = Keithley2100(connection_method="USB", address=DMM_ADDRESS)
# *************************************************************************

# *************************************************************************
# ******Initialize Date/Time Names for Test Instance******
# ******Create directory structures for Test Data Storage******


def get_current_datetime():
    """Get formatted date/time"""
    dir_create_time = datetime.now()
    dir_time_formatted = dir_create_time.strftime("%m-%d-%y_%H-%M-%S")
    report_date_formatted = dir_create_time.strftime("%m/%d/%y")
    report_time_formatted_l = dir_create_time.strftime("%I:%M %p")

    return dir_create_time, dir_time_formatted, report_date_formatted, \
        report_time_formatted_l


def create_test_directories(eib_sn, dir_time_formatted):
    """Create any missing parent directories, make new eib directory,
    raw data subdirectories"""
    # Define paths
    report_path = os.path.join("Test_Data", f"eib_{eib_sn}-"
                               f"{dir_time_formatted}",
                               f"eib_{eib_sn}_Report.pdf")
    raw_data_path = f"./Test_Data/eib_{eib_sn}-{dir_time_formatted}/raw_data"

    # Create parent directories for report and raw data paths (not including
    # the file name)
    report_dir = os.path.dirname(report_path)
    os.makedirs(report_dir, exist_ok=True)

    # Create the raw_data directory
    os.makedirs(raw_data_path, exist_ok=True)

    return report_path, raw_data_path
# *************************************************************************

# *************************************************************************
# ******Acquire Test Technician Names...******
# ******Acquire eib Information......******


def get_test_tech_info():
    """Acquire static test technician information"""
    while True:
        tester_name = input("Enter your name: ")
        tester_life = input("Enter your Life #: ")

        if input(f"You entered: {tester_name}, {tester_life},"
                 f" is this correct? <Y/N>: ") in ("Y", "y"):
            return tester_name, tester_life


def save_test_tech_info():
    """Save test technician demographics to file"""
    # **********************************************************************************
    # Save test data to file...
    # **********************************************************************************

    file_path_l = os.path.join(raw_data_path, f"{EIB_sn}_Technician_Data.csv")

    data = [
        ["tester_name", "tester_life"],
        [tester_name, tester_life]
    ]

    try:
        # Open the file in write mode (will create the file if it
        # doesn't exist)
        with open(file_path_l, mode='w', newline='', encoding='utf-8') \
                as file_l:
            writer = csv.writer(file_l)

            # Write the header and the data rows
            writer.writerows(data)

        print(f"Tester data saved to: {file_path_l}")

    except Exception as e:
        print(f"Error writing to {file_path_l}: {e}")


def get_EIB_info():
    """Acquire eib Serial No./Type Information"""
    while True:
        EIB_sn = input("Enter EIB S/N: ")
        if input(f"You entered: {EIB_sn}, is this correct? <Y/N>: ") \
                in ("Y", "y"):
            dir_create_time, dir_time_formatted, report_date_formatted, \
                report_time_formatted = get_current_datetime()
            # Create test data directories
            report_path, raw_data_path = create_test_directories(
                EIB_sn, dir_time_formatted
            )

            file_path_l = os.path.join(raw_data_path, f"{EIB_sn}_"
                                       "raw_label.csv")
            data = [EIB_sn]

            try:
                # Open the file in write mode (will create the file if
                # it doesn't exist)
                with open(file_path_l, mode='w', newline='', encoding='utf-8')\
                        as file_l:
                    writer = csv.writer(file_l)

                    # Write the header and the data rows
                    writer.writerows(data)

                print(f"Tester data saved to: {file_path_l}")

            except Exception as e:
                print(f"Error writing to {file_path_l}: {e}")
        return EIB_sn, dir_create_time, dir_time_formatted, \
            report_date_formatted, report_time_formatted, \
            report_path, raw_data_path


# *************************************************************************

def save_EIB_test_data(io_voltage_op_off, io_voltage_op_on, Visual_LED_PassFail, raw_data_path,
                        EIB_sn):
    """Call the run_EIB_test function."""
    # **********************************************************************************
    # Save raw data to file...
    file_path = os.path.join(raw_data_path, f"{EIB_sn}_Voltages.csv")

    try:
        # Open the file in write mode and automatically close when the block
        # is finished
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write header
            writer.writerow(["Channel", "Voltage (OFF)", "Voltage (ON)", "Visual LED Pass/Fail"])

            # Write row data
            for chan, (off, on) in enumerate(zip(io_voltage_op_off,
                                                io_voltage_op_on)):
                writer.writerow([chan, off, on, Visual_LED_PassFail])

            print(f"Data saved successfully to {file_path}")

    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
# *************************************************************************

# **********************************************************************************
# ******PLC Initialization******
# **********************************************************************************


def plc_init():
    """Initialize PLC to all outputs OFF"""
    # Disable input and enable DMM for the channel
    plc.Write("CR0", 0)
    for chan in range(16):
        plc.Write(f"DO1_{chan}", 0)
        plc.Write(f"DO2_{chan}", 0)
        sleep(0.5)
# **********************************************************************************


# **********************************************************************************
# ******Functional Tests******
# **********************************************************************************


def pwr_led_test():
    D34_D35_LED_Check = input("Check D34, D35 for +24V and +5V supplies, both "
                              "should now be illuminated. Are they? <Y/N>: ")
    if D34_D35_LED_Check not in ("Y", "y", "N", "n"):
        print("Invalid entry. Try again...")
        pwr_led_test()
    elif D34_D35_LED_Check in ("Y", "y"):
        print("Power LED Test Passed! Continuing...")
        return True
    elif D34_D35_LED_Check in ("N", "n"):
        print("Power LED Test FAILED! Continuing...")
        return False


def io_test():
    io_voltage_op_off = []  # Voltage with output OFF
    io_voltage_op_on = []  # Voltage with output ON
    chan = 0

    # Loop through channels 0 to 7
    for chan in range(8):

        # Disable input and enable DMM for the channel
        plc.Write(f"DO1_{chan}", 0)
        plc.Write(f"DO2_{chan}", 1)
        sleep(0.5)

        # Take output OFF voltage measurement
        io_voltage_op_off.append(round(dmm.meas_dcv(), 3))

        # Enable input and DMM for the channel
        plc.Write(f"DO1_{chan}", 1)
        plc.Write(f"DO2_{chan}", 1)
        sleep(0.5)

        # Take output ON voltage measurement
        voltage = dmm.meas_dcv()
        sleep(0.2)
        io_voltage_op_on.append(round(voltage, 3))
        sleep(2)

        # Disable input and DMM for the channel
        plc.Write(f"DO1_{chan}", 0)
        plc.Write(f"DO2_{chan}", 0)
        sleep(0.5)

    # Measure 24VDC passthrough on TB4 (channel 8)
    chan = 8
    plc.Write(f"DO1_{chan}", 0)
    plc.Write(f"DO2_{chan}", 1)
    sleep(0.5)
    # Take output OFF voltage measurement
    voltage = dmm.meas_dcv()
    sleep(0.2)
    io_voltage_op_on.append(round(voltage, 3))
    io_voltage_op_off.append(0)

    # Shut off the measurement relay output now...
    plc.Write(f"DO2_{chan}", 0)
    sleep(0.5)

    return io_voltage_op_off, io_voltage_op_on
# *************************************************************************


# **********************************************************************************
# ******Pass/Fail Result tabulation******
# **********************************************************************************
def io_tabulate_results(io_voltage_op_off, io_voltage_op_on, Visual_LED_PassFail):
    io_op_off_results = [False] * 8
    io_op_on_results = [False] * 9
    # Check output OFF Values
    for i in range(4):
        if io_voltage_op_off[i] >= OUTx_PSC_FAIL_THRES_OFF:
            # For J1-6 to J1-9 OFF, TB1-1, 5 TB2-1, 5 should be >=4.5V
            io_op_off_results[i] = True
        else:
            io_op_off_results[i] = False  # Failed!

    for i in range(4, 8):
        if io_voltage_op_off[i] <= INx_PSC_FAIL_THRES_OFF:
            # For TB1-3, 7, TB2-3, 7 OFF, RD1-4 should be 0V - 4k4 pulldown!
            io_op_off_results[i] = True
        else:
            io_op_off_results[i] = False  # Failed!

    # Check output ON values
    for i in range(4):
        if io_voltage_op_on[i] <= OUTx_PSC_FAIL_THRES_ON:
            # For J1-6 to J1-9 ON, TB1-1, 5 TB2-1, 5 should be SHORTED (Near 0V)
            io_op_on_results[i] = True
        else:
            io_op_on_results[i] = False  # Failed!

    for i in range(4, 8):
        if io_voltage_op_on[i] >= INx_PSC_FAIL_THRES_ON:
            io_op_on_results[i] = True
        else:
            io_op_on_results[i] = False  # Failed!

    # Check 24V PSU
    if io_voltage_op_on[8] >= 23:
        # If 24V PS Passthrough is >= 23V
        io_op_on_results[8] = True
    else:
        io_op_on_results[8] = False  # Fail!

    # For Channnels 0 to 3:
    # OB16-0-3, TO OUT(1-4)-PSC
    # J1-6 TO J1-9 >> TB1-1, 1-5, 2-1, 2-5
    # Into J1-(6-9) Drive 0V = Fail = LED OFF
    # TB1-1 should be 4.5V (FAILED), LED OFF
    # For Channels 4 to 7:
    # IN(1-4)-PSC TO IB16-(0-4)
    # J1-1 TO J1-4 >> TB1-3, 1-7, 2-3, 2-7
    # Into TB1-3, 1-7, 2-3, 2-7:
    # Drive 0V FAILED = LED OFF
    # Measure J1-1, 1-2, 1-3, 1-4 FAILED = 0V

    # Into J1-(6-9) Drive 24V = Pass = LED ON
    # TB1-1 should be 0.3V or less, LED ON

    # FOR ON: DRIVE 5V into TB1-3, 7, 2-3, 7
    # Measure J1-1, 2, 3, 4, OK = 24V = LED ON

    # Determine overall test pass/fail
    overall_test_passfail = (
        all(io_op_off_results[:4]) and  # Check first 4 for OFF values
        all(io_op_off_results[4:8]) and  # Check next 4 for OFF values
        all(io_op_on_results[:4]) and  # Check first 4 for ON values
        all(io_op_on_results[4:8]) and  # Check next 4 for ON values
        io_op_on_results[8]  and # Check 24V PSU test
        Visual_LED_PassFail  # Check LEDs light sequentially and correctly. 
    )

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

        "24V_PS": (io_voltage_op_on[8], io_op_on_results[8]),

        "Visual_LED": (Visual_LED_PassFail, Visual_LED_PassFail)
    }
    return overall_test_passfail, test_data
# *************************************************************************

# *************************************************************************
# ******Generate Report Dictionaries/Dataset...******
# *************************************************************************


def generate_report_dataset(EIB_sn, tester_name, tester_life,
                            report_date_formatted, test_data,
                            overall_test_passfail, Visual_LED_PassFail):
    """Generate data dictionary for the report_generator.py module"""
    dut_info_l = {
        "Title": f"External Interface Board Test Results<br/>"
                 f"for  EIB S/N: {EIB_sn}",
        "Technician": f"{tester_name}",
        "Life": f"{tester_life}",
        "EIB_sn": f"{EIB_sn}",
        "Date": f"{report_date_formatted}",
        "Time": f"{report_time_formatted}",
        "TestData": test_data,
        "overall_test_passfail": overall_test_passfail,
        "Visual_LED_PassFail": Visual_LED_PassFail
    }
    return dut_info_l

# *************************************************************************
# ******Carry out the testing...******
# *************************************************************************


tester_name, tester_life = get_test_tech_info()  # Get test technician info

EIB_sn, dir_create_time, dir_time_formatted, report_date_formatted, \
        report_time_formatted, report_path, raw_data_path \
        = get_EIB_info()  # Get EIB S/N

# Record the time at the start of the test for reporting, file \
# naming purposes.
print("Test data directories created...")
save_test_tech_info()  # Save technician data to the new test directory...
print("Initialzing PLC...")
plc_init()  # Initialize the PLC


input("Ensure JP1, JP2, JP3, JP4, and F1 are installed as directed.")
input("Ensure TB1-4, and J1 are connected.")
input("Press return when ready for Power ON...")
plc.Write('CR0', 1)  # Enable +24V, +5V PSUs
sleep(0.5)
pwr_led_test_result = pwr_led_test()
# Initial power on test, check +24V and +5V LEDs

input("When ready to begin, monitor LEDs for each channel. They should \
      illuminate in pairs - D3 and D7, then D2 and D11, and so on. They \
      will illuminate for 2 seconds each. Press return when ready to \
      continue.")

io_voltage_op_off, io_voltage_op_on = io_test()  # I/O Test
# Generate pass/fail results
LEDTest = input("Did all LEDs light properly and in sequence? <Y/N>")
if LEDTest in ("Y", "y"):
    Visual_LED_PassFail = True
else:
    Visual_LED_PassFail = False
overall_test_passfail, test_data = io_tabulate_results(io_voltage_op_off, io_voltage_op_on, Visual_LED_PassFail)

save_EIB_test_data(io_voltage_op_off, io_voltage_op_on, Visual_LED_PassFail, raw_data_path, EIB_sn)
# Save test data to raw file


plc.Write('CR0', 0)  # Disable +24V, +5V PSUs
sleep(0.5)
plc.Close()

# *************************************************************************
# ******Generate Report...******
print("Generating Report...")
dut_info = generate_report_dataset(EIB_sn, tester_name, tester_life,
                                   report_date_formatted, test_data,
                                   overall_test_passfail, Visual_LED_PassFail)
plot_pdf(dut_info, report_path)
os.startfile(report_path)

print("Exiting...")
sleep(5)
sys.exit(0)
