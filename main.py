# -*- coding: utf-8 -*-
"""
安卓通讯录获取器 - 稳定版本
简化版本，避免闪退问题
"""
import os
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.toast import toast
import threading

try:
    from android.permissions import request_permissions, Permission, check_permission
    from jnius import autoclass
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False
    print("未在安卓环境中运行")

KV = '''
ScreenManager:
    MainScreen:
    ContactsScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: '通讯录获取器'
            elevation: 10
            
        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(20)
            
            MDLabel:
                text: '安卓通讯录读取工具'
                halign: 'center'
                font_style: 'H5'
                theme_text_color: 'Primary'
                
            MDRaisedButton:
                id: get_contacts_btn
                text: '获取通讯录'
                pos_hint: {'center_x': 0.5}
                size_hint_x: 0.8
                on_release: app.get_contacts()
                
            MDRectangleFlatButton:
                text: '检查权限'
                pos_hint: {'center_x': 0.5}
                size_hint_x: 0.8
                on_release: app.check_permissions()
                
            MDLabel:
                id: status_label
                text: '准备就绪'
                halign: 'center'
                font_style: 'Caption'
                theme_text_color: 'Hint'
                
<ContactsScreen>:
    name: 'contacts'
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: '通讯录联系人'
            elevation: 10
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            
        ScrollView:
            MDList:
                id: contacts_list
                padding: dp(10)
                
        MDProgressBar:
            id: progress_bar
            type: "indeterminate"
            size_hint_y: None
            height: dp(4)
            opacity: 0
'''

class MainScreen(Screen):
    pass

class ContactsScreen(Screen):
    pass

class ContactItem(TwoLineAvatarListItem):
    def __init__(self, contact_data, **kwargs):
        super().__init__(**kwargs)
        self.contact_data = contact_data
        self.text = contact_data.get('name', '未知')
        self.secondary_text = contact_data.get('phone', '无电话号码')

