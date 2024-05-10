import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Chọn backend cho matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment
from matplotlib.animation import FuncAnimation

# Định nghĩa hàm tính toán tiềm năng hấp dẫn giữa drone và mục tiêu
def attractive_potential(drone_pos, target_pos, attractive_gain):
    """Tính toán tiềm năng hấp dẫn giữa drone và mục tiêu."""
    khoang_cach = np.linalg.norm(drone_pos - target_pos)
    return 0.5 * attractive_gain * khoang_cach ** 2  # Hệ số hấp dẫn

# Định nghĩa hàm tính toán tiềm năng đẩy lùi giữa các drones
def repulsive_potential(drone_pos, other_pos, repulsive_gain, repulsive_radius):
    """Tính toán tiềm năng đẩy lùi giữa một drone và drone khác."""
    khoang_cach = np.linalg.norm(drone_pos - other_pos)
    if khoang_cach > 0 and khoang_cach < repulsive_radius:
        return repulsive_gain / khoang_cach ** 2
    else:
        return 0

# Hàm kiểm tra và điều chỉnh vị trí của drones để tránh va chạm
def adjust_positions_to_avoid_collision(drone_positions, repulsive_radius):
    """Điều chỉnh vị trí của các drones để tránh va chạm với nhau."""
    adjusted_positions = np.copy(drone_positions)
    # Duyệt qua tất cả các cặp drones
    for i in range(len(drone_positions)):
        for j in range(len(drone_positions)):
            if i != j:  # Kiểm tra hai drones có khác nhau không
                # Tính khoảng cách giữa hai drones
                distance = np.linalg.norm(drone_positions[i] - drone_positions[j])
                # Kiểm tra va chạm
                if distance < repulsive_radius:
                    # Tính hướng từ drone hiện tại đến drone gần nhất
                    direction = (drone_positions[i] - drone_positions[j]) / distance
                    # Điều chỉnh vị trí của drone hiện tại để tránh va chạm
                    adjusted_positions[i] += direction * (repulsive_radius - distance)
    return adjusted_positions

# Khởi tạo các tham số mô phỏng
num_drones = 36  # Số lượng drones
arena_size = 100  # Kích thước sân bay
attractive_gain = 1  # Hệ số hấp dẫn
repulsive_gain = 10  # Hệ số đẩy lùi
repulsive_radius = 15  # Bán kính đẩy lùi
time_steps = 100  # Số bước thời gian cho hoạt hình
step_size = 0.1  # Kích thước bước cho di chuyển của drones

# Khởi tạo vị trí ban đầu của drones
drone_pos = np.random.rand(num_drones, 2) * arena_size

# Tính toán vị trí mục tiêu cho các drones theo hình "khuôn viền"
target_positions = np.zeros((num_drones, 2))
for i in range(num_drones):
    target_positions[i] = [arena_size * np.sin(np.pi * i / num_drones), arena_size * np.cos(np.pi * i / num_drones)]

# Gán các mục tiêu bằng thuật toán Hungarian
ma_tran_khoang_cach = np.linalg.norm(drone_pos[:, None] - target_positions[None, :], axis=2)
row_ind, col_ind = linear_sum_assignment(ma_tran_khoang_cach)  # Tối thiểu hóa khoảng cách

# Tạo một hình và trục
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, arena_size)
ax.set_ylim(0, arena_size)

# Vẽ vị trí ban đầu của drones và mục tiêu
drone_scatter = ax.scatter(drone_pos[:, 0], drone_pos[:, 1], color='blue', label='Drones')
target_scatter = ax.scatter(target_positions[:, 0], target_positions[:, 1], color='green', label='Targets')

# Đặt tiêu đề và nhãn cho biểu đồ
ax.set_title('Mô phỏng di chuyển của nhiều drones')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.legend()
ax.grid(True)

# Định nghĩa hàm hoạt hình
def animate(frame):
    global drone_pos
    drone_pos = adjust_positions_to_avoid_collision(drone_pos, repulsive_radius)
    # Cập nhật vị trí của drones theo hướng tới mục tiêu
    for i in range(num_drones):
        huong = target_positions[col_ind[i]] - drone_pos[i]
        drone_pos[i] += step_size * huong / np.linalg.norm(huong)
         # Điều chỉnh vị trí của drones để tránh va chạm
    
    # Cập nhật scatter plot
    drone_scatter.set_offsets(drone_pos)

    return drone_scatter,

# Tạo hoạt hình
ani = FuncAnimation(fig, animate, frames=time_steps, interval=0.00000000003, blit=True)

# Hiển thị hoạt hình
plt.show()
