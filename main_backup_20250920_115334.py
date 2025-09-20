# -*- coding: utf-8 -*-
"""
安卓通讯录获取器 - 增强版本
支持真实Android设备联系人读取，包含头像、邮箱等完整信息
"""
import os
import sys
import csv
import json
from datetime import datetime
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.image import Image as CoreImage
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarListItem, ThreeLineAvatarListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
import threading
from io import BytesIO

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
        try:
            with open(filename, 'r', encoding='gbk') as fd:
                kwargs['filename'] = filename
                data = fd.read()
                return original_load_file(filename, **kwargs)
        except Exception:
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
    ContactDetailScreen:

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
                text: '支持读取联系人头像、邮箱、电话等完整信息'
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
                
            MDRectangleFlatButton:
                text: '导出联系人'
                pos_hint: {'center_x': 0.5}
                size_hint_x: 0.8
                on_release: app.show_export_dialog()
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
            right_action_items: [["refresh", lambda x: app.refresh_contacts()], ["magnify", lambda x: app.show_search_dialog()]]
            font_name: 'ChineseFont'
            
        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_height: True
            padding: dp(10)
            spacing: dp(10)
            
            MDTextField:
                id: search_field
                hint_text: '搜索联系人...'
                mode: "fill"
                size_hint_x: 0.7
                font_name: 'ChineseFont'
                on_text: app.filter_contacts(self.text)
                
            MDRaisedButton:
                text: '筛选'
                size_hint_x: 0.3
                on_release: app.show_filter_menu(self)
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
            
<ContactDetailScreen>:
    name: 'contact_detail'
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: '联系人详情'
            elevation: 10
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            font_name: 'ChineseFont'
            
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                adaptive_height: True
                
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_height: True
                    spacing: dp(15)
                    
                    AsyncImage:
                        id: contact_avatar
                        source: ''
                        size_hint: None, None
                        size: dp(80), dp(80)
                        pos_hint: {'center_y': 0.5}
                        
                    MDBoxLayout:
                        orientation: 'vertical'
                        adaptive_height: True
                        spacing: dp(5)
                        
                        MDLabel:
                            id: contact_name
                            text: ''
                            font_style: 'H5'
                            theme_text_color: 'Primary'
                            font_name: 'ChineseFont'
                            
                        MDLabel:
                            id: contact_company
                            text: ''
                            font_style: 'Body2'
                            theme_text_color: 'Secondary'
                            font_name: 'ChineseFont'
                            
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    spacing: dp(10)
                    
                    MDLabel:
                        text: '电话'
                        font_style: 'Subtitle2'
                        theme_text_color: 'Primary'
                        font_name: 'ChineseFont'
                        
                    MDList:
                        id: phone_list
                        
                    MDLabel:
                        text: '邮箱'
                        font_style: 'Subtitle2'
                        theme_text_color: 'Primary'
                        font_name: 'ChineseFont'
                        
                    MDList:
                        id: email_list
                        
                    MDLabel:
                        text: '地址'
                        font_style: 'Subtitle2'
                        theme_text_color: 'Primary'
                        font_name: 'ChineseFont'
                        
                    MDLabel:
                        id: contact_address
                        text: ''
                        font_style: 'Body1'
                        theme_text_color: 'Secondary'
                        font_name: 'ChineseFont'
                        
                MDRectangleFlatButton:
                    text: '添加到收藏'
                    pos_hint: {'center_x': 0.5}
                    on_release: app.add_to_favorites()
                    font_name: 'ChineseFont'
