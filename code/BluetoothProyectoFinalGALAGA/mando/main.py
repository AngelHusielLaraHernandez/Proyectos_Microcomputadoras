import uasyncio as asyncio
import aioble
import bluetooth
import struct
import gc  
from machine import Pin, I2C
from imu import MPU6050

_SERVICE_UUID = bluetooth.UUID("12345678-1234-1234-1234-123456789abc")
_CHAR_UUID = bluetooth.UUID("87654321-4321-4321-4321-cba987654321")

_service = aioble.Service(_SERVICE_UUID)
_char = aioble.Characteristic(_service, _CHAR_UUID, read=True, notify=True)
aioble.register_services(_service)

i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)
imu = MPU6050(i2c)

btn_fire = Pin(4, Pin.IN, Pin.PULL_UP)
btn_pause = Pin(5, Pin.IN, Pin.PULL_UP)

async def peripheral_task():
    while True:
        try:
            connection = await aioble.advertise(
                250_000, 
                name="PicoMando", 
                services=[_SERVICE_UUID]
            )
            print("conectada")

            while connection.is_connected():
                ax = imu.accel.x
                ay = imu.accel.y
                
                fire_pressed = (btn_fire.value() == 0)
                pause_pressed = (btn_pause.value() == 0)

                payload = struct.pack('<ffbb', ax, ay, int(fire_pressed), int(pause_pressed))
                _char.write(payload)
                
                try:
                    await _char.notify(connection)
                except Exception:
                    pass 
                
                gc.collect() 
                
                await asyncio.sleep_ms(10) 
                
            print("La Consola se ha desconectado.")
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print("Error general:", e)
            await asyncio.sleep_ms(1000)

async def main():
    await asyncio.gather(peripheral_task())

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Mando apagado.")
