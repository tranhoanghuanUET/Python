# Import các thư viện cần thiết
import pygame  # Thư viện Pygame để tạo game và đồ họa
import sys  # Thư viện sys để thoát chương trình
from tkinter import messagebox, Tk  # Thư viện tkinter để hiển thị thông báo
import time  # Thư viện time để tạo độ trễ

# Thiết lập kích thước cửa sổ
window_width = 800  # Chiều rộng của cửa sổ Pygame
window_height = 800  # Chiều cao của cửa sổ Pygame

# Khởi tạo Pygame
pygame.init()  # Khởi tạo tất cả các module Pygame đã nhập

# Tạo cửa sổ chính cho việc hiển thị tìm đường
window = pygame.display.set_mode((window_width, window_height))  # Thiết lập cửa sổ chính với kích thước đã định

# Kích thước của lưới (grid)
columns = 50  # Số cột trong lưới
rows = 50  # Số hàng trong lưới

# Kích thước của mỗi ô trong lưới
box_width = window_width // columns  # Chiều rộng của mỗi ô
box_height = window_height // rows  # Chiều cao của mỗi ô

# Các danh sách để lưu trữ các ô của lưới, hàng đợi cho BFS, và đường đi cuối cùng
grid = []  # Danh sách 2D để lưu trữ lưới các ô
queue = []  # Hàng đợi cho thuật toán BFS (Tìm kiếm theo chiều rộng)
path = []  # Danh sách để lưu trữ đường đi cuối cùng

# Định nghĩa lớp Box, đại diện cho mỗi ô trong lưới
class Box(pygame.sprite.Sprite):
    def __init__(self, i, j):
        super().__init__()
        self.image = pygame.Surface((box_width - 2, box_height - 2))  # Bề mặt của ô, trừ đi 2 pixel để tạo khoảng cách giữa các ô
        self.rect = self.image.get_rect()  # Lấy hình chữ nhật đại diện cho bề mặt của ô
        self.rect.topleft = (i * box_width, j * box_height)  # Đặt vị trí của ô trong lưới dựa trên chỉ số cột và hàng
        self.x = i  # Cột của ô trong lưới
        self.y = j  # Hàng của ô trong lưới
        self.start = False  # Cờ đánh dấu ô bắt đầu
        self.wall = False  # Cờ đánh dấu ô là tường
        self.target = False  # Cờ đánh dấu ô đích
        self.queued = False  # Cờ đánh dấu ô đã được đưa vào hàng đợi BFS
        self.visited = False  # Cờ đánh dấu ô đã được thăm trong BFS
        self.neighbours = []  # Danh sách các ô lân cận
        self.prior = None  # Ô trước đó trong đường đi

    def update(self):
        # Cập nhật màu sắc của ô dựa trên trạng thái của nó
        if self.start:
            self.image.fill((0, 200, 200))  # Màu xanh cyan cho ô bắt đầu
        elif self.wall:
            self.image.fill((10, 10, 10))  # Màu xám đậm cho ô tường
        elif self.target:
            self.image.fill((200, 200, 0))  # Màu vàng cho ô đích
        elif self in path:
            self.image.fill((0, 0, 200))  # Màu xanh dương cho ô trong đường đi
        elif self.visited:
            self.image.fill((0, 200, 0))  # Màu xanh lá cho ô đã được thăm
        elif self.queued:
            self.image.fill((200, 0, 0))  # Màu đỏ cho ô đã được đưa vào hàng đợi
        else:
            self.image.fill((100, 100, 100))  # Màu xám nhạt cho ô trống

    def set_neighbours(self):
        # Thiết lập các ô lân cận của ô hiện tại (các ô liền kề trong lưới)
        if self.x > 0:
            self.neighbours.append(grid[self.x - 1][self.y])  # Ô bên trái
        if self.x < columns - 1:
            self.neighbours.append(grid[self.x + 1][self.y])  # Ô bên phải
        if self.y > 0:
            self.neighbours.append(grid[self.x][self.y - 1])  # Ô phía trên
        if self.y < rows - 1:
            self.neighbours.append(grid[self.x][self.y + 1])  # Ô phía dưới

# Tạo lưới và thêm các ô vào lưới
all_sprites = pygame.sprite.Group()  # Nhóm chứa tất cả các sprite
for i in range(columns):
    arr = []  # Danh sách tạm thời để lưu các ô trong một cột
    for j in range(rows):
        box = Box(i, j)  # Tạo một ô mới
        arr.append(box)  # Thêm ô vào danh sách tạm thời
        all_sprites.add(box)  # Thêm ô vào nhóm sprite
    grid.append(arr)  # Thêm danh sách tạm thời vào lưới chính

# Thiết lập các ô lân cận cho mỗi ô trong lưới
for i in range(columns):
    for j in range(rows):
        grid[i][j].set_neighbours()  # Thiết lập các ô lân cận cho ô hiện tại