'''

class MainScreen(Screen):
    pass

class ContactsScreen(Screen):
    pass

class ContactDetailScreen(Screen):
    pass

class EnhancedContactsApp(MDApp):
    contacts = ListProperty([])
    all_contacts = ListProperty([])
    current_contact = StringProperty('')
    favorites = ListProperty([])
    
    def build(self):
        # 注册中文字体
        self.register_chinese_fonts()
        
        self.title = '安卓通讯录获取器'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'
        
        # 初始化文件管理器
        self.file_manager = None
        
        return Builder.load_string(KV)
    
    def register_chinese_fonts(self):
        """注册中文字体"""
        try:
            system_fonts = [
                'C:/Windows/Fonts/msyh.ttf',
                'C:/Windows/Fonts/simhei.ttf',
                'C:/Windows/Fonts/simsun.ttc',
                '/system/fonts/DroidSansFallback.ttf',
                '/system/fonts/NotoSansCJK-Regular.ttc',
            ]
            
            current_dir_fonts = ['msyh.ttf', 'simhei.ttf', 'simsun.ttc', 'DroidSansFallback.ttf']
            all_fonts = system_fonts + current_dir_fonts
            
            for font_path in all_fonts:
                if os.path.exists(font_path):
                    LabelBase.register(name='ChineseFont', fn_regular=font_path)
                    print(f"成功注册字体: {font_path}")
                    return True
            
            LabelBase.register(name='ChineseFont', fn_regular='Roboto')
            return True
            
        except Exception as e:
            print(f"字体注册失败: {str(e)}")
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
            toast("已获得读取联系人权限")
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
        dialog.ids.title_bar.ids.label_title.font_name = 'ChineseFont'
        dialog.ids.text_content.font_name = 'ChineseFont'
        dialog.open()
    
    def get_contacts(self):
        """获取通讯录"""
        self.show_status("正在获取通讯录...")
        
        # 禁用按钮
        main_screen = self.root.get_screen('main')
        main_screen.ids.get_contacts_btn.disabled = True
        
        # 显示进度条
        contacts_screen = self.root.get_screen('contacts')
        contacts_screen.ids.progress_bar.opacity = 1
        contacts_screen.ids.progress_bar.start()
        
        # 在后台线程中获取联系人
        thread = threading.Thread(target=self._fetch_contacts)
        thread.daemon = True
        thread.start()
    
    def _fetch_contacts(self):
        """在后台获取联系人"""
        try:
            if IS_ANDROID:
                contacts_data = self._get_real_contacts_enhanced()
            else:
                contacts_data = self._get_mock_contacts_enhanced()
            
            # 更新UI
            Clock.schedule_once(lambda dt: self._update_contacts_list(contacts_data))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))
    
    def _get_real_contacts_enhanced(self):
        """获取增强的真实安卓联系人信息"""
        if not IS_ANDROID:
            return self._get_mock_contacts_enhanced()
            
        if not check_permission(Permission.READ_CONTACTS):
            raise Exception("没有读取联系人权限")
        
        contacts = []
        
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            content_resolver = activity.getContentResolver()
            
            ContactsContract = autoclass('android.provider.ContactsContract')
            uri = ContactsContract.Contacts.CONTENT_URI
            
            # 查询所有联系人
            cursor = content_resolver.query(uri, None, None, None, None)
            
            if cursor:
                while cursor.moveToNext():
                    contact_info = self._extract_contact_info(cursor, content_resolver, ContactsContract)
                    if contact_info:
                        contacts.append(contact_info)
                
                cursor.close()
            
            return contacts
            
        except Exception as e:
            print(f"获取真实联系人失败: {str(e)}")
            return self._get_mock_contacts_enhanced()
    
    def _extract_contact_info(self, cursor, content_resolver, ContactsContract):
        """提取单个联系人的完整信息"""
        try:
            # 获取联系人ID
            id_index = cursor.getColumnIndex(ContactsContract.Contacts._ID)
            contact_id = cursor.getString(id_index)
            
            # 获取基本信息
            name_index = cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
            name = cursor.getString(name_index) or "未知姓名"
            
            # 获取头像信息
            photo_uri_index = cursor.getColumnIndex(ContactsContract.Contacts.PHOTO_URI)
            photo_uri = cursor.getString(photo_uri_index) or ""
            
            # 获取电话号码
            phone_numbers = self._get_contact_phones(contact_id, content_resolver, ContactsContract)
            
            # 获取邮箱地址
            email_addresses = self._get_contact_emails(contact_id, content_resolver, ContactsContract)
            
            # 获取地址信息
            addresses = self._get_contact_addresses(contact_id, content_resolver, ContactsContract)
            
            # 获取公司信息
            company = self._get_contact_company(contact_id, content_resolver, ContactsContract)
            
            return {
                "id": contact_id,
                "name": name,
                "phone": phone_numbers[0] if phone_numbers else "",
                "phones": phone_numbers,
                "emails": email_addresses,
                "addresses": addresses,
                "company": company,
                "photo_uri": photo_uri,
                "avatar": None  # 将在需要时加载
            }
            
        except Exception as e:
            print(f"提取联系人信息失败: {str(e)}")
            return None
    
    def _get_contact_phones(self, contact_id, content_resolver, ContactsContract):
        """获取联系人电话号码"""
        phone_numbers = []
        try:
            phone_uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
            phone_selection = ContactsContract.CommonDataKinds.Phone.CONTACT_ID + " = ?"
            phone_cursor = content_resolver.query(phone_uri, None, phone_selection, [contact_id], None)
            
            if phone_cursor:
                while phone_cursor.moveToNext():
                    phone_index = phone_cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                    phone_type_index = phone_cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.TYPE)
                    phone_number = phone_cursor.getString(phone_index)
                    phone_type = phone_cursor.getInt(phone_type_index)
                    
                    phone_label = self._get_phone_type_label(phone_type)
                    phone_numbers.append({
                        "number": phone_number,
                        "type": phone_label
                    })
                phone_cursor.close()
                
        except Exception as e:
            print(f"获取电话号码失败: {str(e)}")
        
        return phone_numbers
    
    def _get_contact_emails(self, contact_id, content_resolver, ContactsContract):
        """获取联系人邮箱地址"""
        email_addresses = []
        try:
            email_uri = ContactsContract.CommonDataKinds.Email.CONTENT_URI
            email_selection = ContactsContract.CommonDataKinds.Email.CONTACT_ID + " = ?"
            email_cursor = content_resolver.query(email_uri, None, email_selection, [contact_id], None)
            
            if email_cursor:
                while email_cursor.moveToNext():
                    email_index = email_cursor.getColumnIndex(ContactsContract.CommonDataKinds.Email.ADDRESS)
                    email_type_index = email_cursor.getColumnIndex(ContactsContract.CommonDataKinds.Email.TYPE)
                    email_address = email_cursor.getString(email_index)
                    email_type = email_cursor.getInt(email_type_index)
                    
                    email_label = self._get_email_type_label(email_type)
                    email_addresses.append({
                        "address": email_address,
                        "type": email_label
                    })
                email_cursor.close()
                
        except Exception as e:
            print(f"获取邮箱地址失败: {str(e)}")
        
        return email_addresses
    
    def _get_contact_addresses(self, contact_id, content_resolver, ContactsContract):
        """获取联系人地址"""
        addresses = []
        try:
            address_uri = ContactsContract.CommonDataKinds.StructuredPostal.CONTENT_URI
            address_selection = ContactsContract.CommonDataKinds.StructuredPostal.CONTACT_ID + " = ?"
            address_cursor = content_resolver.query(address_uri, None, address_selection, [contact_id], None)
            
            if address_cursor:
                while address_cursor.moveToNext():
                    street_index = address_cursor.getColumnIndex(ContactsContract.CommonDataKinds.StructuredPostal.STREET)
                    city_index = address_cursor.getColumnIndex(ContactsContract.CommonDataKinds.StructuredPostal.CITY)
                    region_index = address_cursor.getColumnIndex(ContactsContract.CommonDataKinds.StructuredPostal.REGION)
                    
                    street = address_cursor.getString(street_index) or ""
                    city = address_cursor.getString(city_index) or ""
                    region = address_cursor.getString(region_index) or ""
                    
                    full_address = f"{street} {city} {region}".strip()
                    if full_address:
                        addresses.append(full_address)
                address_cursor.close()
                
        except Exception as e:
            print(f"获取地址失败: {str(e)}")
        
        return addresses
    
    def _get_contact_company(self, contact_id, content_resolver, ContactsContract):
        """获取联系人公司信息"""
        company = ""
        try:
            org_uri = ContactsContract.Data.CONTENT_URI
            org_selection = (ContactsContract.Data.CONTACT_ID + " = ? AND " +
                           ContactsContract.Data.MIMETYPE + " = ?")
            org_cursor = content_resolver.query(org_uri, None, org_selection, 
                                               [contact_id, ContactsContract.CommonDataKinds.Organization.CONTENT_ITEM_TYPE])
            
            if org_cursor and org_cursor.moveToFirst():
                company_index = org_cursor.getColumnIndex(ContactsContract.CommonDataKinds.Organization.COMPANY)
                company = org_cursor.getString(company_index) or ""
                org_cursor.close()
                
        except Exception as e:
            print(f"获取公司信息失败: {str(e)}")
        
        return company
    
    def _get_phone_type_label(self, phone_type):
        """获取电话类型标签"""
        phone_types = {
            1: "住宅",
            2: "手机", 
            3: "工作",
            4: "工作传真",
            5: "住宅传真",
            6: "寻呼机",
            7: "其他",
            0: "自定义"
        }
        return phone_types.get(phone_type, "其他")
    
    def _get_email_type_label(self, email_type):
        """获取邮箱类型标签"""
        email_types = {
            1: "住宅",
            2: "工作", 
            3: "其他",
            4: "手机",
            0: "自定义"
        }
        return email_types.get(email_type, "其他")
    
    def _get_mock_contacts_enhanced(self):
        """获取增强的模拟联系人数据"""
        return [
            {
                "id": "1",
                "name": "张三",
                "phone": "13800138000",
                "phones": [{"number": "13800138000", "type": "手机"}, {"number": "010-12345678", "type": "工作"}],
                "emails": [{"address": "zhangsan@example.com", "type": "工作"}],
                "addresses": ["北京市朝阳区建国门外大街1号"],
                "company": "科技有限公司",
                "photo_uri": "",
                "avatar": None
            },
            {
                "id": "2", 
                "name": "李四",
                "phone": "13900139000",
                "phones": [{"number": "13900139000", "type": "手机"}],
                "emails": [{"address": "lisi@gmail.com", "type": "住宅"}],
                "addresses": ["上海市浦东新区陆家嘴环路1000号"],
                "company": "金融投资公司",
                "photo_uri": "",
                "avatar": None
            },
            {
                "id": "3",
                "name": "王五", 
                "phone": "13700137000",
                "phones": [{"number": "13700137000", "type": "手机"}],
                "emails": [{"address": "wangwu@company.com", "type": "工作"}],
                "addresses": ["广州市天河区珠江新城", "深圳市南山区科技园"],
                "company": "互联网科技公司",
                "photo_uri": "",
                "avatar": None
            }
        ]
    
    def _update_contacts_list(self, contacts_data):
        """更新联系人列表"""
        self.all_contacts = contacts_data
        self.contacts = contacts_data
        
        contacts_screen = self.root.get_screen('contacts')
        contacts_list = contacts_screen.ids.contacts_list
        progress_bar = contacts_screen.ids.progress_bar
        
        # 隐藏进度条
        progress_bar.opacity = 0
        progress_bar.stop()
        
        # 清空现有列表
        contacts_list.clear_widgets()
        
        # 添加联系人项
        for contact in contacts_data:
            item = ThreeLineAvatarListItem(
                text=contact["name"],
                secondary_text=contact["phone"],
                tertiary_text=contact.get("company", "")
            )
            
            # 设置中文字体
            item.ids._lbl_primary.font_name = 'ChineseFont'
            item.ids._lbl_secondary.font_name = 'ChineseFont'
            item.ids._lbl_tertiary.font_name = 'ChineseFont'
            
            # 添加点击事件
            item.bind(on_release=lambda x, c=contact: self.show_contact_detail(c))
            
            contacts_list.add_widget(item)
        
        # 更新状态
        self.show_status(f'成功获取 {len(contacts_data)} 个联系人')
        toast(f'成功获取 {len(contacts_data)} 个联系人')
        
        # 重新启用按钮
        main_screen = self.root.get_screen('main')
        main_screen.ids.get_contacts_btn.disabled = False
        
        # 切换到联系人列表屏幕
        self.root.current = 'contacts'
    
    def show_contact_detail(self, contact):
        """显示联系人详情"""
        self.current_contact = contact
        detail_screen = self.root.get_screen('contact_detail')
        
        # 设置基本信息
        detail_screen.ids.contact_name.text = contact["name"]
        detail_screen.ids.contact_company.text = contact.get("company", "")
        
        # 设置头像
        if contact.get("photo_uri"):
            detail_screen.ids.contact_avatar.source = contact["photo_uri"]
        else:
            detail_screen.ids.contact_avatar.source = ""
        
        # 清空并添加电话号码
        phone_list = detail_screen.ids.phone_list
        phone_list.clear_widgets()
        for phone in contact.get("phones", []):
            item = TwoLineListItem(
                text=phone["number"],
                secondary_text=phone["type"]
            )
            item.ids._lbl_primary.font_name = 'ChineseFont'
            item.ids._lbl_secondary.font_name = 'ChineseFont'
            phone_list.add_widget(item)
        
        # 清空并添加邮箱
        email_list = detail_screen.ids.email_list
        email_list.clear_widgets()
        for email in contact.get("emails", []):
            item = TwoLineListItem(
                text=email["address"],
                secondary_text=email["type"]
            )
            item.ids._lbl_primary.font_name = 'ChineseFont'
            item.ids._lbl_secondary.font_name = 'ChineseFont'
            email_list.add_widget(item)
        
        # 设置地址
        addresses = contact.get("addresses", [])
        detail_screen.ids.contact_address.text = "\n".join(addresses) if addresses else "暂无地址信息"
        
        # 切换到详情页面
        self.root.current = 'contact_detail'
    
    def filter_contacts(self, search_text):
        """搜索联系人"""
        if not search_text:
            self.contacts = self.all_contacts
            return
        
        search_text = search_text.lower()
        filtered = []
        
        for contact in self.all_contacts:
            if (search_text in contact["name"].lower() or 
                search_text in contact["phone"].lower() or
                search_text in contact.get("company", "").lower()):
                filtered.append(contact)
        
        self.contacts = filtered
        self._update_filtered_list()
    
    def _update_filtered_list(self):
        """更新过滤后的列表"""
        contacts_screen = self.root.get_screen('contacts')
        contacts_list = contacts_screen.ids.contacts_list
        
        contacts_list.clear_widgets()
        
        for contact in self.contacts:
            item = ThreeLineAvatarListItem(
                text=contact["name"],
                secondary_text=contact["phone"],
                tertiary_text=contact.get("company", "")
            )
            
            item.ids._lbl_primary.font_name = 'ChineseFont'
            item.ids._lbl_secondary.font_name = 'ChineseFont'
            item.ids._lbl_tertiary.font_name = 'ChineseFont'
            
            item.bind(on_release=lambda x, c=contact: self.show_contact_detail(c))
            contacts_list.add_widget(item)
    
    def show_search_dialog(self):
        """显示搜索对话框"""
        toast("使用顶部的搜索框进行搜索")
    
    def show_filter_menu(self, button):
        """显示筛选菜单"""
        menu_items = [
            {"text": "全部", "on_release": lambda: self.filter_by_type("all")},
            {"text": "有电话的", "on_release": lambda: self.filter_by_type("has_phone")},
            {"text": "有邮箱的", "on_release": lambda: self.filter_by_type("has_email")},
            {"text": "有地址的", "on_release": lambda: self.filter_by_type("has_address")},
            {"text": "收藏的", "on_release": lambda: self.filter_by_type("favorites")},
        ]
        
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=3,
        )
        self.menu.open()
    
    def filter_by_type(self, filter_type):
        """按类型筛选联系人"""
        if filter_type == "all":
            self.contacts = self.all_contacts
        elif filter_type == "has_phone":
            self.contacts = [c for c in self.all_contacts if c.get("phones")]
        elif filter_type == "has_email":
            self.contacts = [c for c in self.all_contacts if c.get("emails")]
        elif filter_type == "has_address":
            self.contacts = [c for c in self.all_contacts if c.get("addresses")]
        elif filter_type == "favorites":
            self.contacts = [c for c in self.all_contacts if c["id"] in self.favorites]
        
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        
        self._update_filtered_list()
    
    def show_export_dialog(self):
        """显示导出对话框"""
        if not self.all_contacts:
            toast("请先获取联系人")
            return
        
        dialog = MDDialog(
            title="导出联系人",
            text="选择导出格式：",
            buttons=[
                MDFlatButton(
                    text="取消",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRectangleFlatButton(
                    text="CSV格式",
                    on_release=lambda x: (dialog.dismiss(), self.export_contacts_csv())
                ),
                MDRectangleFlatButton(
                    text="JSON格式", 
                    on_release=lambda x: (dialog.dismiss(), self.export_contacts_json())
                )
            ]
        )
        dialog.ids.title_bar.ids.label_title.font_name = 'ChineseFont'
        dialog.ids.text_content.font_name = 'ChineseFont'
        dialog.open()
    
    def export_contacts_csv(self):
        """导出联系人为CSV格式"""
        try:
            filename = f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['姓名', '电话', '邮箱', '公司', '地址']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for contact in self.all_contacts:
                    writer.writerow({
                        '姓名': contact['name'],
                        '电话': contact['phone'],
                        '邮箱': '; '.join([e['address'] for e in contact.get('emails', [])]),
                        '公司': contact.get('company', ''),
                        '地址': '; '.join(contact.get('addresses', []))
                    })
            
            toast(f"联系人已导出到: {filepath}")
            
        except Exception as e:
            toast(f"导出失败: {str(e)}")
    
    def export_contacts_json(self):
        """导出联系人为JSON格式"""
        try:
            filename = f"contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "total_contacts": len(self.all_contacts),
                "contacts": self.all_contacts
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
            
            toast(f"联系人已导出到: {filepath}")
            
        except Exception as e:
            toast(f"导出失败: {str(e)}")
    
    def add_to_favorites(self):
        """添加到收藏"""
        if self.current_contact:
            contact_id = self.current_contact["id"]
            if contact_id not in self.favorites:
                self.favorites.append(contact_id)
                toast("已添加到收藏")
            else:
                self.favorites.remove(contact_id)
                toast("已从收藏中移除")
    
    def refresh_contacts(self):
        """刷新联系人"""
        contacts_screen = self.root.get_screen('contacts')
        progress_bar = contacts_screen.ids.progress_bar
        progress_bar.opacity = 1
        progress_bar.start()
        
        thread = threading.Thread(target=self._fetch_contacts)
        thread.daemon = True
        thread.start()
    
    def _show_error(self, error_msg):
        """显示错误信息"""
        self.show_status(f'获取失败: {error_msg}')
        
        # 重新启用按钮
        main_screen = self.root.get_screen('main')
        main_screen.ids.get_contacts_btn.disabled = False
        
        # 隐藏进度条
        contacts_screen = self.root.get_screen('contacts')
        contacts_screen.ids.progress_bar.opacity = 0
        contacts_screen.ids.progress_bar.stop()
        
        toast(f"错误: {error_msg}")
    
    def go_back(self):
        """返回主屏幕"""
        self.root.current = 'main'
    
    def show_status(self, message):
        """显示状态信息"""
        main_screen = self.root.get_screen('main')
        status_label = main_screen.ids.status_label
        status_label.text = message

if __name__ == '__main__':
    EnhancedContactsApp().run()