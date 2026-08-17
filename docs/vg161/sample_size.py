"""VG161 随机对照 II 期样本量测算。

生成《VG161-II期设计决策审核意见.md》第 4.2 节表格中的数字。

PFS 采用 Schoenfeld 公式（1:1 随机、对数秩检验、比例风险假设）：
    所需事件数 = 4 * (z_{1-alpha} + z_{power})^2 / (ln HR)^2
样本量按 PFS 事件率 0.90 反推（对照组中位 PFS 3.0 个月、随访 >=12 个月的合理取值）。

ORR 采用两独立比例的正态近似，用于交叉验证 PFS 样本量的量级。
"""

from math import ceil, log
from statistics import NormalDist

NORM = NormalDist()
EVENT_RATE = 0.90


def pfs_events(hr: float, alpha: float, power: float) -> float:
    """1:1 随机下检出给定风险比所需的 PFS 事件数。"""
    z_sum = NORM.inv_cdf(1 - alpha) + NORM.inv_cdf(power)
    return 4 * z_sum**2 / log(hr) ** 2


def orr_per_arm(p_exp: float, p_ctl: float, alpha: float, power: float) -> float:
    """两独立比例比较时每组所需样本量。"""
    z_sum = NORM.inv_cdf(1 - alpha) + NORM.inv_cdf(power)
    variance = p_exp * (1 - p_exp) + p_ctl * (1 - p_ctl)
    return z_sum**2 * variance / (p_exp - p_ctl) ** 2


def main() -> None:
    print("== 主终点 PFS（对照组中位 PFS 3.0 个月，事件率 0.90）==")
    print(f"{'单侧α':>8}{'效能':>8}{'目标HR':>9}{'需事件数':>11}{'需样本量':>11}")
    for alpha in (0.10, 0.025):
        for power in (0.80, 0.90):
            for hr in (0.55, 0.60, 0.65, 0.70):
                events = ceil(pfs_events(hr, alpha, power))
                print(
                    f"{alpha:>8.3f}{power:>8.2f}{hr:>9.2f}"
                    f"{events:>11d}{ceil(events / EVENT_RATE):>11d}"
                )

    print("\n== 交叉验证：以 ORR 为终点（效能 80%）==")
    print(f"{'试验组ORR':>11}{'对照组ORR':>11}{'单侧α':>8}{'每组':>8}{'合计':>8}")
    for p_exp in (0.25, 0.30, 0.35):
        for alpha in (0.10, 0.025):
            per_arm = ceil(orr_per_arm(p_exp, 0.12, alpha, 0.80))
            print(
                f"{p_exp:>11.0%}{0.12:>11.0%}{alpha:>8.3f}"
                f"{per_arm:>8d}{2 * per_arm:>8d}"
            )

    print("\n== 推荐方案 ==")
    for hr in (0.60, 0.65):
        events = ceil(pfs_events(hr, alpha=0.10, power=0.80))
        print(
            f"目标 HR {hr:.2f}：需 {events} 个 PFS 事件，"
            f"约 {ceil(events / EVENT_RATE)} 例；"
            f"无效性中期分析设于第 {ceil(0.45 * events)} 个事件（45%）"
        )


if __name__ == "__main__":
    main()
