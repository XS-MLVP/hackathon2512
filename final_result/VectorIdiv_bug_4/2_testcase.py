from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple


def resolve_dut_class():
    """Load DUTVectorIdiv from any available module variant."""

    try:
        from UT_VectorIdiv import DUTVectorIdiv  # type: ignore

        return DUTVectorIdiv
    except ImportError:
        try:
            from VectorIdiv import DUTVectorIdiv  # type: ignore

            return DUTVectorIdiv
        except ImportError:
            from __init__ import DUTVectorIdiv  # type: ignore

            return DUTVectorIdiv


def apply_reset(dut: "DUTVectorIdiv", cycles: int = 4) -> None:
    # Align DUT with a known state before issuing transactions.
    dut.reset.value = 1
    dut.io_flush.value = 0
    dut.io_div_in_valid.value = 0
    dut.io_div_out_ready.value = 0
    dut.Step(cycles)
    dut.reset.value = 0
    dut.Step(1)


def wait_for_ready(dut: "DUTVectorIdiv", limit: int = 50) -> bool:
    # Poll until the divider reports readiness or the watchdog expires.
    for _ in range(limit):
        if dut.io_div_in_ready.value:
            return True
        dut.Step(1)
    return False


def launch_division(dut: "DUTVectorIdiv") -> None:
    # One-cycle valid pulse to start a divide, then allow state to settle.
    dut.io_div_in_valid.value = 1
    dut.Step(1)
    dut.io_div_in_valid.value = 0
    dut.Step(1)


def flush_and_measure(dut: "DUTVectorIdiv", probe_window: int = 20) -> Optional[int]:
    # Assert flush during BUSY and record how quickly the DUT returns to IDLE.
    dut.io_flush.value = 1
    dut.Step(1)
    dut.io_flush.value = 0

    for cycle in range(1, probe_window + 1):
        if dut.io_div_in_ready.value:
            return cycle
        dut.Step(1)
    return None


def pack_u32_lanes(lanes: Sequence[int]) -> int:
    # Pack little-endian 32-bit lanes into the 128-bit vector container.
    value = 0
    for idx, lane in enumerate(lanes):
        value |= (lane & 0xFFFFFFFF) << (32 * idx)
    return value


def unpack_u32_lanes(value: int, lanes: int = 4) -> Tuple[int, ...]:
    return tuple((value >> (32 * idx)) & 0xFFFFFFFF for idx in range(lanes))


def wait_for_output(dut: "DUTVectorIdiv", limit: int = 200) -> Optional[Tuple[int, int, int, int]]:
    # Capture the first valid result along with latency and status flags.
    for cycle in range(1, limit + 1):
        if dut.io_div_out_valid.value:
            return (
                cycle,
                dut.io_div_out_q_v.value,
                dut.io_div_out_rem_v.value,
                dut.io_d_zero.value,
            )
        dut.Step(1)
    return None


def _format_lane_list(values: Sequence[int]) -> str:
    return "，".join(f"lane{idx}={val:#010x}" for idx, val in enumerate(values))


def _render_notice(message: str) -> None:
    print(f"⚠️ 提示：{message}")


def _render_report(data: Dict[str, object]) -> None:
    lines = [
        "🚀 测试摘要",
        f"  • ⏱️ 刷新后 {data['ready_after_flush']} 个周期重新就绪",
        f"  • 🕒 结果在 {data['output_latency']} 个周期后产生",
        "",
        "📊 结果对比",
        f"  • 实际商向量：{data['actual_quotient']}",
        f"  • 期望商向量：{data['expected_quotient']} (HEX: {data['expected_quotient_hex']})",
        f"  • 实际余数向量：{data['actual_remainder']}",
        f"  • 期望余数向量：{data['expected_remainder']} (HEX: {data['expected_remainder_hex']})",
        f"  • 实际除零掩码：{data['d_zero_mask']}，期望：{data['expected_d_zero_mask']}",
    ]

    mismatched = data["mismatched_lanes"]
    if mismatched:
        lines.append(f"  • ❌ 不一致的通道：{', '.join(str(i) for i in mismatched)}")
    else:
        lines.append("  • ✅ 所有通道结果与期望一致")

    analysis = data.get("analysis")
    if analysis:
        lines.extend(["", f"🔍 原因分析：{analysis}"])

    print("\n".join(lines))


