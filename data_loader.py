import os
import json

class MinecraftDataLoader:
    def __init__(self, folder_path, cube_size=8):
        self.folder_path = folder_path
        self.cube_size = cube_size

    def load_data(self):
        data = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    cube = self.create_cube(json_data)
                    data.append(cube)
        return data

    def create_cube(self, chunk):
        size = self.cube_size
        cube = [[[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
        
        for block in chunk.get('Blocks', []):
            x, y, z = self.normalize_position(
                block['x'], 
                block['y'], 
                block['z']
            )
            if 0 <= x < size and 0 <= y < size and 0 <= z < size:
                cube[x][y][z] = block['id']
        
        return cube

    def normalize_position(self, x, y, z):
        size = self.cube_size
        return (
            (x % size + size) % size,
            (y % size + size) % size,
            (z % size + size) % size
        )