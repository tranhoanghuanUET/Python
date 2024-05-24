import numpy as np  # Import thư viện numpy để làm việc với các mảng số học
import matplotlib.pyplot as plt  # Import thư viện matplotlib.pyplot để vẽ biểu đồ
from matplotlib.animation import FuncAnimation  # Import FuncAnimation để tạo hoạt hình

class Drone:
    def __init__(self, x, y, vx, vy):
        self.position = np.array([x, y])  # Thiết lập vị trí ban đầu của drone
        self.velocity = np.array([vx, vy])  # Thiết lập vận tốc ban đầu của drone

def repulsive_force(drone, others, repulsive_gain, repulsive_radius):
    steer = np.zeros(2)  # Khởi tạo vector điều chỉnh với giá trị ban đầu là [0, 0]
    for other in others:
        if other != drone:  # Đảm bảo không so sánh với chính drone hiện tại
            distance = np.linalg.norm(other.position - drone.position)  # Tính khoảng cách giữa hai drone
            if 0 < distance < repulsive_radius:  # Nếu khoảng cách nằm trong bán kính tránh va chạm
                steer -= (other.position - drone.position) * repulsive_gain / distance**2  # Tính toán lực đẩy
    return steer  # Trả về vector điều chỉnh

def alignment_force(drone, others, alignment_gain, alignment_radius):
    average_velocity = np.zeros(2)  # Khởi tạo vận tốc trung bình với giá trị ban đầu là [0, 0]
    count = 0  # Biến đếm số lượng drone trong bán kính alignment
    for other in others:
        if other != drone:  # Đảm bảo không so sánh với chính drone hiện tại
            distance = np.linalg.norm(other.position - drone.position)  # Tính khoảng cách giữa hai drone
            if distance < alignment_radius:  # Nếu khoảng cách nằm trong bán kính alignment
                average_velocity += other.velocity  # Cộng vận tốc của drone khác vào vận tốc trung bình
                count += 1  # Tăng biến đếm
    if count > 0:
        average_velocity /= count  # Tính vận tốc trung bình
        return (average_velocity - drone.velocity) * alignment_gain  # Tính toán lực alignment
    return np.zeros(2)  # Trả về [0, 0] nếu không có drone nào trong bán kính alignment

def cohesion_force(drone, others, cohesion_gain, cohesion_radius):
    center_of_mass = np.zeros(2)  # Khởi tạo tâm khối với giá trị ban đầu là [0, 0]
    count = 0  # Biến đếm số lượng drone trong bán kính cohesion
    for other in others:
        if other != drone:  # Đảm bảo không so sánh với chính drone hiện tại
            distance = np.linalg.norm(other.position - drone.position)  # Tính khoảng cách giữa hai drone
            if distance < cohesion_radius:  # Nếu khoảng cách nằm trong bán kính cohesion
                center_of_mass += other.position  # Cộng vị trí của drone khác vào tâm khối
                count += 1  # Tăng biến đếm
    if count > 0:
        center_of_mass /= count  # Tính vị trí trung bình (tâm khối)
        return (center_of_mass - drone.position) * cohesion_gain  # Tính toán lực cohesion
    return np.zeros(2)  # Trả về [0, 0] nếu không có drone nào trong bán kính cohesion

def update_drone(drone, others, target_position, repulsive_gain, repulsive_radius, alignment_gain, alignment_radius, cohesion_gain, cohesion_radius, speed_limit):
    avoidance_force = repulsive_force(drone, others, repulsive_gain, repulsive_radius)  # Tính toán lực tránh va chạm
    align_force = alignment_force(drone, others, alignment_gain, alignment_radius)  # Tính toán lực alignment
    cohesion_force_ = cohesion_force(drone, others, cohesion_gain, cohesion_radius)  # Tính toán lực cohesion
    direction = target_position - drone.position  # Tính toán hướng tới mục tiêu

    drone.velocity += direction * 0.005  # Cập nhật vận tốc theo hướng mục tiêu
    drone.velocity += avoidance_force * 0.005  # Cập nhật vận tốc theo lực tránh va chạm
    drone.velocity += align_force * 0.005  # Cập nhật vận tốc theo lực alignment
    drone.velocity += cohesion_force_ * 0.005  # Cập nhật vận tốc theo lực cohesion

    speed = np.linalg.norm(drone.velocity)  # Tính toán vận tốc hiện tại
    if speed > speed_limit:
        drone.velocity = (drone.velocity / speed) * speed_limit  # Giới hạn vận tốc nếu vượt quá speed_limit

    drone.position += drone.velocity  # Cập nhật vị trí của drone

# Thiết lập các thông số mô phỏng
num_drones = 10
arena_size = 100
time_steps = 100
repulsive_gain = 10
repulsive_radius = 1
alignment_gain = 0.1
alignment_radius = 30
cohesion_gain = 0.1
cohesion_radius = 30
speed_limit = 0.5

# Tạo danh sách các drone với vị trí và vận tốc ngẫu nhiên
drones = [Drone(np.random.uniform(0, 10), np.random.uniform(0, 10), np.random.uniform(-1, 1), np.random.uniform(-1, 1)) for _ in range(num_drones)]
target_position = np.array([50, 50])  # Vị trí mục tiêu

# Thiết lập biểu đồ
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, arena_size)
ax.set_ylim(0, arena_size)

# Tạo các đối tượng scatter để vẽ các drone và mục tiêu
drone_scatter = ax.scatter([], [], color='blue', s=5)
target_scatter = ax.scatter(target_position[0], target_position[1], color='red', marker='x', label='Target')

def animate(frame):
    global drones, target_position
    for drone in drones:
        update_drone(drone, drones, target_position, repulsive_gain, repulsive_radius, alignment_gain, alignment_radius, cohesion_gain, cohesion_radius, speed_limit)

    positions = np.array([drone.position for drone in drones])  # Lấy vị trí của tất cả các drone
    drone_scatter.set_offsets(positions)  # Cập nhật vị trí của các drone trong biểu đồ
    return drone_scatter, target_scatter

def move_target(event):
    global target_position, target_scatter
    if event.inaxes and event.button == 1:
        target_position = np.array([event.xdata, event.ydata])  # Cập nhật vị trí mục tiêu mới khi nhấn chuột
        target_scatter.set_offsets(target_position)  # Cập nhật vị trí của mục tiêu trong biểu đồ
        plt.draw()

# Tạo hoạt hình với FuncAnimation
ani = FuncAnimation(fig, animate, frames=time_steps, interval=50, blit=True)
plt.legend()  # Thêm chú thích vào biểu đồ

plt.connect('button_press_event', move_target)  # Kết nối sự kiện nhấn chuột để di chuyển mục tiêu

plt.show()  # Hiển thị biểu đồ
