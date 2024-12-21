from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
import google.generativeai as genai
from datetime import datetime
import os
import shutil
from PIL import Image
import json

KV = '''
<MessageBubble>:
    orientation: 'vertical'
    size_hint_y: None
    height: content.height + attachment_box.height + image_box.height + 20
    padding: [15, 10]
    spacing: 5
    radius: [20, 20, 20, 20]
    ripple_behavior: True
    
    MDBoxLayout:
        id: attachment_box
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: 5
    
    MDBoxLayout:
        id: image_box
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: 5
    
    MDLabel:
        id: content
        text: root.text
        size_hint_y: None
        height: self.texture_size[1]
        color: 1, 1, 1, 1
        markup: True

<FileAttachment>:
    size_hint_y: None
    height: "40dp"
    padding: [5, 5]
    spacing: 10
    
    MDIconButton:
        icon: root.file_icon
        size_hint: None, None
        size: "30dp", "30dp"
        pos_hint: {"center_y": .5}
    
    MDLabel:
        text: root.filename
        size_hint_y: None
        height: "30dp"
        pos_hint: {"center_y": .5}

<ChatImage>:
    size_hint_y: None
    height: image.height
    padding: [5, 5]
    
    AsyncImage:
        id: image
        source: root.source
        size_hint_y: None
        height: 200 if self.texture else 0
        allow_stretch: True
        keep_ratio: True

<ChatHistoryItem>:
    IconLeftWidget:
        icon: "chat"

<ChatScreen>:
    md_bg_color: 0.1, 0.1, 0.1, 1
    
    MDNavigationDrawer:
        id: nav_drawer
        radius: (0, 16, 16, 0)
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: "8dp"
            spacing: "8dp"
            
            MDLabel:
                text: "Chat History"
                font_style: "H6"
                size_hint_y: None
                height: self.texture_size[1]
                padding: "8dp"
            
            MDFlatButton:
                text: "New Chat"
                on_release: root.new_chat()
                size_hint_x: 1
            
            MDScrollView:
                MDList:
                    id: chat_history_list
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [10, 10]
        
        # App Bar
        MDCard:
            size_hint_y: None
            height: 60
            md_bg_color: 0.15, 0.15, 0.15, 1
            radius: [15, 15, 15, 15]
            padding: [15, 0]
            
            MDBoxLayout:
                orientation: 'horizontal'
                padding: [10, 0]
                spacing: 10
                
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"center_y": .5}
                    on_release: root.ids.nav_drawer.set_state("open")
                
                MDLabel:
                    text: "Pegasus AI"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    font_style: "H6"
        
        # Chat Messages Area
        MDScrollView:
            id: chat_scroll
            do_scroll_x: False
            
            MDBoxLayout:
                id: chat_box
                orientation: 'vertical'
                spacing: 15
                size_hint_y: None
                height: self.minimum_height
                padding: [10, 10]
        
        # Input Area
        MDCard:
            size_hint_y: None
            height: 70
            md_bg_color: 0.15, 0.15, 0.15, 1
            radius: [15, 15, 15, 15]
            padding: [5, 5]
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: 10
                padding: [10, 0]
                
                MDIconButton:
                    icon: "file"
                    pos_hint: {"center_y": .5}
                    on_release: root.show_file_manager()
                
                MDIconButton:
                    icon: "image"
                    pos_hint: {"center_y": .5}
                    on_release: root.show_file_manager(file_type="image")
                
                MDTextField:
                    id: message_input
                    hint_text: "Type a message..."
                    multiline: False
                    mode: "round"
                    size_hint: 1, None
                    height: "40dp"
                    pos_hint: {"center_y": .5}
                    text_color_normal: 1, 1, 1, 1
                    text_color_focus: 1, 1, 1, 1
                    hint_text_color_normal: 0.7, 0.7, 0.7, 1
                    hint_text_color_focus: 0.7, 0.7, 0.7, 1
                
                MDIconButton:
                    icon: "send"
                    pos_hint: {"center_y": .5}
                    on_release: root.send_message()

'''

class ChatImage(MDBoxLayout):
    source = StringProperty()

class FileAttachment(MDBoxLayout):
    filename = StringProperty()
    file_icon = StringProperty()
    
    def __init__(self, filepath, **kwargs):
        super().__init__(**kwargs)
        self.filename = os.path.basename(filepath)
        extension = os.path.splitext(filepath)[1].lower()
        
        if extension in ['.pdf']:
            self.file_icon = 'file-pdf-box'
        elif extension in ['.doc', '.docx']:
            self.file_icon = 'file-word-box'
        elif extension in ['.ppt', '.pptx']:
            self.file_icon = 'file-powerpoint-box'
        elif extension in ['.jpg', '.jpeg', '.png', '.gif']:
            self.file_icon = 'file-image'
        else:
            self.file_icon = 'file'

class ChatHistoryItem(OneLineIconListItem):
    chat_id = StringProperty()

class MessageBubble(MDCard):
    text = StringProperty()
    message_type = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.message_type == 'user':
            self.md_bg_color = (0.2, 0.4, 0.8, 1)
            self.pos_hint = {"right": 0.98}
            self.size_hint_x = None
            self.width = min(Window.width * 0.8, len(self.text) * 10 + 50)
        else:
            self.md_bg_color = (0.25, 0.25, 0.25, 1)
            self.pos_hint = {"x": 0.02}
            self.size_hint_x = None
            self.width = min(Window.width * 0.8, len(self.text) * 10 + 50)
    
    def add_attachment(self, filepath):
        extension = os.path.splitext(filepath)[1].lower()
        if extension in ['.jpg', '.jpeg', '.png', '.gif']:
            image = ChatImage(source=filepath)
            self.ids.image_box.add_widget(image)
        else:
            attachment = FileAttachment(filepath)
            self.ids.attachment_box.add_widget(attachment)

