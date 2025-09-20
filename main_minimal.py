# -*- coding: utf-8 -*-
"""
最简化的通讯录应用 - 确保构建成功
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class MinimalContactsApp(App):
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # 标题
        title_label = Label(
            text='极简通讯录',
            font_size='24sp',
            size_hint_y=0.3
        )
        main_layout.add_widget(title_label)
        
        # 状态标签
        self.status_label = Label(
            text='准备就绪',
            font_size='16sp',
            size_hint_y=0.2
        )
        main_layout.add_widget(self.status_label)
        
        # 模拟获取按钮
        get_button = Button(
            text='获取模拟通讯录',
            size_hint_y=0.3,
            font_size='18sp'
        )
        get_button.bind(on_press=self.get_mock_contacts)
        main_layout.add_widget(get_button)
        
        return main_layout
    
    def get_mock_contacts(self, instance):
        """获取模拟联系人数据"""
        self.status_label.text = '正在获取...'
        
        # 模拟联系人数据
        contacts = [
            {'name': '张三', 'phone': '13800138000'},
            {'name': '李四', 'phone': '13900139000'},
            {'name': '王五', 'phone': '13700137000'},
            {'name': '赵六', 'phone': '13600136000'},
            {'name': '钱七', 'phone': '13500135000'},
        ]
        
        # 显示结果
        contact_text = f"已获取 {len(contacts)} 个联系人:\n\n"
        for contact in contacts:
            contact_text += f"• {contact['name']}: {contact['phone']}\n"
        
        self.status_label.text = contact_text
        self.status_label.text_size = (400, None)  # 自动换行
        
        # 添加重置按钮
        if not hasattr(self, 'reset_button'):
            self.reset_button = Button(
                text='重新获取',
                size_hint_y=0.2,
                font_size='16sp'
            )
            self.reset_button.bind(on_press=self.reset_app)
            self.root.add_widget(self.reset_button)
    
    def reset_app(self, instance):
        """重置应用"""
        self.status_label.text = '准备就绪'
        self.status_label.text_size = None
        if hasattr(self, 'reset_button'):
            self.root.remove_widget(self.reset_button)
            delattr(self, 'reset_button')

if __name__ == '__main__':
    MinimalContactsApp().run()