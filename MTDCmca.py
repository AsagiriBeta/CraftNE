import zlib
import os
import re
import argparse
import json
import nbtlib
import time
import traceback
from nbtlib.tag import Compound, List, LongArray
from tkinter import Tk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor  # 新增线程池支持
import tempfile

# ---------------------- NBT转换函数（线程安全）----------------------
def nbt_to_python(tag):
    """增强版NBT转换函数，支持更多数据类型"""
    if isinstance(tag, Compound):
        return {key: nbt_to_python(value) for key, value in tag.items()}
    elif isinstance(tag, List):
        return [nbt_to_python(item) for item in tag]
    elif isinstance(tag, (LongArray, nbtlib.tag.ByteArray, nbtlib.tag.IntArray)):
        return list(tag)
    elif hasattr(tag, 'value'):  # 通用数值类型处理
        return tag.value
    else:
        return tag

def convert_chunk_to_json(dat_path, json_path):
    """更健壮的JSON转换函数"""
    temp_path = None
    try:
        nbt_file = nbtlib.load(dat_path)
        data = nbt_to_python(nbt_file)
        
        # 使用mode='w'和encoding确保文本写入
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(json_path), delete=False, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)  # type: ignore
            temp_path = f.name
        
        if os.path.exists(json_path):
            os.remove(json_path)
        os.rename(temp_path, json_path)
        return True
    except Exception as ex:  # 修改为ex避免变量名冲突
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"JSON转换失败: {str(ex)}")
        return False

