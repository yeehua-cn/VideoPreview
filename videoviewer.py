import os
import tkinter as tk
from tkinter import ttk, filedialog, Listbox, Scrollbar, messagebox
from tkinter.constants import END, BOTH, RIGHT, LEFT, Y, BOTTOM, X

SUPPORTED_FORMATS = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm')

class VideoPreviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频预览工具")
        self.root.geometry("800x600")

        # 创建界面组件
        self.create_widgets()
        self.current_folder = ""

    def create_widgets(self):
        # 顶部按钮框架
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        # 选择文件夹按钮
        self.select_btn = ttk.Button(
            btn_frame,
            text="选择文件夹",
            command=self.select_folder
        )
        self.select_btn.pack(side=LEFT, padx=5)

        # 文件列表框架
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # 滚动条
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        # 文件列表
        self.file_list = Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            font=('Arial', 12),
            bg='#f0f0f0'
        )
        self.file_list.pack(fill=BOTH, expand=True)
        scrollbar.config(command=self.file_list.yview)

        # 绑定双击事件
        self.file_list.bind('<Double-1>', self.play_selected)

        # 底部状态栏
        self.status = ttk.Label(
            self.root,
            text="就绪",
            anchor=tk.W,
            relief=tk.SUNKEN
        )
        self.status.pack(side=BOTTOM, fill=X)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_folder = folder
            self.update_file_list(folder)
            self.status.config(text=f"当前文件夹：{folder}")

    def update_file_list(self, folder):
        self.file_list.delete(0, END)
        try:
            files = os.listdir(folder)
            video_files = [
                f for f in files
                if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS
            ]
            for f in sorted(video_files):
                self.file_list.insert(END, f)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件夹：{e}")

    def play_selected(self, event):
        selection = self.file_list.curselection()
        if not selection:
            return

        selected_file = self.file_list.get(selection[0])
        full_path = os.path.join(self.current_folder, selected_file)

        if not os.path.exists(full_path):
            messagebox.showerror("错误", "文件不存在！")
            return

        try:
            # 使用系统默认播放器打开
            if os.name == 'nt':  # Windows
                os.startfile(full_path)
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', full_path))
            self.status.config(text=f"正在播放：{selected_file}")
        except Exception as e:
            messagebox.showerror("错误", f"无法播放视频：{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPreviewApp(root)
    root.mainloop()
