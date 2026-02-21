# import csv 

# crc_poly = "0x4599"

# def crc(bitstream,crc_poly):
#     divisor = list("1"+ f"{int(crc_poly,16):015b}")
#     padded_stream = list(bitstream + "0" * 15)
#     # The XOR Long Division Loop
#     for i in range(len(bitstream)):
#         # If the leading bit is 1, we XOR the divisor against the current window
#         if padded_stream[i] == '1':
#             for j in range(16):
#                 # Python XOR logic for characters: Same = '0', Different = '1'
#                 if padded_stream[i + j] == divisor[j]:
#                     padded_stream[i + j] = '0'
#                 else:
#                     padded_stream[i + j] = '1'
#     # extracting the remainder 
#     remainder_bin = "".join(padded_stream[-15:])
    
#     # Convert binary string back to an integer
#     return hex(int(remainder_bin, 2))[2:]

# with open("can_frames.csv", mode="r", newline="", encoding="utf-8") as can_frames_file:
#     can_frames = csv.reader(can_frames_file)
#     header = next(can_frames) # skip header
    
#     for frame in can_frames:
#         # 1. Force ID to 11 bits
#         id_val = int(frame[1], 16)
#         bin_id = f"{id_val:011b}"
        
#         # Extract IDE and RTR (assuming they are strings '0' or '1' in CSV)
#         ide = frame[2]
#         rtr = frame[3]
        
#         # 2. Force DLC to 4 bits
#         dlc_val = int(frame[4])
#         bin_dlc = f"{dlc_val:04b}"
        
#         # 3. Force each data byte to 8 bits and join them
#         data_bytes = frame[5].split()
#         data_bytes_no = len(data_bytes)
#         bin_data = "".join([f"{int(x, 16):08b}" for x in data_bytes])
        
#         # 4. Assemble the full bitstream (Adding SOF and r0)
#         sof = "0"
#         r0 = "0"
#         full_frame = sof + bin_id + rtr + ide + r0 + bin_dlc + bin_data
        
#         crc_val = frame[6]
#         # print(full_frame)
#         if(id_val <= 2**(11)-1):
#             print(f"ID: {id_val} | Bitstream Length: {len(full_frame)} bits")
#             if(dlc_val != data_bytes_no):
#                 print("invalid dlc")
#                 continue
#             else:
#                 crc_calc = crc(full_frame,crc_poly)
#                 if crc_calc == crc_val:
#                     print("valid frame")
#                 else :
#                     print("invalid frame")
#         else:
#             print("invalid id")



import csv

crc_poly = "0x4599"

def crc(bitstream, crc_poly):
    divisor = list("1" + f"{int(crc_poly,16):015b}")
    padded_stream = list(bitstream + "0" * 15)
    for i in range(len(bitstream)):
        if padded_stream[i] == '1':
            for j in range(16):
                if padded_stream[i + j] == divisor[j]:
                    padded_stream[i + j] = '0'
                else:
                    padded_stream[i + j] = '1'
    remainder_bin = "".join(padded_stream[-15:])
    return hex(int(remainder_bin, 2))[2:]

# Read input and write output
with open("can_frames.csv", mode="r", newline="", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)  # skip header

    # Add a new column for validation status
    out_fieldnames = header + ["status"]

    with open("validated_frames.csv", mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(out_fieldnames)

        for frame in reader:
            id_val = int(frame[1], 16)
            bin_id = f"{id_val:011b}"
            ide = frame[2]
            rtr = frame[3]
            dlc_val = int(frame[4])
            bin_dlc = f"{dlc_val:04b}"
            data_bytes = frame[5].split()
            data_bytes_no = len(data_bytes)
            bin_data = "".join([f"{int(x, 16):08b}" for x in data_bytes])
            sof = "0"
            r0 = "0"
            full_frame = sof + bin_id + rtr + ide + r0 + bin_dlc + bin_data
            crc_val = frame[6]

            # Validation logic
            if id_val > 2**11 - 1:
                status = "invalid id"
            elif dlc_val != data_bytes_no:
                status = "invalid dlc"
            else:
                crc_calc = crc(full_frame, crc_poly)
                status = "valid frame" if crc_calc == crc_val else "invalid frame"

            # Write original row + status
            writer.writerow(frame + [status])