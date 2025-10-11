
def text_to_path(input_text, front_id="F"):
    """
    Generates a unique path for a given text based on the COSMOS TGP concept.

    This revised function enhances sensitivity by converting each character's ASCII
    value into an 8-bit binary string. It then uses pairs of bits to sequentially
    select one of four quadrants, effectively making each character contribute
    four levels of depth to the path. This ensures that even a one-bit difference
    in input text results in a divergent path.

    Args:
        input_text (str): The input string to be converted into a path.
        front_id (str): An identifier for the entry point ("투입구 ID").

    Returns:
        list[int]: A list of integers (0-3) representing the path of quadrants.
    """
    full_text = f"{front_id}{input_text}"

    min_x, min_y = 0.0, 0.0
    max_x, max_y = 1.0, 1.0

    path = []

    for char in full_text:
        # Convert character to its 8-bit binary representation
        binary_representation = format(ord(char), '08b')

        # Process the 4 bit-pairs from the binary string
        for i in range(0, 8, 2):
            bit_pair = binary_representation[i:i+2]

            # Convert the bit-pair '00', '01', '10', '11' to an integer 0, 1, 2, 3
            quadrant = int(bit_pair, 2)
            path.append(quadrant)

            # "Fold" the space based on the quadrant
            # Quadrant layout based on bit-pairs:
            # '01'(1) | '00'(0)
            #---------+---------
            # '10'(2) | '11'(3)
            center_x = (min_x + max_x) / 2.0
            center_y = (min_y + max_y) / 2.0

            if quadrant == 0: # Top-Right
                min_x, min_y = center_x, center_y
            elif quadrant == 1: # Top-Left
                max_x, min_y = center_x, center_y
            elif quadrant == 2: # Bottom-Left
                max_x, max_y = center_x, center_y
            elif quadrant == 3: # Bottom-Right
                min_x, max_y = center_x, center_y

    return path


if __name__ == "__main__":
    # --- 개념 증명을 위한 데모 ---
    print("COSMOS TGP: 개념 증명 데모")
    print("-" * 40)

    # 1. "Apple" 텍스트에 대한 경로 생성
    text_apple = "Apple"
    path_apple = text_to_path(text_apple, front_id="A")

    print(f"입력 텍스트: '{text_apple}' (Front ID: 'A')")
    print(f"생성된 경로: {path_apple}")
    print("-" * 40)

    # 2. 작은 변화에 대한 민감도 테스트
    # 글자 하나만 달라도 경로가 달라지는 것을 보여줍니다.
    text_appld = "Appld"
    path_appld = text_to_path(text_appld, front_id="A")

    text_applf = "Applf"
    path_applf = text_to_path(text_applf, front_id="A")

    print("입력값 민감도 테스트:")
    print(f"입력 텍스트: '{text_appld}'")
    print(f"생성된 경로: {path_appld}")
    print()
    print(f"입력 텍스트: '{text_applf}'")
    print(f"생성된 경로: {path_applf}")
    print("-" * 40)

    # 3. 경로 비교
    # 'Appl'까지는 경로가 동일해야 합니다.
    common_prefix_len = 0
    for i in range(min(len(path_apple), len(path_appld))):
        if path_apple[i] == path_appld[i]:
            common_prefix_len += 1
        else:
            break

    print(f"'Apple'과 'Appld'의 경로는 첫 {common_prefix_len} 단계까지 동일합니다.")
    print("이후 마지막 문자인 'e'와 'd'에서 경로가 달라집니다.")