class ChatScreen(MDScreen):
    current_chat_id = StringProperty()
    is_nav_drawer_open = False  # Property to track drawer state

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        genai.configure(api_key='PUT YOUR GEMINI API KEY HERE')
        self.model = genai.GenerativeModel('gemini-pro')
        
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
        )
        self.current_file_type = None
        
        # Create necessary directories
        self.chats_dir = os.path.join(os.path.dirname(__file__), "chats")
        self.attachments_dir = os.path.join(os.path.dirname(__file__), "attachments")
        os.makedirs(self.chats_dir, exist_ok=True)
        os.makedirs(self.attachments_dir, exist_ok=True)
        
        # Load chat history
        self.load_chat_history()
        
        # Create new chat if none exists
        if not self.current_chat_id:
            self.new_chat()
    
    def load_chat_history(self):
        self.ids.chat_history_list.clear_widgets()
        for filename in os.listdir(self.chats_dir):
            if filename.endswith('.json'):
                chat_id = filename[:-5]
                item = ChatHistoryItem(text=f"Chat {chat_id}", chat_id=chat_id)
                item.bind(on_release=lambda x, cid=chat_id: self.load_chat(cid))
                self.ids.chat_history_list.add_widget(item)
    
    def new_chat(self):
        self.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.ids.chat_box.clear_widgets()
        self.save_chat()
        self.load_chat_history()
    
    def load_chat(self, chat_id):
        self.current_chat_id = chat_id
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        
        if os.path.exists(chat_file):
            with open(chat_file, 'r') as f:
                chat_data = json.load(f)
            
            self.ids.chat_box.clear_widgets()
            for message in chat_data['messages']:
                bubble = MessageBubble(
                    text=message['text'],
                    message_type=message['type']
                )
                if 'attachment' in message:
                    bubble.add_attachment(message['attachment'])
                self.ids.chat_box.add_widget(bubble)
        
        # Close the navigation drawer when a chat is loaded
        self.ids.nav_drawer.set_state("close")
        self.is_nav_drawer_open = False  # Update the drawer state
    
    def toggle_nav_drawer(self):
        if self.is_nav_drawer_open:
            self.ids.nav_drawer.set_state("close")
            self.is_nav_drawer_open = False
        else:
            self.ids.nav_drawer.set_state("open")
            self.is_nav_drawer_open = True

        # Toggle the icon
        self.update_nav_button_icon()

    def update_nav_button_icon(self):
        # Update the icon based on the drawer state
        if self.is_nav_drawer_open:
            self.ids.menu_button.icon = "arrow-left"  # Change icon to arrow when open
        else:
            self.ids.menu_button.icon = "menu"  # Change icon back to menu when closed

    def save_chat(self):
        chat_data = {
            'id': self.current_chat_id,
            'messages': []
        }
        
        for child in self.ids.chat_box.children:
            if isinstance(child, MessageBubble):
                message = {
                    'text': child.text,
                    'type': child.message_type
                }
                # Save attachment path if exists
                if child.ids.attachment_box.children or child.ids.image_box.children:
                    attachment = None
                    if child.ids.attachment_box.children:
                        attachment = child.ids.attachment_box.children[0].filename
                    elif child.ids.image_box.children:
                        attachment = child.ids.image_box.children[0].source
                    if attachment:
                        message['attachment'] = attachment
                chat_data['messages'].append(message)
        
        with open(os.path.join(self.chats_dir, f"{self.current_chat_id}.json"), 'w') as f:
            json.dump(chat_data, f)
    
    def show_file_manager(self, file_type="document"):
        self.current_file_type = file_type
        if file_type == "image":
            self.file_manager.ext = [".png", ".jpg", ".jpeg", ".gif"]
        else:
            self.file_manager.ext = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
        self.file_manager.show(os.path.expanduser("~"))
    
    def select_path(self, path):
        self.exit_file_manager()
        
        if os.path.exists(path):
            filename = os.path.basename(path)
            dest_path = os.path.join(self.attachments_dir, filename)
            shutil.copy2(path, dest_path)
            
            bubble = MessageBubble(text="", message_type='user')
            bubble.add_attachment(dest_path)
            self.ids.chat_box.add_widget(bubble)
            
            self.save_chat()
            Clock.schedule_once(lambda dt: self.scroll_to_bottom())
    
    def exit_file_manager(self, *args):
        self.file_manager.close()
    
    def send_message(self):
        message = self.ids.message_input.text.strip()
        if message:
            self.add_message(message, 'user')
            self.ids.message_input.text = ""
            
            response = self.get_bot_response(message)
            self.add_message(response, 'bot')
            
            self.save_chat()
            Clock.schedule_once(lambda dt: self.scroll_to_bottom())
    
    def add_message(self, text, message_type):
        bubble = MessageBubble(text=text, message_type=message_type)
        self.ids.chat_box.add_widget(bubble)
    
    def get_bot_response(self, message):
        try:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def scroll_to_bottom(self):
        self.ids.chat_scroll.scroll_y = 0

    def delete_chat(self, chat_id):
        chat_file = os.path.join(self.chats_dir, f"{chat_id}.json")
        if os.path.exists(chat_file):
            os.remove(chat_file)
        self.load_chat_history()

class PegasusAIApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_string(KV)
        return ChatScreen()

if __name__ == "__main__":
    Window.size = (400, 700)
    PegasusAIApp().run()
