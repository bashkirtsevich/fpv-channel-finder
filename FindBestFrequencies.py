HZ_TARGET_COUNT = 8
REQS_1 = 26
REQS_2 = 11
REQS_3 = 12
IN_ONE_ROW = 30


def main():
    hzs = [0] * 10
    base = add_next_hz([0] * 259, hzs, 0)
    print("result: [", end="")
    for i in range(len(hzs)):
        print(f"{hzs[i]:4d}", end="")
        if i < len(hzs) - 1:
            print(", ", end="")
    print("]\n")
    if base is not None:
        print_base(base)
    else:
        print("Failed to find the solution :(")


def add_next_hz(old_base, hzs, adding_hz_idx):
    base = old_base.copy()

    adding_hz_base_idx = 0
    while adding_hz_base_idx < len(base):
        if base[adding_hz_base_idx] != 0:
            adding_hz_base_idx += 1
            continue

        base[adding_hz_base_idx] = -1
        hzs[adding_hz_idx] = adding_hz_base_idx

        if adding_hz_idx == HZ_TARGET_COUNT - 1:
            return base

        return_to_zeros = []

        # delete1
        d1 = adding_hz_base_idx
        while d1 < adding_hz_base_idx + REQS_1 and d1 < len(base):
            if base[d1] == 0:
                base[d1] = 1
                return_to_zeros.append(d1)
            d1 += 1

        # delete2
        d2_1 = adding_hz_base_idx + 190 - REQS_2
        while d2_1 <= adding_hz_base_idx + 190 + REQS_2:
            if 0 <= d2_1 < len(base) and base[d2_1] == 0:
                base[d2_1] = 2
                return_to_zeros.append(d2_1)
            d2_1 += 1

        d2_2 = adding_hz_base_idx + 240 - REQS_2
        while d2_2 <= adding_hz_base_idx + 240 + REQS_2:
            if 0 <= d2_2 < len(base) and base[d2_2] == 0:
                base[d2_2] = 2
                return_to_zeros.append(d2_2)
            d2_2 += 1

        # delete3
        for k in range(adding_hz_idx):
            d3_1 = (hzs[k] * 2 - adding_hz_base_idx) - REQS_3
            while d3_1 <= (hzs[k] * 2 - adding_hz_base_idx) + REQS_3:
                if 0 <= d3_1 < len(base) and base[d3_1] == 0:
                    base[d3_1] = 3
                    return_to_zeros.append(d3_1)
                d3_1 += 1

            d3_2 = (adding_hz_base_idx * 2 - hzs[k]) - REQS_3
            while d3_2 <= (adding_hz_base_idx * 2 - hzs[k]) + REQS_3:
                if 0 <= d3_2 < len(base) and base[d3_2] == 0:
                    base[d3_2] = 3
                    return_to_zeros.append(d3_2)
                d3_2 += 1

        result = add_next_hz(base, hzs, adding_hz_idx + 1)
        if result is not None:
            return result

        hzs[adding_hz_idx] = 0
        base[adding_hz_base_idx] = 4
        for return_to_zero in return_to_zeros:
            base[return_to_zero] = 0
        adding_hz_base_idx += 1

    return None


def print_base(base):
    for i in range(0, len(base) - IN_ONE_ROW + 1, IN_ONE_ROW):
        print(f"{i:4d} - {i + IN_ONE_ROW:4d}: [", end="")
        for j in range(IN_ONE_ROW):
            print(f"{base[i + j]:2d}", end="")
            if j < IN_ONE_ROW - 1:
                print(", ", end="")
        print("]")


if __name__ == "__main__":
    main()
