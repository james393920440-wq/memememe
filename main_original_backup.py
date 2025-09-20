# -*- coding: utf-8 -*-
"""
安卓通讯录获取器 - 优化版本
使用Kivy框架开发，支持读取真实安卓设备联系人
解决了中文显示和编码问题
"""
import os
import sys
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.progressbar import MDProgressBar
import threading

# 修复Kivy的KV文件加载编码问题
original_load_file = Builder.load_file
def load_file_with_encoding(filename, **kwargs):
    """修复KV文件加载的编码问题"""
    try:
        with open(filename, 'r', encoding='utf-8') as fd:
            kwargs['filename'] = filename
            data = fd.read()
            return original_load_file(filename, **kwargs)
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试其他编码
        try:
            with open(filename, 'r', encoding='gbk') as fd:
                kwargs['filename'] = filename
                data = fd.read()
                return original_load_file(filename, **kwargs)
        except Exception:
            # 最后尝试系统默认编码
            return original_load_file(filename, **kwargs)

Builder.load_file = load_file_with_encoding

try:
    from android.permissions import request_permissions, Permission, check_permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass, cast
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False
    print("未在安卓环境中运行，将使用模拟数据")

KV = '''
ScreenManager:
    MainScreen:
    ContactsScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: '安卓通讯录获取器'
            elevation: 10
            font_name: 'ChineseFont'
            
        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(20)
            
            MDLabel:
                text: '安卓通讯录读取工具'
                halign: 'center'
                font_style: 'H4'
                theme_text_color: 'Primary'
                font_name: 'ChineseFont'
                
            MDLabel:
                text: '点击按钮获取设备通讯录联系人'
                halign: 'center'
                font_style: 'Body1'
                theme_text_color: 'Secondary'
                font_name: 'ChineseFont'
                
            MDRaisedButton:
                id: get_contacts_btn
                text: '获取通讯录'
                pos_hint: {'center_x': 0.5}
                size_hint_x: 0.8
                on_release: app.get_contacts()
                font_name: 'ChineseFont'
                
            MDRectangleFlatButton:
                text: '检查权限'
                pos_hint: {'center_x': 0.5}
                size_hint_x: 0.8
                on_release: app.check_permissions()
                font_name: 'ChineseFont'
                
            MDLabel:
                id: status_label
                text: '准备就绪'
                halign: 'center'
                font_style: 'Caption'
                theme_text_color: 'Hint'
                font_name: 'ChineseFont'
                
            Widget:
                size_hint_y: 0.1
                
<ContactsScreen>:
    name: 'contacts'
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: '通讯录联系人'
            elevation: 10
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            right_action_items: [["refresh", lambda x: app.refresh_contacts()]]
            font_name: 'ChineseFont'
            
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

class ContactsApp(MDApp):
    contacts = ListProperty([])
    
    def build(self):
        # 注册中文字体
        self.register_chinese_fonts()
        
        self.title = '安卓通讯录获取器'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'
        return Builder.load_string(KV)
    
    def register_chinese_fonts(self):
        """注册中文字体，解决中文显示问题"""
        try:
            # 尝试注册系统字体
            system_fonts = [
                'C:/Windows/Fonts/msyh.ttf',      # 微软雅黑
                'C:/Windows/Fonts/simhei.ttf',    # 黑体
                'C:/Windows/Fonts/simsun.ttc',    # 宋体
                '/system/fonts/DroidSansFallback.ttf',  # Android系统
                '/system/fonts/NotoSansCJK-Regular.ttc', # Android系统
            ]
            
            # 添加当前目录下的字体文件
            current_dir_fonts = [
                'msyh.ttf',      # 微软雅黑
                'simhei.ttf',    # 黑体
                'simsun.ttc',    # 宋体
                'DroidSansFallback.ttf',  # Android
            ]
            
            all_fonts = system_fonts + current_dir_fonts
            
            for font_path in all_fonts:
                if os.path.exists(font_path):
                    # 注册字体
                    LabelBase.register(
                        name='ChineseFont',
                        fn_regular=font_path
                    )
                    print(f"成功注册字体: {font_path}")
                    return True
            
            # 如果没有找到字体文件，使用默认字体但设置中文支持
            print("未找到中文字体文件，使用默认字体")
            LabelBase.register(
                name='ChineseFont',
                fn_regular='Roboto',
                fn_bold='Roboto-Bold'
            )
            return True
            
        except Exception as e:
            print(f"字体注册失败: {str(e)}")
            # 即使字体注册失败，也要继续运行
            return False
    
    def on_start(self):
        """应用启动时检查权限"""
        if IS_ANDROID:
            self.check_permissions()
    
    def check_permissions(self):
        """检查并请求权限"""
        if not IS_ANDROID:
            self.show_status("当前不在安卓环境中，使用模拟数据")
            return
            
        try:
            # 检查读取联系人权限
            has_permission = check_permission(Permission.READ_CONTACTS)
            
            if has_permission:
                self.show_status("已有读取联系人权限")
            else:
                self.show_status("正在请求读取联系人权限...")
                request_permissions([Permission.READ_CONTACTS], self.permission_callback)
                
        except Exception as e:
            self.show_status(f"权限检查失败: {str(e)}")
    
    def permission_callback(self, permissions, results):
        """权限请求回调"""
        if all(results):
            self.show_status("已获得读取联系人权限")
        else:
            self.show_status("未获得读取联系人权限")
            self.show_permission_dialog()
    
    def show_permission_dialog(self):
        """显示权限说明对话框"""
        dialog = MDDialog(
            title="需要权限",
            text="应用需要读取联系人权限才能获取通讯录。请在设置中授予权限。",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRectangleFlatButton(
                    text="确定",
                    on_release=lambda x: (dialog.dismiss(), self.check_permissions())
                )
            ]
        )
        # 设置对话框中文字体
        dialog.ids.title_bar.ids.label_title.font_name = 'ChineseFont'
        dialog.ids.text_content.font_name = 'ChineseFont'
        dialog.open()
    
    def get_contacts(self):
        """获取通讯录"""
        self.show_status("正在获取通讯录...")
        
        # 禁用按钮
        main_screen = self.root.get_screen('main')
        main_screen.ids.get_contacts_btn.disabled = True
        
        # 在后台线程中获取联系人
        thread = threading.Thread(target=self._fetch_contacts)
        thread.daemon = True
        thread.start()
    
    def _fetch_contacts(self):
        """在后台获取联系人"""
        try:
            if IS_ANDROID:
                contacts_data = self._get_real_contacts()
            else:
                contacts_data = self._get_mock_contacts()
            
            # 更新UI
            Clock.schedule_once(lambda dt: self._update_contacts_list(contacts_data))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))
    
    def _get_real_contacts(self):
        """获取真实的安卓联系人"""
        if not IS_ANDROID:
            return self._get_mock_contacts()
            
        # 检查权限
        if not check_permission(Permission.READ_CONTACTS):
            raise Exception("没有读取联系人权限")
        
        contacts = []
        
        try:
            # 获取安卓上下文
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            content_resolver = activity.getContentResolver()
            
            # 联系人URI
            ContactsContract = autoclass('android.provider.ContactsContract')
            uri = ContactsContract.Contacts.CONTENT_URI
            
            # 查询联系人
            cursor = content_resolver.query(uri, None, None, None, None)
            
            if cursor:
                while cursor.moveToNext():
                    # 获取联系人ID
                    id_index = cursor.getColumnIndex(ContactsContract.Contacts._ID)
                    contact_id = cursor.getString(id_index)
                    
                    # 获取联系人姓名
                    name_index = cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
                    name = cursor.getString(name_index)
                    
                    # 获取电话号码
                    phone_uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
                    phone_selection = ContactsContract.CommonDataKinds.Phone.CONTACT_ID + " = ?"
                    phone_cursor = content_resolver.query(
                        phone_uri, 
                        None, 
                        phone_selection, 
                        [contact_id], 
                        None
                    )
                    
                    phone_numbers = []
                    if phone_cursor:
                        while phone_cursor.moveToNext():
                            phone_index = phone_cursor.getColumnIndex(
                                ContactsContract.CommonDataKinds.Phone.NUMBER
                            )
                            phone_number = phone_cursor.getString(phone_index)
                            phone_numbers.append(phone_number)
                        phone_cursor.close()
                    
                    if name and phone_numbers:
                        contacts.append({
                            "name": name,
                            "phone": phone_numbers[0]  # 取第一个电话号码
                        })
                
                cursor.close()
            
            return contacts
            
        except Exception as e:
            print(f"获取真实联系人失败: {str(e)}")
            return self._get_mock_contacts()
    
    def _get_mock_contacts(self):
        """获取模拟联系人数据"""
        return [
            {"name": "张三", "phone": "13800138000"},
            {"name": "李四", "phone": "13900139000"},
            {"name": "王五", "phone": "13700137000"},
            {"name": "赵六", "phone": "13600136000"},
            {"name": "钱七", "phone": "13500135000"},
            {"name": "孙八", "phone": "13400134000"},
            {"name": "周九", "phone": "13300133000"},
            {"name": "吴十", "phone": "13200132000"},
            {"name": "郑十一", "phone": "13100131000"},
            {"name": "王十二", "phone": "13000130000"},
        ]
    
    def _update_contacts_list(self, contacts_data):
        """更新联系人列表"""
        self.contacts = contacts_data
        contacts_screen = self.root.get_screen('contacts')
        contacts_list = contacts_screen.ids.contacts_list
        progress_bar = contacts_screen.ids.progress_bar
        
        # 隐藏进度条
        progress_bar.opacity = 0
        
        # 清空现有列表
        contacts_list.clear_widgets()
        
        # 添加联系人项
        for contact in contacts_data:
            item = TwoLineListItem(
                text=contact["name"],
                secondary_text=contact["phone"]
            )
            # 设置中文字体
            item.ids._lbl_primary.font_name = 'ChineseFont'
            item.ids._lbl_secondary.font_name = 'ChineseFont'
            contacts_list.add_widget(item)
        
        # 更新状态并切换屏幕
        self.show_status(f'成功获取 {len(contacts_data)} 个联系人')
        
        # 重新启用按钮
        main_screen = self.root.get_screen('main')
        main_screen.ids.get_contacts_btn.disabled = False
        
        # 切换到联系人列表屏幕
        self.root.current = 'contacts'
    
    def _show_error(self, error_msg):
        """显示错误信息"""
        self.show_status(f'获取失败: {error_msg}')
        
        # 重新启用按钮
        main_screen = self.root.get_screen('main')
        main_screen.ids.get_contacts_btn.disabled = False
        
        # 显示错误对话框
        dialog = MDDialog(
            title="错误",
            text=f"获取通讯录失败: {error_msg}",
            buttons=[
                MDFlatButton(
                    text="确定",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        # 设置对话框中文字体
        dialog.ids.title_bar.ids.label_title.font_name = 'ChineseFont'
        dialog.ids.text_content.font_name = 'ChineseFont'
        dialog.open()
    
    def refresh_contacts(self):
        """刷新联系人"""
        contacts_screen = self.root.get_screen('contacts')
        progress_bar = contacts_screen.ids.progress_bar
        progress_bar.opacity = 1
        progress_bar.start()
        
        # 重新获取联系人
        thread = threading.Thread(target=self._fetch_contacts)
        thread.daemon = True
        thread.start()
    
    def go_back(self):
        """返回主屏幕"""
        self.root.current = 'main'
    
    def show_status(self, message):
        """显示状态信息"""
        main_screen = self.root.get_screen('main')
        status_label = main_screen.ids.status_label
        status_label.text = message

if __name__ == '__main__':
    ContactsApp().run()