import csv

# CAN CRC-15 polynomial
CRC_POLY = 0x4599

def apply_bit_stuffing(bitstream):
    """Apply CAN bit stuffing: after 5 consecutive identical bits, insert opposite bit."""
    if not bitstream:
        return ""
        
    stuffed = []
    count = 1
    prev = bitstream[0]
    stuffed.append(prev)

    for bit in bitstream[1:]:
        if bit == prev:
            count += 1
            stuffed.append(bit)
            if count == 5:
                stuffed.append('0' if bit == '1' else '1')
                count = 0
        else:
            count = 1
            stuffed.append(bit)
        prev = bit

    return "".join(stuffed)

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

with open("can_frames.csv", mode="r", newline="", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader)  # skip header

    for frame in reader:
        errors = []

        # Parse ID
        id_val = int(frame[1], 16)
        bin_id = f"{id_val:011b}"

        ide = frame[2]
        rtr = frame[3]

        # DLC
        dlc_val = int(frame[4])
        bin_dlc = f"{dlc_val:04b}"

        # Data field
        data_bytes = frame[5].split() if frame[5] else []
        data_bytes_no = len(data_bytes)
        bin_data = "".join([f"{int(x, 16):08b}" for x in data_bytes])

        # Assemble the unstuffed bitstream for CRC calculation
        # It must include SOF (0) and r0 (0)
        sof = "0"
        r0 = "0"
        full_frame = sof + bin_id + rtr + ide + r0 + bin_dlc + bin_data

        # Apply bit stuffing
        stuffed_frame = apply_bit_stuffing(full_frame)

        # Given CRC
        crc_val_int = int(frame[6], 16)

        # Validation
        if id_val > 2**11 - 1:
            errors.append("bad_id")
            
        # The CAN standard max data length is 8 bytes
        if dlc_val > 8:
            errors.append("bad_dlc")
        elif dlc_val != data_bytes_no:
            errors.append("mismatch_of_dlc_and_data_frame")
        else:
            # Calculate CRC on the UN-STUFFED full_frame
            crc_calc = crc(full_frame, CRC_POLY)
            if crc_calc != crc_val_int:
                errors.append("bad_crc")

        success = "success" if not errors else "failure"
        error_str = ", ".join(errors) if errors else "none"

        # Print formatted output exactly as requested
        print(f"{frame[0]} can frame check is {success} | error: {error_str} | given error is {frame[7]}")