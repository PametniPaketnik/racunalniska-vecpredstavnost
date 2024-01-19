import math

from PIL import Image
from math import log2
import os
import time
import sys

def read_bmp_image(image_path):
    try:
        img = Image.open(image_path)

        pixel_val = []
        width, height = img.size
        for y in range(height):
            row = []
            for x in range(width):
                row.append(img.getpixel((x, y)))
            pixel_val.append(row)

        return img, pixel_val, width, height, img.mode

    except FileNotFoundError:
        print("File not found!")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_pixel_value(image, x, y):
    if image.mode == 'L':
        return image.getpixel((x, y))

    elif image.mode == 'RGB':
        return image.getpixel((x, y))[0]

def predict(P, X, Y):
    E = []

    for x in range(Y):
        for y in range(X):
            current_val = get_pixel_value(P, x, y)
            value_to_append = P.getpixel((x, y))  # Dodajte to vrstico

            if x == 0 and y == 0:
                pass
            elif y == 0:
                prev_val = get_pixel_value(P, x - 1, 0)
                value_to_append = prev_val - current_val
            elif x == 0:
                prev_val = get_pixel_value(P, 0, y - 1)
                value_to_append = prev_val - current_val
            else:
                val1 = get_pixel_value(P, x - 1, y)
                val2 = get_pixel_value(P, x, y - 1)
                val3 = get_pixel_value(P, x - 1, y - 1)

                max_val = max(val1, val2)
                min_val = min(val1, val2)

                if val3 >= max_val:
                    value_to_append = min_val - current_val
                elif val3 <= min_val:
                    value_to_append = max_val - current_val
                else:
                    value_to_append = (val1 + val2 - val3 - current_val)

            E.append(value_to_append)

    return E



def setHeader(X, min_val, max_val, n):
    header = []

    # Image height (12 bits)
    header.append(bin(n)[2:].zfill(12))

    # First element from C (8 bits)
    header.append(bin(min_val)[2:].zfill(8))

    # Last element from C (32 bits)
    header.append(bin(max_val)[2:].zfill(32))

    # Number of all elements (24 bits)
    header.append(bin(X * n)[2:].zfill(24))

    return header


def IC(B, C, L, H):
    if H - L > 1:
        if C[L] != C[H]:
            m = math.floor(0.5 * (L + H))
            g = math.ceil(log2(C[H] - C[L] + 1))
            B = encode(B, g, C[m] - C[L])

            if L < m:
                IC(B, C, L, m)

            if m < H:
                IC(B, C, m, H)
    return B


def encode(B, g, m):
    # Truncate 'm' to fit within 'g' bits
    max_val = (1 << int(g)) - 1
    if m > max_val:
        m = max_val

    # Encode 'm' as a truncated binary with 'g' bits
    truncated_binary = format(m, f'0{int(g)}b')

    # Ensure that the encoded binary matches the size of 'g'
    if len(truncated_binary) > int(g):
        truncated_binary = truncated_binary[-int(g):]  # Take the least significant 'g' bits
    elif len(truncated_binary) < int(g):
        truncated_binary = truncated_binary.zfill(int(g))  # Zero-pad to make it 'g' bits

    B.append(truncated_binary)
    return B


def compress(P, X, Y):
    predicted_val = predict(P, X, Y)
    #print(predicted_val)
    N = [predicted_val[0]]

    for i in range(1, X * Y):
        if predicted_val[i] == 0:
            N.append(0)
        elif predicted_val[i] > 0:
            N.append(2 * predicted_val[i])
        else:
            N.append(2 * abs(predicted_val[i]) - 1)

    #print(N)
    if P.mode == 'L':
       C = [N[0]]
    elif P.mode == 'RGB':
       C = [N[0][0]]

    for i in range(1, X * Y):
        C.append(N[i] + C[i - 1])

    n = X * Y
    B = setHeader(X, C[0], C[n - 1], n)
    Bic = IC(B, C, 0, n - 1)
    return predicted_val, N, C, B, Bic


if __name__ == "__main__":
    # image_path = "slike BMP/Monarch.bmp"
    image_path = sys.argv[1]
    print("pot " + image_path)

    #slika, pixel_values, Y, X, original_mode = read_bmp_image(image_path)

    #predicted_values, N, C, B, Bic = compress(slika, X, Y)
    #print("Pixel values:", Bic)
