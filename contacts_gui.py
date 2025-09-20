# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import threading
import time

class ContactsGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("通讯录获取器")
        self.root.geometry("400x600")
        
        # 设置字体
        self.font_title = ("Microsoft YaHei", 16, "bold")
        self.font_normal = ("Microsoft YaHei", 12)
        self.font_small = ("Microsoft YaHei", 10)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 标题
        title_label = tk.Label(self.root, text="通讯录获取器", font=self.font_title, fg="#2E4BC7")
        title_label.pack(pady=20)
        
        # 获取按钮
        self.get_btn = tk.Button(
            self.root, 
            text="获取通讯录", 
            font=self.font_normal,
            bg="#2E4BC7",
            fg="white",
            command=self.get_contacts,
            width=15,
            height=2
        )
        self.get_btn.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(
            self.root, 
            text="点击按钮获取通讯录联系人", 
            font=self.font_small,
            fg="#666666"
        )
        self.status_label.pack(pady=10)
        
        # 创建框架和滚动条
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建树形视图来显示联系人
        self.tree = ttk.Treeview(frame, columns=('电话',), height=15)
        self.tree.heading('#0', text='姓名')
        self.tree.heading('电话', text='电话')
        self.tree.column('#0', width=150)
        self.tree.column('电话', width=200)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def get_contacts(self):
        """获取通讯录"""
        self.get_btn.config(state=tk.DISABLED)
        self.status_label.config(text="正在获取通讯录...", fg="#2E4BC7")
        self.tree.delete(*self.tree.get_children())
        
        # 使用线程模拟异步获取数据
        thread = threading.Thread(target=self.simulate_get_contacts)
        thread.daemon = True
        thread.start()
        
    def simulate_get_contacts(self):
        """模拟获取通讯录数据"""
        time.sleep(1)  # 模拟网络延迟
        
        # 模拟联系人数据
        contacts = [
            {'name': '张三', 'phone': '13800138000'},
            {'name': '李四', 'phone': '13900139000'},
            {'name': '王五', 'phone': '13700137000'},
            {'name': '赵六', 'phone': '13600136000'},
            {'name': '孙七', 'phone': '13500135000'},
            {'name': '周八', 'phone': '13400134000'},
            {'name': '吴九', 'phone': '13300133000'},
            {'name': '郑十', 'phone': '13200132000'}
        ]
        
        # 在主线程中更新UI
        self.root.after(0, self.update_contacts_list, contacts)
        
    def update_contacts_list(self, contacts):
        """更新联系人列表"""
        for contact in contacts:
            self.tree.insert('', tk.END, text=contact['name'], values=(contact['phone'],))
        
        self.status_label.config(text=f"共找到 {len(contacts)} 个联系人", fg="#666666")
        self.get_btn.config(state=tk.NORMAL)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ContactsGUI()
    app.run()