def main() -> None:
    DUT = resolve_dut_class()
    dut = DUT()

    try:
        dut.InitClock("clock")
        apply_reset(dut)

        dut.io_div_out_ready.value = 1
        dut.io_sew.value = 0b10
        dut.io_sign.value = 0
        # Operand set A launches before the flush; operand set B follows after recovery.
        op_a_dividends = [0xCAFEBABE, 0x10203040, 0x0F1E2D3C, 0x89ABCDEF]
        op_a_divisors = [0x0000FF11, 0x00010003, 0x00F0F0F1, 0x01020304]
        op_b_dividends = [0x13572468, 0x5555AAA0, 0xFEEDC0DE, 0x12348765]
        op_b_divisors = [0x00000007, 0x0000AAAA, 0x00010001, 0x00C00003]

        dut.io_dividend_v.value = pack_u32_lanes(op_a_dividends)
        dut.io_divisor_v.value = pack_u32_lanes(op_a_divisors)

        if not wait_for_ready(dut):
            raise RuntimeError("DUT never asserted io_div_in_ready during init window")

        launch_division(dut)

        if dut.io_div_in_ready.value:
            raise RuntimeError("Division did not enter busy state as expected")

        dut.Step(2)

        recovery_cycle = flush_and_measure(dut)

        status: Dict[str, object] = {
            "ready_after_flush": recovery_cycle,
        }

        if recovery_cycle is None:
            status["note"] = "刷新信号在观测窗口内未生效"
            _render_notice(status["note"])
            return

        dut.io_dividend_v.value = pack_u32_lanes(op_b_dividends)
        dut.io_divisor_v.value = pack_u32_lanes(op_b_divisors)

        if not wait_for_ready(dut):
            raise RuntimeError("刷新后 DUT 未重新进入就绪态")

        launch_division(dut)

        output_snapshot = wait_for_output(dut)

        if output_snapshot is None:
            status["note"] = "在等待窗口内未观察到输出"
            _render_notice(status["note"])
            return

        latency, quotient, remainder, d_zero = output_snapshot

        exp_quots = tuple(div // divr if divr else 0 for div, divr in zip(op_b_dividends, op_b_divisors))
        exp_rems = tuple(div % divr if divr else div for div, divr in zip(op_b_dividends, op_b_divisors))
        exp_d_zero = sum((1 << idx) for idx, divr in enumerate(op_b_divisors) if divr == 0)

        act_quots = unpack_u32_lanes(quotient)
        act_rems = unpack_u32_lanes(remainder)

        mismatched = [idx for idx in range(len(exp_quots)) if (act_quots[idx] != exp_quots[idx] or act_rems[idx] != exp_rems[idx])]

        status.update(
            {
                "output_latency": latency,
                "actual_quotient": f"0x{quotient:032x}",
                "expected_quotient": f"[{_format_lane_list(exp_quots)}]",
                "expected_quotient_hex": f"0x{pack_u32_lanes(exp_quots):032x}",
                "actual_remainder": f"0x{remainder:032x}",
                "expected_remainder": f"[{_format_lane_list(exp_rems)}]",
                "expected_remainder_hex": f"0x{pack_u32_lanes(exp_rems):032x}",
                "d_zero_mask": f"0x{d_zero:04x}",
                "expected_d_zero_mask": f"0x{exp_d_zero:04x}",
                "mismatched_lanes": mismatched,
            }
        )

        if mismatched:
            pre_flush_quots = tuple(div // divr if divr else 0 for div, divr in zip(op_a_dividends, op_a_divisors))
            stale_lanes = [idx for idx in mismatched if act_quots[idx] == pre_flush_quots[idx]]
            if stale_lanes:
                status["analysis"] = (
                    "通道 "
                    + "、".join(str(idx) for idx in stale_lanes)
                    + " 保留了刷新前的商值，说明 io_flush 未能清除流水线寄存器"
                )
            else:
                status["analysis"] = "刷新后仍存在残余数据，请检查额外的寄存器路径"
        else:
            status["analysis"] = "所有通道均符合刷新后的期望数值"

        _render_report(status)
    finally:
        dut.Finish()


if __name__ == "__main__":
    main()
