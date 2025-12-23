try:
    from UT_VectorIdiv import *
except:
    try:
        from VectorIdiv import *
    except:
        from __init__ import *

# 构造一个能触发 bug 的场景：8-bit 模式下余数向量低64位等于 0x5
# lane0: dividend=5, divisor=10 -> rem=5
# lane1-7: dividend=0, divisor=1 -> rem=0
# 其余高位 lanes 设置为0，不影响触发条件
if __name__ == "__main__":
    dut = DUTVectorIdiv()
    # 时序/握手：使用Step推进
    dut.InitClock("clock")

    # 复位序列
    dut.reset.value = 1
    dut.io_flush.value = 0
    for _ in range(5):
        dut.Step(1)
    dut.reset.value = 0

    # 配置8-bit模式，无符号除法
    dut.io_sew.value = 0  # 00 -> I8
    dut.io_sign.value = 0 # 无符号

    # 构造 128-bit 输入向量，每8位一个lane，总计16 lanes
    lanes_dividend = [5, 0, 0, 0, 0, 0, 0, 0,  # 低64位的8个lane
                      0, 0, 0, 0, 0, 0, 0, 0]  # 高64位的8个lane
    lanes_divisor  = [10, 1, 1, 1, 1, 1, 1, 1,
                      1, 1, 1, 1, 1, 1, 1, 1]

    # 将8位lane打包成小端序的128位向量：lane0为最低8位
    def pack_u8_le(vals):
        v = 0
        for i, b in enumerate(vals):
            v |= (b & 0xFF) << (8 * i)
        return v

    dut.io_dividend_v.value = pack_u8_le(lanes_dividend)
    dut.io_divisor_v.value  = pack_u8_le(lanes_divisor)

    # 刷新组合逻辑以采样当前输入
    dut.RefreshComb()

    # 握手信号准备
    dut.io_div_in_valid.value = 0
    dut.io_div_out_ready.value = 1

    # 复位拉低，准备运行
    dut.reset.value = 0

    # 等待输入ready
    for _ in range(200):
        dut.Step(1)
        if dut.io_div_in_ready.value:
            break

    # 发送一次有效输入脉冲
    dut.io_div_in_valid.value = 1
    dut.Step(1)
    dut.io_div_in_valid.value = 0

    # 推进直到输出有效
    for _ in range(500):
        dut.Step(1)
        if dut.io_div_out_valid.value:
            break

    rem = dut.io_div_out_rem_v.value
    q   = dut.io_div_out_q_v.value
    dz  = dut.io_d_zero.value
    print(f"io_div_out_valid={dut.io_div_out_valid.value}")
    print(f"remainder=0x{rem:032x}")
    print(f"quotient=0x{q:032x}")
    print(f"d_zero=0x{dz:04x}")

    dut.Finish()
