import os
from nbtlib import nbt

class MinecraftDataLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def load_data(self):
        data = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.mca'):
                    region_file = nbt.load(os.path.join(root, file))
                    chunks = self.extract_chunks(region_file)
                    data.extend(chunks)
        return data

    def extract_chunks(self, region_file):
        chunks = []
        for chunk in region_file['Chunks']:
            blocks = self.extract_blocks(chunk)
            chunks.extend(blocks)
        return chunks

    @staticmethod
    def extract_blocks(chunk):
        blocks = []
        for block in chunk['Blocks']:
            block_data = {
                'type': block['id'].value,
                'state': block['state'].value,
                'position': (block['x'].value, block['y'].value, block['z'].value)
            }
            blocks.append(block_data)
        return blocks