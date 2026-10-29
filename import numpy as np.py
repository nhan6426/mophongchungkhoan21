import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

# 1. Tải dữ liệu chính xác từ file abc-21.csv
df = pd.read_csv('abc-21.csv', header=None)
n_days = len(df)  # 365 ngày

# Lấy các giá trị Mở cửa, Đóng cửa, Đỉnh (High), Đáy (Low)
opens = df.iloc[:, 0].values
closes = df.iloc[:, 6].values
highs = df.max(axis=1).values
lows = df.min(axis=1).values

# Tính toán giá tham chiếu (Ref), giá sàn (90%), giá trần (110%)
ref_prices = np.zeros(n_days)
ref_prices[0] = opens[0]
ref_prices[1:] = closes[:-1]

floor_prices = ref_prices * 0.90
ceil_prices = ref_prices * 1.10

# 2. Thiết lập Figure & Subplots (Giao diện Dark theme như đề)
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw={'height_ratios': [1.2, 1]})
fig.patch.set_facecolor('black')

# 3. Hàm cập nhật từng khung hình (Animation)
def update(frame):
    if frame == 0:
        return
    
    ax1.clear()
    ax2.clear()
    
    # Cấu hình Subplot 1 (Candlestick Chart - Nến Nhật)
    ax1.set_facecolor('black')
    ax1.set_ylabel('VND', color='white', fontsize=10)
    ax1.set_xlim(-5, n_days + 10)
    ax1.set_ylim(-500, max(highs) * 1.1)
    ax1.grid(True, color='#222222', linestyle='--', alpha=0.5)
    
    # Cấu hình Subplot 2 (Continuous Band Chart)
    ax2.set_facecolor('black')
    ax2.set_ylabel('VND', color='white', fontsize=10)
    ax2.set_xlabel('Date (Ngày quan sát)', color='white', fontsize=10)
    ax2.set_xlim(-5, n_days + 10)
    ax2.set_ylim(-500, max(highs) * 1.1)
    ax2.grid(True, color='#222222', linestyle='--', alpha=0.5)
    
    # --- SUBPLOT 1: VẼ BIỂU ĐỒ CỘT NẾN CHUẨN (CANDLESTICK) ---
    for i in range(frame):
        op = opens[i]
        cl = closes[i]
        hi = highs[i]
        lo = lows[i]
        ref = ref_prices[i]
        
        # Quy ước màu sắc theo chuẩn chứng khoán Việt Nam:
        if np.isclose(cl, ceil_prices[i], rtol=1e-3):
            color = '#8A2BE2'  # Tím (Trần)
        elif np.isclose(cl, floor_prices[i], rtol=1e-3):
            color = '#00BFFF'  # Xanh dương (Sàn)
        elif np.isclose(cl, ref, rtol=1e-3):
            color = '#FFFF00'  # Vàng (Tham chiếu)
        elif cl >= ref:
            color = '#00FF00'  # Xanh lá (Tăng)
        else:
            color = '#FF0000'  # Đỏ (Giảm)
            
        # 1. Vẽ Râu nến / Bóng nến (Nối từ Low đến High)
        ax1.plot([i, i], [lo, hi], color=color, linewidth=1.2, zorder=2)
        
        # 2. Vẽ Thân nến dạng Hình chữ nhật (Open -> Close)
        body_bottom = min(op, cl)
        body_height = max(abs(cl - op), (hi - lo) * 0.08, 30)  # Đảm bảo độ dày tối thiểu
        
        rect = patches.Rectangle(
            (i - 0.35, body_bottom),  # Tọa độ góc dưới bên trái
            0.7,                      # Bề rộng thân nến
            body_height,              # Chiều cao thân nến
            facecolor=color,
            edgecolor=color,
            zorder=3
        )
        ax1.add_patch(rect)

    # --- SUBPLOT 2: VẼ DẢI BIÊN ĐỘ VÀ CÁC ĐƯỜNG GIÁ KẺ NGANG ---
    x_data = np.arange(frame)
    y_close = closes[:frame]
    y_high = highs[:frame]
    y_low = lows[:frame]
    
    # Dải biên độ High - Low
    ax2.fill_between(x_data, y_low, y_high, color='#2e8b57', alpha=0.4)
    ax2.plot(x_data, y_close, color='#adff2f', linewidth=1.2)
    
    curr_close = closes[frame - 1]
    curr_max_all = np.max(highs[:frame])
    curr_min_all = np.min(lows[:frame])
    
    # Đỉnh lịch sử
    ax2.axhline(y=curr_max_all, color='green', linestyle=':', linewidth=0.8, alpha=0.7)
    ax2.text(n_days + 2, curr_max_all, f"{curr_max_all:,.0f}", color='#00FF00', fontsize=8, verticalalignment='center')
    
    # Giá hiện tại
    ax2.axhline(y=curr_close, color='limegreen', linestyle='--', linewidth=0.8, alpha=0.8)
    ax2.text(n_days + 2, curr_close, f"{curr_close:,.0f}", color='limegreen', fontsize=8, verticalalignment='center')
    
    # Đáy lịch sử
    ax2.axhline(y=curr_min_all, color='red', linestyle=':', linewidth=0.8, alpha=0.7)
    ax2.text(n_days + 2, curr_min_all, f"{curr_min_all:,.0f}", color='red', fontsize=8, verticalalignment='center')

# 4. Xuất Video MP4
print("Đang khởi tạo Video Animation Biểu đồ Cột Nến chuẩn...")
ani = animation.FuncAnimation(fig, update, frames=n_days, interval=40, repeat=False)

output_filename = "simulation.mp4"
print(f"Đang ghi file {output_filename}...")
ani.save(output_filename, writer='ffmpeg', fps=25)
print("-> ĐÃ XUẤT VIDEO THÀNH CÔNG!")