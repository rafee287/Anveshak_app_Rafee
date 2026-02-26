import serial
import numpy as np
import threading
import time

# CAN CRC-15 polynomial
CRC_POLY = 0x4599

port_sender = "COM30"                                       #"your_port"  
port_receiver = "COM31"                                     #"your_port" 

BYTE_RESET_PROBABLITY = 0.005

def crc(bitstream, poly):
    """Compute CRC-15 remainder for given bitstream using XOR division."""
    # Force the divisor to be 16 bits (Implicit '1' + 15-bit polynomial)
    divisor_str = "1" + f"{poly:015b}"
    divisor = list(divisor_str)
    
    padded_stream = list(bitstream + "0" * 15)

    for i in range(len(bitstream)):
        if padded_stream[i] == '1':
            for j in range(16):
                padded_stream[i + j] = (
                    '0' if padded_stream[i + j] == divisor[j] else '1'
                )

    remainder_bin = "".join(padded_stream[-15:])
    return int(remainder_bin, 2)

def send_data(ser: serial.Serial, data: np.ndarray) -> None:

    data_to_send = data                                         #[40,120,200,255,260,170,100,40,-10,1000]
    bitstream = "".join( f"{b:08b}"for b in data_to_send)
    crc_val = crc(bitstream,CRC_POLY)
    for i in range(len(data_to_send)):
        if np.random.random() < BYTE_RESET_PROBABLITY:
            data_to_send[i] = 0x00

    for i in data_to_send :
        ser.write(bytes([i]))
    ser.write(crc_val.to_bytes(2,'big'))
 
    
def receive_data(ser: serial.Serial) -> tuple[np.ndarray, bool]:
    ser.reset_input_buffer() 
    received_pwm_data = []
    acknowledgement = False
    # data = ser.read(100)
    # received_pwm_data = list(data)
    # if received_pwm_data != [] : acknowledgement = True
    # while True:
    #     if ser.in_waiting >= 1:
    #         data = ser.read(1)
    #         val = data[0]
    #         if(val <= 255 or val>=0):
    #             received_pwm_data.append(data[0])
            
    #         if(len(received_pwm_data) == 100):
    #             #acknowledgement = True

    #             break
    #     else:
    #         pass
    # received_bitstream = "".join(received_pwm_data)
    # crc_cal = crc(received_bitstream)
    # if crc_recieved == crc_cal: acknowledgement = True

    # Receiver side
    while len(received_pwm_data) < 100:
        if ser.in_waiting > 0:
            received_pwm_data.append(ser.read(1)[0])

    # Now read the 2 CRC bytes sent by the sender
    if ser.in_waiting >= 2:
        raw_crc = ser.read(2)
        received_crc_val = int.from_bytes(raw_crc, 'big')

        # Calculate CRC on what we actually got
        bitstream = "".join(f"{b:08b}" for b in received_pwm_data)
        calculated_crc = crc(bitstream, CRC_POLY)

        if calculated_crc == received_crc_val:
            acknowledgement = True 
    
    return received_pwm_data, acknowledgement

def receive_thread_task(received_data: list, no_of_success: int):
    no_of_tries = 0
    try:
        with serial.Serial(port_receiver, 9600, timeout=0.2) as ser:
            while len(received_data) < 100 and no_of_tries < 150:
                print(f"[RECIEVER] [{no_of_tries}] Trying to Recieve Data")

                received_arr, acknowledgement = receive_data(ser)
                
                if np.any(received_arr) or acknowledgement:
                    received_data.append(received_arr)
                    if acknowledgement:
                        print(f"[RECEIVER] [{len(received_data)}] SUCCESS")
                        no_of_success[0] += 1
                    else: 
                        print(f"[RECEIVER] [{len(received_data)}] FAILED")
                no_of_tries += 1
                time.sleep(0.01) 
            else: 
                print(f"[RECEIVER] Time Out")
    except Exception as e:
        print(f"Receiver Thread Error: {e}")

def send_thread_task(all_data):
    try: 
        with serial.Serial(port_sender, 9600) as ser:
            for i, data in enumerate(all_data):
                send_data(ser, data)
                print(f"[SENDER]   packer {i+1}/100 Sent")
                time.sleep(0.3) 
    except Exception as e:
        print(f"Sender Thread Error: {e}")

def generate_pwm():

    pwm = np.random.randint(0, 255, size=(100,))
    return pwm

def main():

    pwm_data = [generate_pwm() for i in range(100)]
    received_data = []
    no_of_success = [0]

    receiver_thread = threading.Thread(target=receive_thread_task, args=(received_data, no_of_success))
    receiver_thread.daemon = True
    receiver_thread.start()

    time.sleep(1)

    sender_thread = threading.Thread(target=send_thread_task, args=(pwm_data,))
    sender_thread.daemon = True
    sender_thread.start()

    time.sleep(1)

    sender_thread.join(timeout=30)
    receiver_thread.join(timeout=30)

    print(f"Total Successful: {no_of_success[0]}/100")

if __name__ == "__main__":
    main()