# Hàm chính cho việc hiển thị tìm đường
def main():
    begin_search = False  # Cờ để bắt đầu tìm kiếm
    target_box_set = False  # Cờ để kiểm tra xem ô đích đã được đặt hay chưa
    searching = True  # Cờ để kiểm tra xem quá trình tìm kiếm có đang diễn ra hay không
    target_box = None  # Ô đích
    start_box_set = False  # Cờ để kiểm tra xem ô bắt đầu đã được đặt hay chưa

    while True:
        for event in pygame.event.get():
            # Thoát ứng dụng
            if event.type == pygame.QUIT:
                pygame.quit()  # Thoát Pygame
                sys.exit()  # Thoát chương trình
            # Xử lý sự kiện nhấn nút chuột
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Nút chuột trái
                    x, y = pygame.mouse.get_pos()  # Lấy vị trí của chuột
                    i = x // box_width  # Tính chỉ số cột dựa trên vị trí chuột
                    j = y // box_height  # Tính chỉ số hàng dựa trên vị trí chuột
                    if not start_box_set and not grid[i][j].wall:
                        start_box = grid[i][j]  # Đặt ô bắt đầu
                        start_box.start = True  # Đánh dấu ô bắt đầu
                        start_box.visited = True  # Đánh dấu ô đã được thăm
                        queue.append(start_box)  # Thêm ô vào hàng đợi BFS
                        start_box_set = True  # Đặt cờ đã đặt ô bắt đầu
                    elif not grid[i][j].wall and not grid[i][j].start:
                        grid[i][j].wall = True  # Đánh dấu ô là tường
                elif event.button == 3:  # Nút chuột phải
                    x, y = pygame.mouse.get_pos()  # Lấy vị trí của chuột
                    i = x // box_width  # Tính chỉ số cột dựa trên vị trí chuột
                    j = y // box_height  # Tính chỉ số hàng dựa trên vị trí chuột
                    if not target_box_set and not grid[i][j].wall:
                        target_box = grid[i][j]  # Đặt ô đích
                        target_box.target = True  # Đánh dấu ô đích
                        target_box_set = True  # Đặt cờ đã đặt ô đích
            # Bắt đầu thuật toán tìm kiếm khi nhấn phím cách
            elif event.type == pygame.KEYDOWN and target_box_set:
                if event.key == pygame.K_SPACE:
                    begin_search = True  # Đặt cờ bắt đầu tìm kiếm

        if begin_search:
            if len(queue) > 0 and searching:
                current_box = queue.pop(0)  # Lấy ô đầu tiên trong hàng đợi
                current_box.visited = True  # Đánh dấu ô đã được thăm
                if current_box == target_box:
                    searching = False  # Ngừng tìm kiếm khi tìm thấy ô đích
                    while current_box.prior != start_box:
                        path.append(current_box.prior)  # Thêm ô vào đường đi
                        current_box = current_box.prior  # Di chuyển đến ô trước đó
                    animate_path(path[::-1])  # Gọi hàm để tạo hoạt ảnh cho đường đi
                else:
                    for neighbour in current_box.neighbours:
                        if not neighbour.queued and not neighbour.wall:
                            neighbour.queued = True  # Đánh dấu ô đã được đưa vào hàng đợi
                            neighbour.prior = current_box  # Đặt ô hiện tại là ô trước đó của ô lân cận
                            queue.append(neighbour)  # Thêm ô lân cận vào hàng đợi
            else:
                if searching:
                    Tk().wm_withdraw()  # Ẩn cửa sổ tkinter
                    messagebox.showinfo("No Solution", "There is no solution!")  # Hiển thị thông báo không có giải pháp
                    searching = False  # Ngừng tìm kiếm

        # Cập nhật hiển thị
        window.fill((0, 0, 0))  # Xóa màn hình bằng màu đen
        all_sprites.update()  # Cập nhật trạng thái của tất cả các sprite
        all_sprites.draw(window)  # Vẽ tất cả các sprite lên cửa sổ
        pygame.display.flip()  # Cập nhật toàn bộ màn hình hiển thị

# Hàm để tạo hoạt ảnh cho đường đi cuối cùng
def animate_path(path):
    animation_window = pygame.display.set_mode((window_width, window_height))  # Thiết lập cửa sổ hiển thị
    path_sprite = pygame.Surface((box_width - 2, box_height - 2))  # Tạo bề mặt cho sprite của đường đi
    path_sprite.fill((255, 0, 0))  # Đặt màu cho sprite là đỏ
    for box in path:
        animation_window.fill((0, 0, 0))  # Xóa màn hình bằng màu đen
        for i in range(columns):
            for j in range(rows):
                current_box = grid[i][j]
                color = (100, 100, 100)  # Màu mặc định là xám nhạt
                if current_box.start:
                    color = (0, 200, 200)  # Màu xanh cyan cho ô bắt đầu
                elif current_box.wall:
                    color = (10, 10, 10)  # Màu xám đậm cho ô tường
                elif current_box.target:
                    color = (200, 200, 0)  # Màu vàng cho ô đích
                pygame.draw.rect(animation_window, color, (current_box.x * box_width, current_box.y * box_height, box_width - 2, box_height - 2))  # Vẽ hình chữ nhật đại diện cho ô
        animation_window.blit(path_sprite, (box.x * box_width, box.y * box_height))  # Vẽ sprite đường đi lên màn hình
        pygame.display.flip()  # Cập nhật toàn bộ màn hình hiển thị
        time.sleep(0.1)  # Thời gian trễ để tạo hiệu ứng hoạt ảnh

# Chạy hàm chính
main()
