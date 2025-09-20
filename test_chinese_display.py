# -*- coding: utf-8 -*-
"""
测试Kivy中文显示
"""
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import os

KV = '''
BoxLayout:
    orientation: 'vertical'
    spacing: 10
    padding: 20
    
    Label:
        text: '中文字体测试'
        font_name: 'ChineseFont'
        font_size: '24sp'
        size_hint_y: 0.3
        
    Label:
        text: '这是使用注册字体的中文显示测试'
        font_name: 'ChineseFont'
        font_size: '18sp'
        size_hint_y: 0.3
        
    Label:
        text: '联系人姓名: 张三、李四、王五'
        font_name: 'ChineseFont'
        font_size: '16sp'
        size_hint_y: 0.2
        
    Button:
        text: '测试按钮中文'
        font_name: 'ChineseFont'
        font_size: '16sp'
        size_hint_y: 0.2
        on_release: app.test_button()
'''

class ChineseTestApp(App):
    def build(self):
        self.register_chinese_fonts()
        return Builder.load_string(KV)
    
    def register_chinese_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册系统字体
            system_fonts = [
                'C:/Windows/Fonts/msyh.ttf',      # 微软雅黑
                'C:/Windows/Fonts/simhei.ttf',    # 黑体
                'C:/Windows/Fonts/simsun.ttc',    # 宋体
            ]
            
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    LabelBase.register(
                        name='ChineseFont',
                        fn_regular=font_path
                    )
                    print(f"成功注册字体: {font_path}")
                    return True
            
            print("未找到中文字体文件，使用默认字体")
            LabelBase.register(
                name='ChineseFont',
                fn_regular='Roboto'
            )
            return True
            
        except Exception as e:
            print(f"字体注册失败: {str(e)}")
            return False
    
    def test_button(self):
        print("按钮点击测试成功！")

if __name__ == '__main__':
    ChineseTestApp().run()