class ContactsApp(MDApp):
    contacts = ListProperty([])
    
    def build(self):
        self.title = "通讯录获取器"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)
    
    def on_start(self):
        if IS_ANDROID:
            Clock.schedule_once(lambda dt: self.check_permissions(), 0.5)
    
    def check_permissions(self):
        """检查并请求权限"""
        if not IS_ANDROID:
            self.show_status("当前不在安卓环境中")
            return
            
        try:
            has_permission = check_permission(Permission.READ_CONTACTS)
            
            if has_permission:
                self.show_status("已有读取联系人权限")
            else:
                self.show_status("正在请求权限...")
                request_permissions([Permission.READ_CONTACTS], self.permission_callback)
                
        except Exception as e:
            self.show_status(f"权限检查失败: {str(e)}")
    
    def permission_callback(self, permissions, results):
        """权限请求回调"""
        if all(results):
            self.show_status("已获得读取联系人权限")
            toast("已获得权限")
        else:
            self.show_status("未获得读取联系人权限")
    
    def get_contacts(self):
        """获取通讯录"""
        if not IS_ANDROID:
            self.show_status("请在真实安卓设备上运行")
            self.show_mock_contacts()
            return
            
        if not check_permission(Permission.READ_CONTACTS):
            self.show_status("请先授予读取联系人权限")
            self.check_permissions()
            return
        
        self.show_status("正在获取通讯录...")
        
        # 显示进度条
        contacts_screen = self.root.get_screen('contacts')
        contacts_screen.ids.progress_bar.opacity = 1
        contacts_screen.ids.progress_bar.start()
        
        # 在后台线程中获取联系人
        thread = threading.Thread(target=self._fetch_contacts_safe)
        thread.daemon = True
        thread.start()
    
    def _fetch_contacts_safe(self):
        """安全地获取联系人（简化版）"""
        try:
            contacts_data = self._get_simple_contacts()
            
            # 更新UI
            Clock.schedule_once(lambda dt: self._update_contacts_list(contacts_data))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))
    
    def _get_simple_contacts(self):
        """获取简化的联系人信息"""
        if not IS_ANDROID:
            return self._get_mock_contacts()
            
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            content_resolver = activity.getContentResolver()
            
            ContactsContract = autoclass('android.provider.ContactsContract')
            uri = ContactsContract.Contacts.CONTENT_URI
            
            # 只查询基本字段
            projection = [
                ContactsContract.Contacts._ID,
                ContactsContract.Contacts.DISPLAY_NAME,
                ContactsContract.Contacts.HAS_PHONE_NUMBER
            ]
            
            cursor = content_resolver.query(uri, projection, None, None, None)
            
            contacts = []
            if cursor:
                while cursor.moveToNext():
                    try:
                        id_index = cursor.getColumnIndex(ContactsContract.Contacts._ID)
                        name_index = cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
                        has_phone_index = cursor.getColumnIndex(ContactsContract.Contacts.HAS_PHONE_NUMBER)
                        
                        contact_id = cursor.getString(id_index)
                        name = cursor.getString(name_index) or "未知姓名"
                        has_phone = cursor.getInt(has_phone_index)
                        
                        # 获取第一个电话号码
                        phone = ""
                        if has_phone > 0:
                            phone = self._get_first_phone(contact_id, content_resolver, ContactsContract)
                        
                        contacts.append({
                            'id': contact_id,
                            'name': name,
                            'phone': phone
                        })
                        
                    except Exception as e:
                        print(f"处理联系人失败: {str(e)}")
                        continue
                
                cursor.close()
            
            return contacts
            
        except Exception as e:
            print(f"获取联系人失败: {str(e)}")
            return self._get_mock_contacts()
    
    def _get_first_phone(self, contact_id, content_resolver, ContactsContract):
        """获取第一个电话号码"""
        try:
            phone_uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
            phone_selection = ContactsContract.CommonDataKinds.Phone.CONTACT_ID + " = ?"
            phone_cursor = content_resolver.query(
                phone_uri, 
                [ContactsContract.CommonDataKinds.Phone.NUMBER],
                phone_selection, 
                [contact_id], 
                None
            )
            
            if phone_cursor and phone_cursor.moveToFirst():
                phone_index = phone_cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                phone = phone_cursor.getString(phone_index) or ""
                phone_cursor.close()
                return phone
                
            if phone_cursor:
                phone_cursor.close()
                
        except Exception as e:
            print(f"获取电话号码失败: {str(e)}")
        
        return ""
    
    def _get_mock_contacts(self):
        """模拟联系人数据"""
        return [
            {'id': '1', 'name': '张三', 'phone': '13800138000'},
            {'id': '2', 'name': '李四', 'phone': '13900139000'},
            {'id': '3', 'name': '王五', 'phone': '13700137000'},
        ]
    
    def _update_contacts_list(self, contacts):
        """更新联系人列表"""
        contacts_screen = self.root.get_screen('contacts')
        contacts_screen.ids.progress_bar.opacity = 0
        contacts_screen.ids.progress_bar.stop()
        
        contacts_list = contacts_screen.ids.contacts_list
        contacts_list.clear_widgets()
        
        if not contacts:
            self.show_status("未找到联系人")
            return
        
        for contact in contacts:
            try:
                item = ContactItem(contact)
                contacts_list.add_widget(item)
            except Exception as e:
                print(f"添加联系人失败: {str(e)}")
                continue
        
        self.contacts = contacts
        self.root.current = 'contacts'
        self.show_status(f"已获取 {len(contacts)} 个联系人")
    
    def _show_error(self, error_msg):
        """显示错误信息"""
        contacts_screen = self.root.get_screen('contacts')
        contacts_screen.ids.progress_bar.opacity = 0
        contacts_screen.ids.progress_bar.stop()
        
        self.show_status(f"获取失败: {error_msg}")
        
        # 显示错误对话框
        dialog = MDDialog(
            title="错误",
            text=f"获取联系人失败: {error_msg}",
            buttons=[
                MDFlatButton(
                    text="确定",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_mock_contacts(self):
        """显示模拟联系人"""
        contacts = self._get_mock_contacts()
        self._update_contacts_list(contacts)
    
    def go_back(self):
        """返回主界面"""
        self.root.current = 'main'
    
    def show_status(self, message):
        """显示状态信息"""
        try:
            main_screen = self.root.get_screen('main')
            main_screen.ids.status_label.text = message
        except:
            pass

if __name__ == '__main__':
    ContactsApp().run()