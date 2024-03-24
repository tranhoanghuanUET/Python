import turtle
import math

class ThreeWheeledRobot:
    def __init__(self):
        # Khởi tạo các thuộc tính của robot
        self.x = 0  # Tọa độ x của robot
        self.y = 0  # Tọa độ y của robot
        self.theta = 0  # Hướng của robot (góc so với trục x)
        self.velocity = 1  # Vận tốc của robot
        self.wheel_radius = 5  # Bán kính bánh xe
        self.length = 20  # Khoảng cách từ trục sau đến trục trước của robot
        self.dt = 0.1  # Thời gian giữa các bước di chuyển (đơn vị: giây)

    def move_forward(self):
        # Tính toán tọa độ mới của robot sau mỗi bước di chuyển thẳng
        self.x += self.velocity * math.cos(self.theta) * self.dt
        self.y += self.velocity * math.sin(self.theta) * self.dt

    def turn_left(self, angle):
        # Quay robot sang trái một góc được xác định bởi biến angle
        self.theta += angle

    def turn_right(self, angle):
        # Quay robot sang phải một góc được xác định bởi biến angle
        self.theta -= angle

    def update_position(self):
        # Cập nhật tọa độ mới của robot sau mỗi bước di chuyển
        # Di chuyển theo hướng hiện tại của robot
        self.move_forward()
        # Cập nhật tọa độ mới dựa trên bán kính bánh xe
        self.x += self.wheel_radius * math.cos(self.theta) * self.dt
        self.y += self.wheel_radius * math.sin(self.theta) * self.dt

# Hàm chính
def main():
    # Khởi tạo robot và cửa sổ đồ họa
    robot = ThreeWheeledRobot()
    screen = turtle.Screen()
    screen.setup(width=600, height=600)
    screen.bgcolor("white")

    # Tạo turtle để vẽ robot
    robot_turtle = turtle.Turtle()
    robot_turtle.shape("turtle")
    robot_turtle.color("blue")

    # Đường đi cho robot
    path = [(0, 50), (-90, 50), (90, 50), (0, 50), (45, 50), (0, 50)]

    # Mô phỏng di chuyển của robot theo đường đi đã cho
    for angle, distance in path:
        # Quay robot sang trái hoặc phải theo góc đã chỉ định
        robot.turn_left(angle) #quay phải trước xong mới đi thẳng
        # Di chuyển robot theo đường thẳng với khoảng cách đã chỉ định
        for _ in range(int(distance * 3 / robot.velocity)):
            # Cập nhật tọa độ mới của robot
            robot.update_position()
            # Di chuyển con rùa vẽ robot đến tọa độ mới
            robot_turtle.goto(robot.x, robot.y)

    # Hiển thị cửa sổ đồ họa và giữ cho nó hiển thị
    screen.mainloop()

# Gọi hàm chính để thực thi chương trình
if __name__ == "__main__":
    main()
