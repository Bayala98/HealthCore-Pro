import os

def get_image_path(folder, filename):

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "assets", folder, filename)

    print("📌 Cargando imagen:", path)

    if not os.path.exists(path):
        print("❌ No existe:", path)
        return None

    return path