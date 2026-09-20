# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
import numpy as np
cimport numpy as np
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from libc.math cimport log2
import time

ctypedef unsigned char uint8_t
ctypedef unsigned int uint32_t

DEF WINDOW_SIZE = 4096
DEF LOOKAHEAD_BUFFER_SIZE = 64
DEF MIN_MATCH_LENGTH = 3
DEF MAX_MATCH_LENGTH = 258


cdef inline uint32_t hash_function(uint8_t* data, int pos) nogil:
    cdef uint32_t hash_val = (data[pos] << 16) | (data[pos + 1] << 8) | data[pos + 2]
    return hash_val % WINDOW_SIZE


cdef (int, int) find_longest_match(uint8_t* data, int current_position, int data_length) nogil:
    cdef int max_match_length = 0
    cdef int match_position = 0
    cdef int window_start = max(0, current_position - WINDOW_SIZE)
    cdef int lookahead_end = min(current_position + LOOKAHEAD_BUFFER_SIZE, data_length)
    cdef int i, j, match_length

    for i in range(window_start, current_position):
        match_length = 0
        while (current_position + match_length < lookahead_end and
               data[i + match_length] == data[current_position + match_length] and
               match_length < MAX_MATCH_LENGTH):
            match_length += 1

        if match_length > max_match_length and match_length >= MIN_MATCH_LENGTH:
            max_match_length = match_length
            match_position = i

    return match_position, max_match_length


def compress(bytes input_data):
    cdef np.ndarray[uint8_t, ndim=1] data = np.frombuffer(input_data, dtype=np.uint8)
    cdef int data_length = len(data)
    cdef uint8_t* data_ptr = &data[0]

    cdef np.ndarray[uint8_t, ndim=1] output = np.zeros(data_length * 2, dtype=np.uint8)
    cdef uint8_t* output_ptr = &output[0]
    cdef int output_size = 0

    cdef int position = 0
    cdef int offset, length
    cdef double start_time = time.time()

    while position < data_length:
        if position + MIN_MATCH_LENGTH <= data_length:
            offset, length = find_longest_match(data_ptr, position, data_length)
        else:
            length = 0

        if length >= MIN_MATCH_LENGTH:
            # Match: flag=1, 2-byte offset, 1-byte length
            output[output_size] = 1
            output_size += 1
            output[output_size] = (position - offset) >> 8
            output[output_size + 1] = (position - offset) & 0xFF
            output_size += 2
            output[output_size] = length
            output_size += 1
            position += length
        else:
            # Literal: flag=0, byte
            output[output_size] = 0
            output_size += 1
            output[output_size] = data[position]
            output_size += 1
            position += 1

    cdef double end_time = time.time()
    cdef double compression_time = end_time - start_time
    cdef double original_size_mb = data_length / (1024.0 * 1024.0)
    cdef double compression_ratio = data_length / float(output_size) if output_size > 0 else 0
    cdef double compression_factor = output_size / float(data_length) if data_length > 0 else 0
    cdef double space_savings = (1.0 - compression_factor) * 100.0
    cdef double bits_per_byte = (output_size * 8.0) / data_length if data_length > 0 else 0
    cdef double compression_throughput = original_size_mb / compression_time if compression_time > 0 else 0

    print(f"Original size: {data_length} bytes")
    print(f"Compressed size: {output_size} bytes")
    print(f"Compression ratio: {compression_ratio:.2f}x")
    print(f"Space savings: {space_savings:.2f}%")
    print(f"Bits per byte: {bits_per_byte:.2f}")
    print(f"Compression time: {compression_time:.4f} seconds")
    print(f"Compression throughput: {compression_throughput:.2f} MB/s")

    return bytes(output[:output_size])


def decompress(bytes compressed_data, int original_size):
    cdef np.ndarray[uint8_t, ndim=1] input_data = np.frombuffer(compressed_data, dtype=np.uint8)
    cdef int input_length = len(input_data)
    cdef uint8_t* input_ptr = &input_data[0]

    cdef np.ndarray[uint8_t, ndim=1] output = np.zeros(original_size, dtype=np.uint8)
    cdef uint8_t* output_ptr = &output[0]

    cdef int input_pos = 0
    cdef int output_pos = 0
    cdef int flag, offset, length, i
    cdef double start_time = time.time()

    while input_pos < input_length and output_pos < original_size:
        flag = input_data[input_pos]
        input_pos += 1

        if flag == 1:
            offset = (input_data[input_pos] << 8) | input_data[input_pos + 1]
            input_pos += 2
            length = input_data[input_pos]
            input_pos += 1

            for i in range(length):
                output[output_pos + i] = output[output_pos - offset + i]
            output_pos += length
        else:
            output[output_pos] = input_data[input_pos]
            input_pos += 1
            output_pos += 1

    cdef double end_time = time.time()
    cdef double decompression_time = end_time - start_time
    cdef double original_size_mb = original_size / (1024.0 * 1024.0)
    cdef double decompression_throughput = (
        original_size_mb / decompression_time if decompression_time > 0 else 0
    )

    print(f"Decompression time: {decompression_time:.4f} seconds")
    print(f"Decompression throughput: {decompression_throughput:.2f} MB/s")

    return bytes(output[:output_pos])
