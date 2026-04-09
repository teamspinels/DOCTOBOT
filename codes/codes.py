import serial
import time
import sys

# Port detected from your 'ls' command
PORT = '/dev/ttyACM1'
BAUD = 9600

def get_temp(ser):
    # 1. Clear the buffer of any old data
    ser.reset_input_buffer()
    
    # 2. Send the Request signal
    ser.write(b'R')
    
    # 3. Read the response
    line = ser.readline().decode('utf-8').strip()
    return line

try:
    # Open serial with a 2-second timeout
    ser = serial.Serial(PORT, BAUD, timeout=2)
    
    # IMPORTANT: The Mega resets when the serial port opens. 
    # We must wait for it to finish booting.
    print("Initializing Mega...")
    time.sleep(3) 
    
    print(f"Connected to {PORT} successfully.")
    print("Commands: [Enter] = Get Temp, [q] = Quit")

    while True:
        cmd = input(">> ").lower()
        
        if cmd == 'q':
            break
            
        data = get_temp(ser)
        
        if data and ',' in data:
            try:
                ambient, obj = data.split(',')
                print(f"  [+] Ambient: {ambient}°C")
                print(f"  [+] Object:  {obj}°C")
            except ValueError:
                print(f"  [!] Data mismatch: {data}")
        else:
            print("  [!] Error: No data received or sensor not ready.")

except serial.SerialException as e:
    print(f"Check connection: {e}")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial closed.")
