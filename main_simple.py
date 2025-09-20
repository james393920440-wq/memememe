# -*- coding: utf-8 -*-
"""
超简单通讯录应用 - 避免构建错误
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import json

try:
    from android.permissions import request_permissions, Permission
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

class SimpleContactsApp(App):
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # 标题
        title_label = Label(
            text='通讯录获取器',
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
        
        # 获取联系人按钮
        get_button = Button(
            text='获取通讯录',
            size_hint_y=0.3,
            font_size='18sp'
        )
        get_button.bind(on_press=self.get_contacts)
        main_layout.add_widget(get_button)
        
        # 检查权限按钮
        check_button = Button(
            text='检查权限',
            size_hint_y=0.2,
            font_size='16sp'
        )
        check_button.bind(on_press=self.check_permissions)
        main_layout.add_widget(check_button)
        
        return main_layout
    
    def on_start(self):
        if IS_ANDROID:
            Clock.schedule_once(lambda dt: self.check_permissions(), 0.5)
    
    def check_permissions(self, instance=None):
        """检查权限"""
        if not IS_ANDROID:
            self.status_label.text = "当前不在安卓环境中"
            return
            
        try:
            from android.permissions import check_permission
            has_permission = check_permission(Permission.READ_CONTACTS)
            
            if has_permission:
                self.status_label.text = "已有读取联系人权限"
            else:
                self.status_label.text = "正在请求权限..."
                request_permissions([Permission.READ_CONTACTS], self.permission_callback)
                
        except Exception as e:
            self.status_label.text = f"权限检查失败: {str(e)}"
    
    def permission_callback(self, permissions, results):
        """权限回调"""
        if all(results):
            self.status_label.text = "已获得读取联系人权限"
        else:
            self.status_label.text = "未获得读取联系人权限"
    
    def get_contacts(self, instance):
        """获取联系人"""
        if not IS_ANDROID:
            self.status_label.text = "请在真实安卓设备上运行"
            self.show_mock_contacts()
            return
            
        try:
            from android.permissions import check_permission
            if not check_permission(Permission.READ_CONTACTS):
                self.status_label.text = "请先授予读取联系人权限"
                self.check_permissions()
                return
            
            self.status_label.text = "正在获取通讯录..."
            
            # 简单获取联系人
            contacts = self._get_simple_contacts()
            
            if contacts:
                self.status_label.text = f"已获取 {len(contacts)} 个联系人"
                self.show_contacts(contacts)
            else:
                self.status_label.text = "未找到联系人"
                
        except Exception as e:
            self.status_label.text = f"获取失败: {str(e)}"
    
    def _get_simple_contacts(self):
        """简单获取联系人"""
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            content_resolver = activity.getContentResolver()
            
            ContactsContract = autoclass('android.provider.ContactsContract')
            uri = ContactsContract.Contacts.CONTENT_URI
            
            # 查询基本字段
            projection = [
                ContactsContract.Contacts._ID,
                ContactsContract.Contacts.DISPLAY_NAME
            ]
            
            cursor = content_resolver.query(uri, projection, None, None, None)
            
            contacts = []
            if cursor:
                while cursor.moveToNext():
                    try:
                        name_index = cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
                        name = cursor.getString(name_index) or "未知姓名"
                        
                        contacts.append({
                            'name': name,
                            'phone': '未知号码'
                        })
                        
                    except Exception as e:
                        continue
                
                cursor.close()
            
            return contacts
            
        except Exception as e:
            print(f"获取联系人失败: {str(e)}")
            return self._get_mock_contacts()
    
    def _get_mock_contacts(self):
        """模拟联系人数据"""
        return [
            {'name': '张三', 'phone': '13800138000'},
            {'name': '李四', 'phone': '13900139000'},
            {'name': '王五', 'phone': '13700137000'},
        ]
    
    def show_contacts(self, contacts):
        """显示联系人"""
        # 简单显示联系人信息
        contact_text = "联系人列表:\n"
        for contact in contacts[:10]:  # 只显示前10个
            contact_text += f"- {contact['name']}: {contact['phone']}\n"
        
        if len(contacts) > 10:
            contact_text += f"... 还有 {len(contacts) - 10} 个联系人"
        
        # 创建简单的结果显示
        result_layout = BoxLayout(orientation='vertical', padding=10)
        result_label = Label(
            text=contact_text,
            font_size='14sp',
            text_size=(400, None)
        )
        result_layout.add_widget(result_label)
        
        close_button = Button(text='关闭', size_hint_y=0.2)
        close_button.bind(on_press=lambda x: self.remove_result_popup(result_layout))
        result_layout.add_widget(close_button)
        
        # 添加到当前界面
        self.root.add_widget(result_layout)
        result_layout.id = 'result_popup'
    
    def remove_result_popup(self, popup):
        """移除结果弹窗"""
        self.root.remove_widget(popup)
    
    def show_mock_contacts(self):
        """显示模拟联系人"""
        contacts = self._get_mock_contacts()
        self.show_contacts(contacts)

if __name__ == '__main__':
    SimpleContactsApp().run()