# ---------------------- 多线程解压处理器 ----------------------
class ChunkProcessor:
    def __init__(self, output_root, convert_json, max_workers=4):
        self.output_root = output_root
        self.convert_json = convert_json
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    # 新增process_mca方法处理单个MCA文件
    def process_mca(self, mca_file_path):
        """处理单个MCA文件"""
        return decompress_mca_file(mca_file_path, self.output_root, self.convert_json)

    def process_chunk(self, x_global, z_global, decompressed_data):
        """处理单个区块"""
        dat_path = os.path.normpath(os.path.join(self.output_root, f"chunk_{x_global}_{z_global}.dat"))
        # 使用原子写入保证数据完整性
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(dat_path), delete=False) as f:
            temp_path = f.name
            f.write(decompressed_data)
        os.replace(temp_path, dat_path)
        print(f"解压成功 -> {dat_path}")

        if self.convert_json:
            # 构造 json_path
            json_path = os.path.splitext(dat_path)[0] + ".json"
            # 使用异步任务提交
            future = self.executor.submit(
                self._convert_task, dat_path, x_global, z_global, json_path
            )
            self.futures.append(future)

    @staticmethod  # 添加静态方法装饰器
    def _convert_task(dat_path, x, z, json_path):
        """优化后的JSON转换任务"""
        try:
            nbt_file = nbtlib.load(dat_path)
            data = nbt_to_python(nbt_file)
            # 使用传入的json_path参数而非外部作用域变量
            with tempfile.NamedTemporaryFile(dir=os.path.dirname(json_path), delete=False, mode='w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                temp_json_path = f.name
            os.replace(temp_json_path, json_path)

            # 仅在JSON写入成功后删除原始 .dat 文件
            if os.path.exists(json_path):
                os.remove(dat_path)
                print(f"JSON转换成功并删除原始文件 -> {json_path}")
            return True
        except Exception as task_ex:  # 修改为task_ex避免变量名冲突
            print(f"转换失败 [{x},{z}]: {str(task_ex)}\n原始文件保留在: {dat_path}")
            return False

    def wait_completion(self):
        self.executor.shutdown(wait=True)
        # 检查任务结果
        for future in self.futures:
            if future.exception():
                print(f"后台任务异常: {future.exception()}")

# ---------------------- 改进后的解压逻辑 ----------------------
def decompress_mca_file(mca_file_path, output_directory, convert_to_json):
    """修改参数名称避免遮蔽外部作用域变量"""
    start_time = time.perf_counter()
    mca_filename = os.path.basename(mca_file_path)
    region_match = re.match(r"r\.(-?\d+)\.(-?\d+)\.mca", mca_filename)
    x_region = int(region_match.group(1))
    z_region = int(region_match.group(2))
    
    processor = ChunkProcessor(output_directory, convert_to_json, max_workers=4)
    
    try:
        with open(mca_file_path, 'rb') as f:
            header = f.read(8192)
            for chunk_index in range(1024):
                x_local = chunk_index % 32
                z_local = chunk_index // 32
                x_global = x_region * 32 + x_local
                z_global = z_region * 32 + z_local

                entry_offset = chunk_index * 4
                entry = header[entry_offset:entry_offset+4]
                offset = (entry[0] << 16 | entry[1] << 8 | entry[2]) * 4096
                sector_count = entry[3]

                if offset == 0 or sector_count == 0:
                    continue

                try:
                    f.seek(offset)
                    chunk_data = f.read(sector_count * 4096)
                    data_length = int.from_bytes(chunk_data[:4], 'big')
                    compression_type = chunk_data[4]
                    compressed_data = chunk_data[5 : 4 + data_length]
                
                    if compression_type == 2:
                        decompressed_data = zlib.decompress(compressed_data)
                    elif compression_type == 1:
                        import gzip
                        decompressed_data = gzip.decompress(compressed_data)
                    elif compression_type == 3:
                        decompressed_data = compressed_data
                    else:
                        continue
                
                    processor.process_chunk(x_global, z_global, decompressed_data)
                
                except Exception as inner_ex:  
                    print(f"区块处理异常: {str(inner_ex)}")
                    continue
    
        processor.wait_completion()  
    finally:
        elapsed = time.perf_counter() - start_time
    
    return elapsed 

def select_mca_files():
    file_dialog_root = Tk()  # 重命名避免变量遮蔽
    file_dialog_root.withdraw()
    files = filedialog.askopenfilenames(
        title="选择Minecraft区域文件",
        filetypes=[("MCA files", "*.mca"), ("All files", "*.*")]
    )
    file_dialog_root.destroy()
    return files

def select_output_dir():
    file_dialog_root = Tk()  # 重命名避免变量遮蔽
    file_dialog_root.withdraw()
    dir_path = filedialog.askdirectory(title="选择输出根目录")
    file_dialog_root.destroy()
    return dir_path

def process_files(mca_paths, output_root, convert_json, threads):
    start_time = time.perf_counter()
    processor = ChunkProcessor(output_root, convert_json, max_workers=threads)
    
    for mca_path in mca_paths:
        print(f"\n正在处理文件: {mca_path}")
        processor.process_mca(mca_path)
    
    processor.wait_completion()
    return time.perf_counter() - start_time

def validate_filename(fname):
    pattern = r"r\.-?\d+\.-?\d+\.mca"
    return re.fullmatch(pattern, fname) is not None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCA批量处理工具")
    parser.add_argument("-i", "--input", nargs='+', help="MCA文件路径列表")
    parser.add_argument("-d", "--dir", help="包含MCA文件的目录")
    parser.add_argument("-o", "--output", help="输出根目录")
    parser.add_argument("-j", "--json", action="store_true", help="生成JSON文件")
    parser.add_argument("-t", "--threads", type=int, default=4, help="并发线程数 (默认: 4)")
    args = parser.parse_args()

    # 命令行模式处理
    if args.input or args.dir:
        if not args.output:
            print("错误：必须指定输出目录(-o/--output)")
            exit(1)
        
        mca_files = []
        # 处理目录
        if args.dir:
            if not os.path.isdir(args.dir):
                print(f"错误：目录不存在 {args.dir}")
                exit(1)
            for dir_root, _, dir_files in os.walk(args.dir):
                for filename in dir_files:
                    if re.match(r"r\.-?\d+\.-?\d+\.mca", filename):
                        mca_files.append(os.path.join(dir_root, filename))
        # 处理文件
        if args.input:
            for file_path in args.input:
                if not os.path.isfile(file_path):
                    print(f"警告：文件不存在 {file_path}")
                    continue
                if not re.match(r"r\.-?\d+\.-?\d+\.mca", os.path.basename(file_path)):
                    print(f"警告：跳过无效文件 {file_path}")
                    continue
                mca_files.append(file_path)
        
        if not mca_files:
            print("错误：未找到有效的MCA文件")
            exit(1)
        
        try:
            total_time = process_files(mca_files, args.output, args.json, args.threads)
            print(f"\n处理完成！总耗时: {total_time:.2f}秒")
            print(f"输出目录: {os.path.abspath(args.output)}")
        except Exception as e:
            print(f"处理失败: {str(e)}")
            traceback.print_exc()
    
    # GUI模式处理
    else:
        root = Tk()
        root.withdraw()
        
        # 修改变量名避免隐藏外部作用域变量
        selected_mca_files = filedialog.askopenfilenames(
            title="选择Minecraft区域文件（可多选）",
            filetypes=[("MCA files", "*.mca"), ("All files", "*.*")]
        )
        if not selected_mca_files:
            messagebox.showinfo("信息", "已取消选择文件")
            exit()
        
        # 验证文件格式
        invalid_files = []
        for path in selected_mca_files:
            if not re.fullmatch(r"r\.-?\d+\.-?\d+\.mca", os.path.basename(path)):
                invalid_files.append(os.path.basename(path))
        if invalid_files:
            messagebox.showerror("错误", "以下文件格式无效:\n" + "\n".join(invalid_files))
            exit()
        
        # 选择输出目录
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            messagebox.showinfo("信息", "已取消选择输出目录")
            exit()
        
        # 修改变量名避免隐藏外部作用域变量
        convert_json_flag = messagebox.askyesno("选项", "是否要转换为JSON文件？")
        
        try:
            total_time = process_files(selected_mca_files, output_dir, convert_json_flag, threads=4)
            message = f"处理完成！\n总耗时: {total_time:.2f}秒\n输出目录: {output_dir}"
            messagebox.showinfo("完成", message)
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中出现异常:\n{str(e)}")
            traceback.print_exc()
        finally:
            root.destroy()