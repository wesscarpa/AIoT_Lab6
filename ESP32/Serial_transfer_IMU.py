import serial
idx = input("Enter the index of the IMU data file to save (e.g., 0, 1, 2): ")
filename = f"ESP_IMU_Data/IMU_data_{idx}.txt"
ser = serial.Serial("COM3", 115200, timeout=5)   # change port
with open(filename, "w") as f:
    for _ in range(129):                          # header + 128 rows
        f.write(ser.readline().decode().strip() + "\n")