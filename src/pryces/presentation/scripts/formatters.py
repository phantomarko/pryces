from ...application.dtos import StockStatisticsDTO


def format_stats(dto: StockStatisticsDTO) -> str:
    header = f"📊 {dto.symbol} — {dto.current_price:.2f}"
    lines = [header]
    if not dto.price_changes:
        lines.append("No historical data available")
        return "\n".join(lines)
    for pc in dto.price_changes:
        sign = "+" if pc.change_percentage > 0 else ""
        pct_str = f"{sign}{pc.change_percentage:.2f}%"
        icon = "📈" if pc.change_percentage >= 0 else "📉"
        lines.append(f"{icon} {pc.period:<3}  {pc.close_price:.2f}  {pct_str}")
    return "\n".join(lines)
