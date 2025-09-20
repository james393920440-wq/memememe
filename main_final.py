# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
import threading
import time

class ContactsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("通讯录获取器")
        self.root.geometry("400x500")
        
        # 配置样式
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 按钮样式
        style.configure(
            'GetContacts.TButton',
            font=('Microsoft YaHei', 12, 'bold'),
            background='#2E4BC7',
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=10
        )
        style.map('GetContacts.TButton', background=[('active', '#1E3CB7')])
        
        # 标签样式
        style.configure(
            'Title.TLabel',
            font=('Microsoft YaHei', 18, 'bold'),
            foreground='#2E4BC7'
        )
        
        style.configure(
            'Status.TLabel',
            font=('Microsoft YaHei', 10),
            foreground='#666666'
        )
        
        # 树形视图样式
        style.configure(
            'Contacts.Treeview',
            font=('Microsoft YaHei', 11),
            rowheight=25
        )
        
        style.configure(
            'Contacts.Treeview.Heading',
            font=('Microsoft YaHei', 12, 'bold'),
            background='#F0F0F0',
            foreground='#333333'
        )
        
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="通讯录获取器",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # 获取按钮
        self.get_btn = ttk.Button(
            main_frame,
            text="获取通讯录",
            style='GetContacts.TButton',
            command=self.get_contacts
        )
        self.get_btn.pack(pady=(0, 15))
        
        # 状态标签
        self.status_label = ttk.Label(
            main_frame,
            text="点击按钮获取通讯录联系人",
            style='Status.TLabel'
        )
        self.status_label.pack(pady=(0, 15))
        
        # 联系人列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图来显示联系人
        self.tree = ttk.Treeview(
            list_frame,
            columns=('phone',),
            style='Contacts.Treeview',
            height=15
        )
        
        # 设置列
        self.tree.heading('#0', text='姓名', anchor=tk.W)
        self.tree.heading('phone', text='电话', anchor=tk.W)
        self.tree.column('#0', width=150, anchor=tk.W)
        self.tree.column('phone', width=200, anchor=tk.W)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def get_contacts(self):
        """获取通讯录"""
        self.get_btn.config(state=tk.DISABLED)
        self.status_label.config(text="正在获取通讯录...")
        
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
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
            self.tree.insert(
                '', 
                tk.END, 
                text=contact['name'], 
                values=(contact['phone'],)
            )
        
        self.status_label.config(text=f"共找到 {len(contacts)} 个联系人")
        self.get_btn.config(state=tk.NORMAL)
        
    def run(self):
        """运行应用"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ContactsApp()
    app.run()