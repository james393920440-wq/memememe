# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.core.window import Window
import os

# 设置窗口大小
Window.size = (300, 200)

# 注册系统黑体字体
font_path = "C:\\WINDOWS\\Fonts\\simhei.ttf"
if os.path.exists(font_path):
    LabelBase.register(name='SimHei', fn_regular=font_path)
    print(f"成功注册字体: {font_path}")
    font_name = 'SimHei'
else:
    print(f"字体文件不存在: {font_path}")
    font_name = 'Roboto'

class TestFontApp(App):
    def build(self):
        self.title = "字体测试"
        
        # 测试标签
        label = Label(
            text='中文测试：张三\nEnglish Test: ABC',
            font_size='20sp',
            font_name=font_name,
            halign='center',
            valign='middle'
        )
        label.bind(size=label.setter('text_size'))
        
        return label

if __name__ == "__main__":
    TestFontApp().run()