import math

from PIL import Image
from math import log2
import os
import time
import sys


def decodeheader(B):
    n = int(B[0], 2)
    min_val = int(B[1], 2)
    max_val = int(B[2], 2)
    X = int(B[3], 2) // n

    return X, min_val, max_val, n


def initializeC(n, first_el, last_el):
    return [first_el] + [0] * (n - 2) + [last_el]


def getBits(B, i, g):
    bits = ""
    for j in range(i, len(B)):
        bits += B[j]

        # Increment 'i' to move to the next segment of 'B'
        i += 1
        if len(bits) == g:
            break

    return bits, i  # Return the extracted bits and the updated index 'i'

def decode(bits_list):
    decoded_values = []
    for bits in bits_list:
        decoded_values.append(int(bits, 2))
    return decoded_values


def deIC(B, C, L, H, i=4):
    if H - L > 1:
        if C[L] != C[H]:
            m = math.floor(0.5 * (L + H))
            g = math.ceil(log2(C[H] - C[L] + 1))
            bits, i = getBits(B, i, g)
            decoded_values = decode([bits])
            C[m] = decoded_values[0] + C[L]

            if L < m:
                C, i = deIC(B, C, L, m, i)

            if m < H:
                C, i = deIC(B, C, m, H, i)
        else:
            for j in range(L + 1, H):
                C[j] = C[L]

    return C, i


def inversePredict(E, X, Y):
    P = []

    for x in range(Y):
        for y in range(X):
            index = x * X + y

            if x == 0 and y == 0:
                P.append(E[index])
            elif y == 0:
                x1 = P[(x - 1) * X] - E[index]
                P.append(x1)
            elif x == 0:
                y1 = P[y - 1] - E[index]
                P.append(y1)
            else:
                max_val = max(P[(x - 1) * X + y], P[x * X + y - 1])
                min_val = min(P[(x - 1) * X + y], P[x * X + y - 1])

                if P[(x - 1) * X + y - 1] >= max_val:
                    P.append(min_val - E[index])
                elif P[(x - 1) * X + y - 1] <= min_val:
                    P.append(max_val - E[index])
                else:
                    tmp = (P[(x - 1) * X + y] + P[x * X + y - 1] - P[(x - 1) * X + y - 1])
                    P.append(tmp - E[index])

    return P


def create_image_from_P(P, X, Y):
    img = Image.new('RGB', (Y, X))

    for x in range(Y):
        for y in range(X):
            index = x * X + y
            img.putpixel((x, y), (P[index], P[index], P[index]))

    return img

def decompress(B):
    X, first_el, last_el, n = decodeheader(B)

    # print("X:", X)
    # print("First element:", first_el)
    # print("Last element:", last_el)
    # print("n:", n)

    Y = int(n / X)
    # print("Y:", Y)
    C = initializeC(n, first_el, last_el)
    # print("C:", C)
    C = deIC(B, C, 0, n-1)
    C = C[0]
    # print("C:", C)
    dN = [0] * n
    dN[0] = C[0]
    for i in range(1, n):
        dN[i] = C[i] - C[i - 1]
    # print("dN:", dN)
    dE = [0] * n
    dE[0] = dN[0]

    for i in range(1, n):
        if (dN[i] % 2 == 0):
            dE[i] = int(dN[i] / 2)
        else:
            dE[i] = - int((dN[i] + 1) / 2)
    # print("dE:", dE)
    dP = inversePredict(dE, X, Y)
    dImg = create_image_from_P(dP, X, Y)
    # print("dP:", dP)
    return dImg


def save_as_bmp(dec_img, file_path):
    try:
        dec_img = dec_img.convert('L')  # Convert to 8-bit grayscale
        print("L")
        dec_img.save(file_path)

        print(f"Image saved successfully at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    my_img = Image.open(file_path)
    my_img.show()

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read().strip()  # Uporabite read() namesto readlines()
    return [file_content]

if __name__ == "__main__":
    input_file_path = sys.argv[1]
    print(input_file_path)
    Bic = read_file_content(input_file_path)


    print(Bic)
    #decImg = decompress(Bic1)
    #print(decImg)
    #dec_img_path = "decompressed.bmp"
    #save_as_bmp(decImg, dec_img_path)