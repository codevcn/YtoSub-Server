from pathlib import Path

# Thêm .resolve() để đảm bảo root_dir luôn là đường dẫn tuyệt đối rõ ràng
root_dir = Path(__file__).resolve().parent.parent.parent
print("Project root directory:", root_dir)
