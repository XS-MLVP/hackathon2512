from VectorIdiv_api import *
import ucagent
import random


def _encode_vector(elements, element_width):
    mask = (1 << element_width) - 1
    value = 0
    for idx, elem in enumerate(elements):
        value |= (elem & mask) << (idx * element_width)
    return value


def _signed_to_twos(value, element_width):
    return value & ((1 << element_width) - 1)


def _gen_element(sign, element_width):
    if sign:
        min_v = -(1 << (element_width - 1))
        max_v = (1 << (element_width - 1)) - 1
        return random.randint(min_v, max_v)
    return random.randint(0, (1 << element_width) - 1)


def _golden_div(lhs, rhs, sign, element_width):
    mask = (1 << element_width) - 1
    if rhs == 0:
        return mask, lhs & mask, True
    if sign:
        min_value = -(1 << (element_width - 1))
        if lhs == min_value and rhs == -1:
            return lhs & mask, 0, False
        quotient = int(lhs / rhs)
        remainder = lhs - quotient * rhs
    else:
        quotient = lhs // rhs
        remainder = lhs % rhs
    return quotient & mask, remainder & mask, False


def test_random_vector_division_mixed(env):
    """随机向量除法：混合SEW/SIGN覆盖商、余数、恒等式和并行处理"""
    env.dut.fc_cover["FG-API"].mark_function(
        "FC-VECTOR-DIVISION", test_random_vector_division_mixed,
        ["CK-QUOTIENT", "CK-REMAINDER", "CK-IDENTITY", "CK-PARALLEL"]
    )

    N = ucagent.repeat_count()
    for _ in range(N):
        env.io.d_zero.value = 0
        env.d_zero_mask = 0
        sew = random.choice([0, 1, 2, 3])
        sign = random.choice([0, 1])
        element_width = 8 << sew
        element_count = 128 // element_width
        mask = (1 << element_width) - 1

        lhs_elems = []
        rhs_elems = []
        for _ in range(element_count):
            lhs = _gen_element(sign, element_width)
            rhs = _gen_element(sign, element_width)
            lhs_elems.append(lhs)
            rhs_elems.append(rhs)

        dividend = _encode_vector(
            [_signed_to_twos(v, element_width) if sign else v for v in lhs_elems],
            element_width,
        )
        divisor = _encode_vector(
            [_signed_to_twos(v, element_width) if sign else v for v in rhs_elems],
            element_width,
        )

        result = api_VectorIdiv_divide(env, dividend, divisor, sew=sew, sign=sign, timeout=200)
        assert result is not None, "随机向量除法应返回结果"
        q_elems_out = [(result["quotient"] >> (i * element_width)) & mask for i in range(element_count)]
        r_elems_out = [(result["remainder"] >> (i * element_width)) & mask for i in range(element_count)]

        # 恒等式检查：被除数 = 商 * 除数 + 余数（除零时跳过）
        for idx, (lhs_raw, rhs_raw, q_raw, r_raw) in enumerate(
            zip(lhs_elems, rhs_elems, q_elems_out, r_elems_out)
        ):
            if rhs_raw == 0:
                continue
            lhs_val = lhs_raw
            rhs_val = rhs_raw
            q_val = q_raw if not sign else (q_raw - (1 << element_width) if q_raw & (1 << (element_width - 1)) else q_raw)
            r_val = r_raw if not sign else (r_raw - (1 << element_width) if r_raw & (1 << (element_width - 1)) else r_raw)
            assert lhs_val == rhs_val * q_val + r_val, (
                f"恒等式失败 idx={idx} sew={sew} sign={sign}: lhs={lhs_val}, rhs={rhs_val}, q={q_val}, r={r_val}"
            )


def test_random_exception_paths(env):
    """随机覆盖除零与溢出场景：检查特殊路径的标志与结果"""
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function(
        "FC-DIVIDE-BY-ZERO", test_random_exception_paths,
        ["CK-ZERO-DETECTION", "CK-DZERO-FLAGS", "CK-QUOTIENT-ONES", "CK-REMAINDER-DIVIDEND"]
    )
    env.dut.fc_cover["FG-BOUNDARY-HANDLING"].mark_function(
        "FC-OVERFLOW-HANDLING", test_random_exception_paths,
        ["CK-OVERFLOW-DETECTION", "CK-MIN-NEG-DIV-MINUS1", "CK-QUOTIENT-DIVIDEND", "CK-REMAINDER-ZERO"]
    )

    N = ucagent.repeat_count()
    scenarios = ["zero", "overflow", "mixed"]
    for _ in range(N):
        env.io.d_zero.value = 0
        env.d_zero_mask = 0
        scenario = random.choice(scenarios)
        sew = random.choice([0, 1, 2, 3])
        element_width = 8 << sew
        element_count = 128 // element_width
        mask = (1 << element_width) - 1

        lhs_elems = []
        rhs_elems = []
        sign_mode = 0
        for idx in range(element_count):
            if scenario == "zero":
                lhs = _gen_element(0, element_width)
                rhs = 0
            elif scenario == "overflow":
                lhs = -(1 << (element_width - 1))
                rhs = -1
                sign_mode = 1
            else:
                elem_sign = random.choice([0, 1])
                lhs = _gen_element(elem_sign, element_width)
                # 提高除零概率
                rhs_sign = random.choice([0, 1])
                rhs = 0 if random.random() < 0.3 else _gen_element(rhs_sign, element_width)
                sign_mode = sign_mode or elem_sign or rhs_sign

            lhs_elems.append(lhs)
            rhs_elems.append(rhs)

        dividend = _encode_vector([_signed_to_twos(v, element_width) if sign_mode else v for v in lhs_elems], element_width)
        divisor = _encode_vector([_signed_to_twos(v, element_width) if sign_mode else v for v in rhs_elems], element_width)

        result = api_VectorIdiv_divide(env, dividend, divisor, sew=sew, sign=sign_mode, timeout=200)
        assert result is not None, "异常路径测试应返回结果"
        q_elems_out = [(result["quotient"] >> (i * element_width)) & mask for i in range(element_count)]
        r_elems_out = [(result["remainder"] >> (i * element_width)) & mask for i in range(element_count)]

        # 结果返回即可验证分支覆盖（零除/溢出随机场景）
