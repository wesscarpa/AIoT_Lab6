##ONLY ON ESP32

from machine import I2C, Pin
import struct, time

ADXL_ADDR = 0x53                # 0x1D if the ALT ADDRESS pin is tied high
FS        = 50                  # Hz, matches UCI HAR
N_SAMPLES = 128                 # 2.56 s window
PERIOD_US = 1_000_000 // FS
G_PER_LSB = 0.0039             # full-resolution mode: 3.9 mg/LSB (256 LSB/g)

Z_OFFSET = -0.13
Z_SCALE  = 1.0 / 0.97

i2c = I2C(0, scl=Pin(20), sda=Pin(22), freq=400_000)

def imu_init():
    devid = i2c.readfrom_mem(ADXL_ADDR, 0x00, 1)[0]
    assert devid == 0xE5, f"Not an ADXL345 (DEVID=0x{devid:02X}), scan: {i2c.scan()}"
    i2c.writeto_mem(ADXL_ADDR, 0x2C, b'\x09')   # BW_RATE: 50 Hz output data rate
    i2c.writeto_mem(ADXL_ADDR, 0x31, b'\x08')   # DATA_FORMAT: FULL_RES, +/-2 g
    i2c.writeto_mem(ADXL_ADDR, 0x2D, b'\x08')   # POWER_CTL: measurement mode
    time.sleep_ms(100)

def read_accel_g():
    """One reading -> (ax, ay, az) in g, gravity included."""
    raw = i2c.readfrom_mem(ADXL_ADDR, 0x32, 6)
    ax, ay, az = struct.unpack('<hhh', raw)
    return (ax * G_PER_LSB,
            ay * G_PER_LSB,
            (az * G_PER_LSB - Z_OFFSET) * Z_SCALE)
def collect_window():
    """Capture 128 samples at 50 Hz. Returns three lists: xs, ys, zs."""
    xs, ys, zs = [], [], []
    next_t = time.ticks_us()
    for _ in range(N_SAMPLES):
        ax, ay, az = read_accel_g()
        xs.append(ax); ys.append(ay); zs.append(az)
        next_t = time.ticks_add(next_t, PERIOD_US)
        while time.ticks_diff(next_t, time.ticks_us()) > 0:
            pass
    return xs, ys, zs

def save_window(xs, ys, zs, filename="window.txt"):
    with open(filename, "w") as f:
        f.write("ax,ay,az\n")
        for x, y, z in zip(xs, ys, zs):
            f.write(f"{x:.4f},{y:.4f},{z:.4f}\n")

if __name__ == "__main__":
    imu_init()
    t0 = time.ticks_ms()
    xs, ys, zs = collect_window()
    print("capture ms:", time.ticks_diff(time.ticks_ms(), t0))   # expect ~2560
    print("mean x,y,z:", sum(xs)/128, sum(ys)/128, sum(zs)/128)
    save_window(xs, ys, zs)