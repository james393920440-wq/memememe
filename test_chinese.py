# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox

def show_chinese():
    root = tk.Tk()
    root.title("中文测试")
    root.geometry("400x300")
    
    label = tk.Label(root, text="通讯录获取器", font=("Microsoft YaHei", 16))
    label.pack(pady=20)
    
    contacts = ["张三 - 13800138000", "李四 - 13900139000", "王五 - 13700137000"]
    
    for contact in contacts:
        contact_label = tk.Label(root, text=contact, font=("Microsoft YaHei", 12))
        contact_label.pack(pady=5)
    
    button = tk.Button(root, text="关闭", command=root.destroy, font=("Microsoft YaHei", 12))
    button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    show_chinese()