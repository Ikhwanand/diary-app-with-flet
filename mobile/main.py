import flet as ft
from flet import (
    Page, 
    Text, 
    Container, 
    Column, 
    Row, 
    AppBar, 
    ElevatedButton, 
    OutlinedButton, 
    TextButton,
    IconButton, 
    Image, 
    ListView, 
    View, 
    alignment, 
    padding, 
    Icons,  # Add this
    Icon,
    Colors,
    FontWeight,
    MainAxisAlignment,
    CrossAxisAlignment,
    ButtonStyle,
    AlertDialog,
    ProgressRing,
    UserControl, 
    TextField, 
    Card, 
    Divider, 
    border, 
    border_radius,
    margin, 
    Audio, 
    FilePickerResultEvent, 
    FilePicker, 
    ListTile, 
    SnackBar
)
import requests
import os

BASE_URL = 'http://127.0.0.1:8000/api/'

class DiaryApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = 'Diary App'
        self.page.padding = 20
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.token = None 
        self.current_view = None
        self.file_picker = FilePicker()
        self.page.overlay.append(self.file_picker)
        self.file_picker.on_result = self.file_picker_result

        # Initialize audio player with a dummy source
        self.audio_player = Audio(
            src="https://example.com/dummy.mp3",  # Dummy source to satisfy initialization
            autoplay=False,
            volume=1.0,
            balance=0,
        )
        self.page.overlay.append(self.audio_player)

        # Create styled text fields
        self.username_field = TextField(
            label='Username',
            border_radius=10,
            text_size=16,
            prefix_icon=ft.icons.PERSON,
            focused_border_color=Colors.BLUE_400,
        )
        self.password_field = TextField(
            label='Password',
            password=True,
            can_reveal_password=True,
            border_radius=10,
            text_size=16,
            prefix_icon=ft.icons.LOCK,
            focused_border_color=Colors.BLUE_400,
        )
        self.title_field = TextField(
            label='Title',
            border_radius=10,
            text_size=16,
            prefix_icon=ft.icons.TITLE,
            focused_border_color=Colors.BLUE_400,
        )
        self.content_field = TextField(
            label='Content',
            multiline=True,
            min_lines=3,
            max_lines=8,
            text_size=16,
            border_radius=10,
            focused_border_color=Colors.BLUE_400,
        )

        # File upload related attributes
        self.selected_file_path = None
        self.selected_file_type = None
        self.current_file_upload_type = None
        self.file_info_container = ft.Ref[ft.Container]()

        # Input fields for diary creation
        self.title_input = None
        self.content_input = None

        self.auth_screen()
        
    def auth_screen(self):
        """Display the authentication screen"""
        # Create the auth view
        auth_view = View(
            route="/auth",
            controls=[
                Container(
                    content=Card(
                        content=Container(
                            content=Column(
                                [
                                    Container(
                                        content=Text("Welcome to Diary App", size=32, weight=FontWeight.BOLD),
                                        margin=margin.only(bottom=20),
                                    ),
                                    Container(
                                        content=self.username_field,
                                        margin=margin.only(bottom=10),
                                    ),
                                    Container(
                                        content=self.password_field,
                                        margin=margin.only(bottom=20),
                                    ),
                                    Row(
                                        [
                                            ElevatedButton(
                                                text='Login',
                                                style=ft.ButtonStyle(
                                                    color={ft.ControlState.DEFAULT: Colors.WHITE},
                                                    bgcolor={ft.ControlState.DEFAULT: Colors.BLUE_400},
                                                ),
                                                width=150,
                                                height=40,
                                                on_click=self.login
                                            ),
                                            ElevatedButton(
                                                text='Register',
                                                style=ft.ButtonStyle(
                                                    color={ft.ControlState.DEFAULT: Colors.BLUE_400},
                                                    bgcolor={ft.ControlState.DEFAULT: Colors.WHITE},
                                                    side={ft.ControlState.DEFAULT: ft.BorderSide(1, Colors.BLUE_400)},
                                                ),
                                                width=150,
                                                height=40,
                                                on_click=self.register
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=20,
                        ),
                        elevation=5,
                        surface_tint_color=Colors.BLUE_100,
                    ),
                    width=400,
                    alignment=alignment.center,
                )
            ],
            padding=20,
            bgcolor=Colors.WHITE,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            vertical_alignment=MainAxisAlignment.CENTER
        )

        # Update the page with the new view
        self.page.views.clear()
        self.page.views.append(auth_view)
        self.page.go('/')
        self.page.update()
    
    def login(self, e):
        username = self.username_field.value
        password = self.password_field.value
        if not username or not password:
            self.show_snack_bar('Please enter both username and password')
            return
            
        try:
            response = requests.post(
                f"{BASE_URL}login/", 
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.token = response.json().get('key')
                self.show_snack_bar('Login successful')
                # Clear the current view stack and show home screen
                self.page.views.clear()
                self.home_screen(None)  # Pass None as the event parameter
                self.page.update()
            else:
                self.show_snack_bar(f'Login failed: {response.text}')
        except requests.RequestException as e:
            self.show_snack_bar(f'Network error: {str(e)}')
    
    def register(self, e):
        username = self.username_field.value
        password = self.password_field.value
        if not username or not password:
            self.show_snack_bar('Please enter both username and password')
            return
            
        try:
            response = requests.post(
                f"{BASE_URL}register/", 
                data={
                    "username": username, 
                    "password1": password,
                    "password2": password
                }
            )
            if response.status_code == 201:
                self.show_snack_bar("Registration successful. Please login.")
                # Clear the fields
                self.username_field.value = ""
                self.password_field.value = ""
                self.page.update()
            else:
                self.show_snack_bar(f"Registration failed: {response.text}")
        except requests.RequestException as e:
            self.show_snack_bar(f"Network error: {str(e)}")
    
    def home_screen(self, e=None):
        """Display the home screen with user's diaries"""
        print("Debug: ENTERING home_screen method")
        
        # Reset page state with fallback mechanisms
        try:
            # Explicit page property setting
            self.page.bgcolor = Colors.WHITE
            self.page.vertical_alignment = MainAxisAlignment.START
            self.page.horizontal_alignment = CrossAxisAlignment.STRETCH
            
            print("Debug: Page reset complete")
        except Exception as reset_error:
            print(f"Debug: CRITICAL ERROR during page reset - {reset_error}")
            import traceback
            traceback.print_exc()
            return

        # Fetch diaries with comprehensive error handling
        try:
            print(f"Debug: Attempting to fetch diaries with token: {self.token}")
            response = requests.get(
                f"{BASE_URL}diaries/", 
                headers={"Authorization": f"Token {self.token}"},
                timeout=10
            )
            print(f"Debug: API Response Status Code: {response.status_code}")
            
            try:
                diaries = response.json()
                print("Debug: Diaries fetched successfully")
                print("Debug: Diaries content:", diaries)
            except ValueError as json_error:
                print(f"Debug: JSON Parsing Error - {json_error}")
                print("Debug: Response Text:", response.text)
                diaries = []
        
        except requests.RequestException as req_error:
            print(f"Debug: Request Error - {req_error}")
            diaries = []

        # Explicit view construction with multiple fallback strategies
        try:
            print("Debug: Starting view construction")
            # Create multiple layout options
            layout_options = []

            # Option 1: Full Page Container
            print("Debug: Creating app bar and main container")
            full_page_container = Container(
                width=self.page.width,
                height=self.page.height,
                bgcolor=Colors.WHITE,
                padding=20,
                content=Column(
                    controls=[
                        # Top App Bar
                        Container(
                            bgcolor=Colors.BLUE_400,
                            padding=padding.all(12),
                            border_radius=border_radius.only(bottom_left=10, bottom_right=10),
                            content=Row(
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    Text("My Diaries", size=24, weight=FontWeight.BOLD, color=Colors.WHITE),
                                    Row(
                                        controls=[
                                            IconButton(
                                                icon=ft.icons.ADD,
                                                icon_color=Colors.WHITE,
                                                tooltip="Create New Diary",
                                                on_click=self.show_create_diary_view
                                            ),
                                            IconButton(
                                                icon=ft.icons.LOGOUT,
                                                icon_color=Colors.WHITE,
                                                tooltip="Logout",
                                                on_click=self.logout
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ),
                        
                        # Main Content
                        Container(
                            margin=margin.only(top=20),
                            content=Column(
                                controls=[
                                    Container(
                                        padding=padding.only(left=4, bottom=12),
                                        content=Text(
                                            "Your Diaries",
                                            size=20,
                                            weight=FontWeight.BOLD,
                                            color=Colors.BLUE_GREY_800
                                        )
                                    )
                                ] + (
                                    [
                                        ListView(
                                            controls=[
                                                Card(
                                                    elevation=4,
                                                    content=Container(
                                                        padding=20,
                                                        content=Column(
                                                            controls=[
                                                                Row(
                                                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                                                    controls=[
                                                                        Text(
                                                                            diary["title"],
                                                                            size=18,
                                                                            weight=FontWeight.BOLD,
                                                                            color=Colors.BLUE_GREY_800
                                                                        ),
                                                                        Row(
                                                                            spacing=0,
                                                                            controls=[
                                                                                IconButton(
                                                                                    icon=ft.icons.EDIT,
                                                                                    icon_color=Colors.BLUE_400,
                                                                                    tooltip="Edit",
                                                                                    on_click=lambda e, diary=diary: self.update_diary(diary['id'])
                                                                                ),
                                                                                IconButton(
                                                                                    icon=ft.icons.DELETE,
                                                                                    icon_color=Colors.RED_400,
                                                                                    tooltip="Delete",
                                                                                    on_click=lambda e, diary=diary: self.delete_diary(diary['id'])
                                                                                ),
                                                                            ]
                                                                        )
                                                                    ]
                                                                ),
                                                                Container(
                                                                    padding=padding.only(top=8, bottom=12),
                                                                    content=Text(
                                                                        diary["content"][:100] + "..." if len(diary["content"]) > 100 else diary["content"],
                                                                        color=Colors.BLUE_GREY_600,
                                                                        size=14,
                                                                    )
                                                                ),
                                                                Divider(
                                                                    color=Colors.BLUE_GREY_100,
                                                                    height=1,
                                                                ),
                                                                Container(
                                                                    padding=padding.only(top=12),
                                                                    content=Row(
                                                                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                                                                        controls=[
                                                                            Column(
                                                                                spacing=5,
                                                                                controls=[
                                                                                    Text(
                                                                                        "Created",
                                                                                        size=12,
                                                                                        color=Colors.BLUE_GREY_400,
                                                                                    ),
                                                                                    Text(
                                                                                        diary.get("created_at", "").split("T")[0],
                                                                                        size=12,
                                                                                        color=Colors.BLUE_GREY_700,
                                                                                        weight=FontWeight.BOLD,
                                                                                    )
                                                                                ]
                                                                            ),
                                                                            ElevatedButton(
                                                                                content=Row(
                                                                                    controls=[
                                                                                        Icon(
                                                                                            ft.icons.VISIBILITY,
                                                                                            color=Colors.WHITE,
                                                                                            size=16,
                                                                                        ),
                                                                                        Text(
                                                                                            "View Details",
                                                                                            color=Colors.WHITE,
                                                                                            size=14,
                                                                                        ),
                                                                                    ],
                                                                                    spacing=5,
                                                                                ),
                                                                                style=ButtonStyle(
                                                                                    color={
                                                                                        "": Colors.WHITE,
                                                                                    },
                                                                                    bgcolor={
                                                                                        "": Colors.BLUE_400,
                                                                                    },
                                                                                    padding=padding.only(left=15, right=15, top=12, bottom=12),
                                                                                ),
                                                                                on_click=lambda e, diary=diary: self.show_diary_details(diary)
                                                                            ),
                                                                        ]
                                                                    )
                                                                )
                                                            ]
                                                        )
                                                    ),
                                                    margin=margin.only(bottom=16)
                                                )
                                                for diary in diaries
                                            ],
                                            expand=True,
                                            spacing=0,
                                            padding=padding.only(right=4)
                                        )
                                    ] if diaries else [
                                        Container(
                                            margin=margin.only(top=40),
                                            content=Column(
                                                horizontal_alignment=CrossAxisAlignment.CENTER,
                                                controls=[
                                                    Icon(
                                                        ft.icons.BOOK_OUTLINED,
                                                        size=64,
                                                        color=Colors.BLUE_GREY_200
                                                    ),
                                                    Container(
                                                        margin=margin.only(top=20, bottom=20),
                                                        content=Text(
                                                            "No diaries yet!",
                                                            size=16,
                                                            color=Colors.BLUE_GREY_400,
                                                            weight=FontWeight.BOLD
                                                        )
                                                    ),
                                                    Row(
                                                        alignment=MainAxisAlignment.CENTER,
                                                        controls=[
                                                            ElevatedButton(
                                                                "Create Your First Diary",
                                                                icon=ft.icons.ADD,
                                                                on_click=self.show_create_diary_view,
                                                                style=ButtonStyle(
                                                                    color={
                                                                        "": Colors.WHITE,
                                                                    },
                                                                    bgcolor={
                                                                        "": Colors.BLUE_400,
                                                                    },
                                                                    padding=padding.all(16),
                                                                )
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            alignment=alignment.center
                                        )
                                    ]
                                ),
                                expand=True
                            ),
                            expand=True
                        )
                    ],
                    expand=True
                ),
                expand=True
            )
            
            print("Debug: Main container created successfully")
            
            # Create the view
            home_view = ft.View(
                "/home",
                [full_page_container],
                bgcolor=Colors.WHITE,
                padding=0
            )
            
            print("Debug: View created successfully")
            
            # Update the page
            self.page.views.clear()
            self.page.views.append(home_view)
            print(f"Debug: View appended. Total views: {len(self.page.views)}")
            
            self.page.update()
            print("Debug: Page updated successfully")
            
        except Exception as view_error:
            print(f"Debug: CRITICAL ERROR during view construction - {view_error}")
            import traceback
            traceback.print_exc()
            return
    
    def show_create_diary_view(self, e=None):
        """Show the diary creation form"""
        # Create form fields
        self._title_value = ""  # Initialize title value
        self._content_value = ""  # Initialize content value
        
        # Create form
        form = Column(
            controls=[
                Container(
                    padding=padding.only(bottom=20),
                    content=Text(
                        "Create New Diary",
                        size=24,
                        weight=FontWeight.BOLD,
                        color=Colors.BLUE_GREY_800,
                    ),
                ),
                self.title_field,
                self.content_field,
                Container(
                    content=Row(
                        controls=[
                            OutlinedButton(
                                "Upload File",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=self.pick_file
                            ),
                            Text(
                                "No file selected",
                                size=12,
                                color=Colors.BLUE,
                                ref=self.file_info_container,
                            ),
                        ],
                        alignment=MainAxisAlignment.START,
                        spacing=10,
                    ),
                ),
                Container(
                    padding=padding.only(top=20),
                    content=Row(
                        controls=[
                            OutlinedButton(
                                "Cancel",
                                icon=ft.icons.CANCEL,
                                on_click=lambda _: self.home_screen()
                            ),
                            ElevatedButton(
                                "Create",
                                icon=ft.icons.SAVE,
                                on_click=self.handle_create_diary,
                                style=ButtonStyle(
                                    color={"": Colors.WHITE},
                                    bgcolor={"": Colors.BLUE},
                                ),
                            ),
                        ],
                        alignment=MainAxisAlignment.END,
                        spacing=10,
                    ),
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        # Create view
        view = ft.View(
            "/create",
            [
                ft.AppBar(
                    title=Text("Create New Diary"),
                    bgcolor=Colors.BLUE,
                    leading=IconButton(
                        icon=ft.icons.ARROW_BACK,
                        icon_color=Colors.WHITE,
                        on_click=lambda _: self.home_screen()
                    ),
                    actions=[
                        IconButton(
                            icon=ft.icons.CLOSE,
                            icon_color=Colors.WHITE,
                            tooltip="Cancel",
                            on_click=lambda _: self.home_screen()
                        )
                    ]
                ),
                Container(
                    content=form,
                    padding=20,
                    expand=True,
                )
            ],
            bgcolor=Colors.WHITE,
            padding=0
        )

        self.page.views.clear()
        self.page.views.append(view)
        self.page.go('/create')
        self.page.update()
        
    def handle_create_diary(self, e):
        """Handle the creation of a new diary entry"""
        title = self.title_field.value
        content = self.content_field.value

        print(f"Debug - Title: {title}, Content: {content}")

        if not title or not content:
            self.show_snack_bar("Please enter both title and content")
            return

        # Prepare file if selected
        files = {}
        if self.selected_file_path:
            try:
                files['file'] = open(self.selected_file_path, 'rb')
            except Exception as e:
                self.show_snack_bar(f"Error with file: {str(e)}")
                return

        try:
            # Prepare request data
            data = {
                'title': title,
                'content': content,
            }

            # Make API request
            response = requests.post(
                f"{BASE_URL}diaries/",
                data=data,
                files=files,
                headers={'Authorization': f'Token {self.token}'}
            )

            if response.status_code == 201:
                print("Debug: Diary created successfully")
                
                # Clear the form fields
                self.title_field.value = ""
                self.content_field.value = ""
                self.selected_file_path = None
                if self.file_info_container.current:
                    self.file_info_container.current.value = "No file selected"
                
                # Show success message
                self.show_snack_bar("Diary created successfully!")
                
                # Navigate back to home screen
                self.page.views.clear()
                self.page.update()
                self.home_screen()
            else:
                print(f"Debug: Error creating diary - {response.text}")
                self.show_snack_bar(f"Error creating diary: {response.text}")

        except Exception as e:
            print(f"Debug: Exception while creating diary - {str(e)}")
            self.show_snack_bar(f"Error: {str(e)}")
            
        finally:
            # Clean up resources
            if files and 'file' in files:
                files['file'].close()

    def update_diary(self, diary_id):
        """Update an existing diary entry"""
        try:
            # Get the diary details first
            response = requests.get(
                f"{BASE_URL}diaries/{diary_id}/",
                headers={'Authorization': f'Token {self.token}'}
            )
            
            if response.status_code == 200:
                diary = response.json()
                
                # Pre-fill the form fields
                self.title_field.value = diary.get('title', '')
                self.content_field.value = diary.get('content', '')
                
                # Create the update form
                form = Column(
                    controls=[
                        Container(
                            padding=padding.only(bottom=20),
                            content=Text(
                                "Edit Diary",
                                size=24,
                                weight=FontWeight.BOLD,
                                color=Colors.BLUE_GREY_800,
                            ),
                        ),
                        self.title_field,
                        self.content_field,
                        Container(
                            padding=padding.only(top=20),
                            content=Row(
                                controls=[
                                    OutlinedButton(
                                        "Cancel",
                                        icon=ft.icons.CANCEL,
                                        on_click=lambda _: self.home_screen()
                                    ),
                                    ElevatedButton(
                                        "Update",
                                        icon=ft.icons.SAVE,
                                        on_click=lambda _: self.handle_update_diary(diary_id),
                                        style=ButtonStyle(
                                            color={"": Colors.WHITE},
                                            bgcolor={"": Colors.BLUE_400},
                                        ),
                                    ),
                                ],
                                alignment=MainAxisAlignment.END,
                                spacing=10,
                            ),
                        ),
                    ],
                    spacing=20,
                )

                # Create and show the update view
                view = View(
                    "/edit",
                    [
                        AppBar(
                            title=Text("Edit Diary"),
                            bgcolor=Colors.BLUE_400,
                            leading=IconButton(
                                icon=ft.icons.ARROW_BACK,
                                icon_color=Colors.WHITE,
                                on_click=lambda _: self.home_screen()
                            ),
                        ),
                        Container(
                            content=form,
                            padding=20,
                            expand=True,
                        ),
                    ],
                    bgcolor=Colors.WHITE,
                    padding=0,
                )

                self.page.views.clear()
                self.page.views.append(view)
                self.page.go('/edit')
                self.page.update()
            else:
                self.show_snack_bar("Error loading diary details")
        except Exception as e:
            print(f"Error updating diary: {str(e)}")
            self.show_snack_bar(f"Error: {str(e)}")

    def handle_update_diary(self, diary_id):
        """Handle the diary update submission"""
        title = self.title_field.value
        content = self.content_field.value

        if not title or not content:
            self.show_snack_bar("Please enter both title and content")
            return

        try:
            # Make API request
            response = requests.put(
                f"{BASE_URL}diaries/{diary_id}/",
                data={
                    'title': title,
                    'content': content,
                },
                headers={'Authorization': f'Token {self.token}'}
            )

            if response.status_code == 200:
                print("Debug: Diary updated successfully")
                
                # Clear the form fields
                self.title_field.value = ""
                self.content_field.value = ""
                
                # Show success message
                self.show_snack_bar("Diary updated successfully!")
                
                # Navigate back to home screen
                self.page.views.clear()
                self.page.update()
                self.home_screen()
            else:
                print(f"Debug: Error updating diary - {response.text}")
                self.show_snack_bar(f"Error updating diary: {response.text}")

        except Exception as e:
            print(f"Debug: Exception while updating diary - {str(e)}")
            self.show_snack_bar(f"Error: {str(e)}")

    def reload_diaries(self):
        """Reload diaries list without recreating the entire view"""
        try:
            # Fetch updated diaries
            response = requests.get(
                f"{BASE_URL}diaries/", 
                headers={"Authorization": f"Token {self.token}"}
            )
            
            if response.status_code == 200:
                diaries = response.json()
                
                # Find the ListView in the current view
                if self.page.views:
                    current_view = self.page.views[-1]
                    
                    # Traverse through controls to find the ListView
                    def find_listview(controls):
                        for control in controls:
                            if isinstance(control, ListView):
                                return control
                            if hasattr(control, 'content'):
                                if isinstance(control.content, ListView):
                                    return control.content
                                if hasattr(control.content, 'controls'):
                                    result = find_listview(control.content.controls)
                                    if result:
                                        return result
                        return None
                    
                    # Get the ListView
                    diaries_list = find_listview(current_view.controls)
                    
                    if diaries_list:
                        # Clear existing diaries
                        diaries_list.controls.clear()
                        
                        # Populate with new diaries
                        for diary in diaries:
                            diary_card = Card(
                                content=Container(
                                    padding=10,
                                    content=Column([
                                        Text(diary['title'], size=18, weight=FontWeight.BOLD),
                                        Text(diary['content'][:100], size=14),
                                        Row([
                                            IconButton(
                                                icon=ft.icons.EDIT,
                                                on_click=lambda e: self.update_diary(diary['id'])
                                            ),
                                            IconButton(
                                                icon=ft.icons.DELETE,
                                                on_click=lambda e: self.delete_diary(diary['id'])
                                            )
                                        ])
                                    ])
                                )
                            )
                            diaries_list.controls.append(diary_card)
                        
                        # Update the page
                        self.page.update()
                        return True
            
            return False
        
        except Exception as e:
            print(f"Error reloading diaries: {e}")
            return False

    def delete_diary(self, diary_id):
        """Delete a diary entry"""
        try:
            # Show confirmation dialog
            dialog = AlertDialog(
                modal=True,
                title=Text("Confirm Delete"),
                content=Text("Are you sure you want to delete this diary?"),
                actions=[
                    TextButton("Cancel", on_click=lambda _: self.close_dialog()),
                    TextButton(
                        "Delete", 
                        on_click=lambda _: self.handle_delete_confirmation(diary_id)
                    ),
                ]
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as e:
            print(f"Error preparing delete dialog: {str(e)}")
            self.show_snack_bar(f"Error: {str(e)}")

    def handle_delete_confirmation(self, diary_id):
        """Handle the actual deletion of the diary after confirmation"""
        try:
            # Close the confirmation dialog
            self.close_dialog()

            # Show loading indicator
            loading = ProgressRing()
            self.page.overlay.append(loading)
            self.page.update()

            # Make delete request
            response = requests.delete(
                f"{BASE_URL}diaries/{diary_id}/",
                headers={'Authorization': f'Token {self.token}'}
            )

            # Remove loading indicator
            self.page.overlay.remove(loading)

            if response.status_code == 204:  # No content (successful deletion)
                self.show_snack_bar("Diary deleted successfully!")
                # Refresh home screen
                self.page.views.clear()
                self.home_screen()
                self.page.go('/home')
                self.page.update()
            else:
                error_message = f"Error deleting diary: {response.status_code} - {response.text}"
                print(error_message)
                self.show_snack_bar(error_message)

        except requests.RequestException as e:
            error_message = f"Network error deleting diary: {str(e)}"
            print(error_message)
            self.show_snack_bar(error_message)
        except Exception as e:
            error_message = f"Unexpected error deleting diary: {str(e)}"
            print(error_message)
            self.show_snack_bar(error_message)
        finally:
            # Ensure loading is removed
            self.page.update()

    def close_dialog(self):
        """Close the current dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def logout(self, e=None):
        """Logout the user and return to auth screen"""
        try:
            # Clear the token
            self.token = None
            
            # Reset fields
            self.username_field.value = ""
            self.password_field.value = ""
            self.title_field.value = ""
            self.content_field.value = ""
            
            # Reset file-related attributes
            self.selected_file_path = None
            self.selected_file_type = None
            self.current_file_upload_type = None
            
            # Clear views and show auth screen
            self.page.views.clear()
            self.show_snack_bar("Logged out successfully!")
            self.auth_screen()
            
        except Exception as e:
            print(f"Error during logout: {str(e)}")
            self.show_snack_bar(f"Error during logout: {str(e)}")

    def pick_file(self, e):
        """Open file picker for selecting a file"""
        print("Opening file picker...")
        # Make file extensions more permissive by removing the dot
        allowed_extensions = [
            "jpg", "jpeg", "png", "gif", 
            "mp3", "wav", "ogg", "m4a", 
            "pdf", "doc", "docx", "txt"
        ]
        # Add uppercase versions
        allowed_extensions.extend([ext.upper() for ext in allowed_extensions])
        print(f"Allowed extensions: {allowed_extensions}")
        
        try:
            self.file_picker.pick_files(
                dialog_title="Select a file for your diary",
                allowed_extensions=allowed_extensions,
                allow_multiple=False,
                initial_directory="Downloads"  # Try to start in Downloads folder
            )
        except Exception as e:
            print(f"Error in file picker: {str(e)}")
            self.show_snack_bar(f"Error opening file picker: {str(e)}")

    def clear_selected_file(self, e):
        """Clear the selected file and update the UI"""
        print("Clearing selected file...")
        self.selected_file_path = None
        self.selected_file_type = None
        
        if hasattr(self, 'file_info_container') and self.file_info_container.current:
            # Only reset to "No file selected" if there's no current file
            if not self.selected_file_path:
                print("Resetting file info container to 'No file selected'")
                self.file_info_container.current.content = Text("No file selected")
            else:
                print("Preserving current file information")
            
            self.file_info_container.current.update()

    def file_picker_result(self, e: FilePickerResultEvent):
        """Handle the result of file picker selection"""
        print("File picker result event received")
        print(f"Files: {e.files}")
        
        if e.files and len(e.files) > 0:
            file = e.files[0]
            print(f"Selected file: {file.name}")
            print(f"File path: {file.path}")
            print(f"File size: {file.size}")
            
            try:
                # Check if file exists and is readable
                with open(file.path, 'rb') as f:
                    print(f"File is readable: {file.path}")
            except Exception as e:
                print(f"Error accessing file: {str(e)}")
                self.show_snack_bar(f"Error accessing file: {str(e)}")
                return
            
            # Preserve the selected file information
            self.selected_file_path = file.path
            self.selected_file_type = file.name.split('.')[-1].lower()
            print(f"File type detected: {self.selected_file_type}")

            # Update file info container to show file name
            if hasattr(self, 'file_info_container') and self.file_info_container.current:
                # Clear previous content and create a new Column
                self.file_info_container.current.content = Column(
                    controls=[
                        Text(f"Selected file: {file.name}", weight=ft.FontWeight.BOLD),
                        Text(f"Size: {file.size} bytes"),
                        IconButton(
                            icon=ft.icons.CLOSE,
                            icon_color="red",
                            tooltip="Remove file",
                            on_click=self.clear_selected_file
                        )
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.START
                )
                # Ensure the container is updated
                self.file_info_container.current.update()
                print("File info container updated successfully")

            # Show a success snackbar
            self.show_snack_bar(f"File selected: {file.name}")
        else:
            print("No files selected or file picker was cancelled")
            # Only clear if no file was previously selected
            if not self.selected_file_path:
                self.clear_selected_file(None)
                self.show_snack_bar("No file was selected")

    def show_snack_bar(self, message):
        self.page.snack_bar = SnackBar(content=Text(message))
        self.page.snack_bar.open = True 
        self.page.update()
    
    def _render_diary_file_content(self, diary):
        """Render file content based on file type"""
        if not diary.get('file_url'):
            return Container()  # Return empty container if no file

        if diary.get('file_type') == 'image':
            return Container(
                content=Image(
                    src=diary['file_url'],
                    width=300,
                    height=200,
                    fit=ft.ImageFit.COVER,
                ),
                margin=margin.only(bottom=10),
                alignment=alignment.center,
            )
        
        elif diary.get('file_type') == 'audio':
            return Container(
                content=Row([
                    IconButton(
                        icon=ft.icons.PLAY_ARROW,
                        icon_color=Colors.BLUE_400,
                        on_click=lambda e: self._play_audio(diary['file_url'])
                    ),
                    Text(
                        os.path.basename(diary['file_url']),
                        color=Colors.BLACK54,
                    )
                ]),
                margin=margin.only(bottom=10),
            )
        
        return Container()  # Default empty container

    def _play_audio(self, audio_url):
        """Play audio from the given URL"""
        try:
            # Update the audio player's source
            self.audio_player.src = audio_url
            
            # Attempt to play the audio
            self.audio_player.play()
            
            # Show a snackbar to indicate audio is playing
            self.show_snack_bar(f"Playing: {os.path.basename(audio_url)}")
        except Exception as e:
            # Handle any errors in playing the audio
            self.show_snack_bar(f"Error playing audio: {str(e)}")

    def show_diary_details(self, diary):
        """Show full details of a specific diary entry"""
        try:
            # Create the details view
            details_view = View(
                "/details",
                [
                    AppBar(
                        title=Text("Diary Details"),
                        bgcolor=Colors.BLUE_400,
                        leading=IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color=Colors.WHITE,
                            on_click=lambda _: self.home_screen()
                        ),
                        actions=[
                            IconButton(
                                icon=ft.icons.EDIT,
                                icon_color=Colors.WHITE,
                                tooltip="Edit",
                                on_click=lambda _: self.update_diary(diary['id'])
                            ),
                            IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=Colors.WHITE,
                                tooltip="Delete",
                                on_click=lambda _: self.delete_diary(diary['id'])
                            ),
                        ],
                    ),
                    Container(
                        padding=20,
                        content=Column(
                            controls=[
                                Text(
                                    diary['title'],
                                    size=24,
                                    weight=FontWeight.BOLD,
                                    color=Colors.BLUE_GREY_800,
                                ),
                                Container(
                                    padding=padding.only(top=10, bottom=20),
                                    content=Text(
                                        diary['content'],
                                        size=16,
                                        color=Colors.BLUE_GREY_700,
                                    ),
                                ),
                                Row(
                                    controls=[
                                        Text(
                                            f"Created: {diary.get('created_at', '').split('T')[0]}",
                                            size=14,
                                            color=Colors.BLUE_GREY_400,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        expand=True,
                    ),
                ],
                bgcolor=Colors.WHITE,
                padding=0,
            )
            
            self.page.views.clear()
            self.page.views.append(details_view)
            self.page.go('/details')
            self.page.update()
            
        except Exception as e:
            print(f"Error showing diary details: {str(e)}")
            self.show_snack_bar("Error showing diary details")

    def create_home_view(self):
        """Create the home view"""
        # Comprehensive diagnostics function
        def log_detailed_diagnostics(prefix=""):
            """Log extensive page and system diagnostics"""
            print(f"Debug {prefix}: Comprehensive Diagnostics")
            print(f"Debug {prefix}: Controls count: {len(self.page.controls)}")
            print(f"Debug {prefix}: Views count: {len(self.page.views)}")
            print(f"Debug {prefix}: Page width: {self.page.width}")
            print(f"Debug {prefix}: Page height: {self.page.height}")
            print(f"Debug {prefix}: Page bgcolor: {self.page.bgcolor}")
            print(f"Debug {prefix}: Vertical alignment: {self.page.vertical_alignment}")
            print(f"Debug {prefix}: Horizontal alignment: {self.page.horizontal_alignment}")
            
            # Additional system diagnostics
            import sys
            print(f"Debug {prefix}: Python version: {sys.version}")
            try:
                import flet
                print(f"Debug {prefix}: Flet version: {flet.__version__}")
            except Exception as e:
                print(f"Debug {prefix}: Error getting Flet version: {e}")

        # Initial diagnostics
        log_detailed_diagnostics("BEFORE_RESET")
        
        # Reset page state with fallback mechanisms
        try:
            # Aggressive page reset
            self.page.controls.clear()
            self.page.views.clear()
            
            # Explicit page property setting
            self.page.bgcolor = Colors.WHITE
            self.page.vertical_alignment = MainAxisAlignment.START
            self.page.horizontal_alignment = CrossAxisAlignment.STRETCH
            
            print("Debug: Page reset complete")
        except Exception as reset_error:
            print(f"Debug: CRITICAL ERROR during page reset - {reset_error}")
            import traceback
            traceback.print_exc()
            return

        # Fetch diaries with comprehensive error
        try:
            print(f"Debug: Attempting to fetch diaries with token: {self.token}")
            response = requests.get(
                f"{BASE_URL}diaries/", 
                headers={"Authorization": f"Token {self.token}"},
                timeout=10
            )
            print(f"Debug: API Response Status Code: {response.status_code}")
            
            try:
                diaries = response.json()
                print("Debug: Diaries fetched successfully")
                print("Debug: Diaries content:", diaries)
            except ValueError as json_error:
                print(f"Debug: JSON Parsing Error - {json_error}")
                print("Debug: Response Text:", response.text)
                diaries = []
        
        except requests.RequestException as req_error:
            print(f"Debug: Request Error - {req_error}")
            diaries = []

        # Explicit view construction with multiple fallback strategies
        try:
            print("Debug: Starting view construction")
            # Create multiple layout options
            layout_options = []

            # Option 1: Full Page Container
            print("Debug: Creating app bar and main container")
            full_page_container = Container(
                width=self.page.width,
                height=self.page.height,
                bgcolor=Colors.WHITE,
                padding=20,
                content=Column(
                    controls=[
                        # Top App Bar
                        Container(
                            bgcolor=Colors.BLUE_400,
                            padding=padding.all(12),
                            border_radius=border_radius.only(bottom_left=10, bottom_right=10),
                            content=Row(
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    Text("My Diaries", size=24, weight=FontWeight.BOLD, color=Colors.WHITE),
                                    Row(
                                        controls=[
                                            IconButton(
                                                icon=Icons.ADD,
                                                icon_color=Colors.WHITE,
                                                tooltip="Create New Diary",
                                                on_click=self.show_create_diary_view
                                            ),
                                            IconButton(
                                                icon=Icons.LOGOUT,
                                                icon_color=Colors.WHITE,
                                                tooltip="Logout",
                                                on_click=self.logout
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ),
                        
                        # Main Content
                        Container(
                            margin=margin.only(top=20),
                            content=Column(
                                controls=[
                                    Container(
                                        padding=padding.only(left=4, bottom=12),
                                        content=Text(
                                            "Your Diaries",
                                            size=20,
                                            weight=FontWeight.BOLD,
                                            color=Colors.BLUE_GREY_800
                                        )
                                    )
                                ] + (
                                    [
                                        ListView(
                                            controls=[
                                                Card(
                                                    elevation=4,
                                                    content=Container(
                                                        padding=20,
                                                        content=Column(
                                                            controls=[
                                                                Row(
                                                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                                                    controls=[
                                                                        Text(
                                                                            diary["title"],
                                                                            size=18,
                                                                            weight=FontWeight.BOLD,
                                                                            color=Colors.BLUE_GREY_800
                                                                        ),
                                                                        Row(
                                                                            spacing=0,
                                                                            controls=[
                                                                                IconButton(
                                                                                    icon=Icons.EDIT,
                                                                                    icon_color=Colors.BLUE_400,
                                                                                    tooltip="Edit",
                                                                                    on_click=lambda e, diary=diary: self.update_diary(diary['id'])
                                                                                ),
                                                                                IconButton(
                                                                                    icon=Icons.DELETE,
                                                                                    icon_color=Colors.RED_400,
                                                                                    tooltip="Delete",
                                                                                    on_click=lambda e, diary=diary: self.delete_diary(diary['id'])
                                                                                ),
                                                                            ]
                                                                        )
                                                                    ]
                                                                ),
                                                                Container(
                                                                    padding=padding.only(top=8, bottom=12),
                                                                    content=Text(
                                                                        diary["content"][:100] + "..." if len(diary["content"]) > 100 else diary["content"],
                                                                        color=Colors.BLUE_GREY_600,
                                                                        size=14,
                                                                    )
                                                                ),
                                                                Divider(
                                                                    color=Colors.BLUE_GREY_100,
                                                                    height=1,
                                                                ),
                                                                Container(
                                                                    padding=padding.only(top=12),
                                                                    content=Row(
                                                                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                                                                        controls=[
                                                                            Column(
                                                                                spacing=5,
                                                                                controls=[
                                                                                    Text(
                                                                                        "Created",
                                                                                        size=12,
                                                                                        color=Colors.BLUE_GREY_400,
                                                                                    ),
                                                                                    Text(
                                                                                        diary.get("created_at", "").split("T")[0],
                                                                                        size=12,
                                                                                        color=Colors.BLUE_GREY_700,
                                                                                        weight=FontWeight.BOLD,
                                                                                    )
                                                                                ]
                                                                            ),
                                                                            ElevatedButton(
                                                                                content=Row(
                                                                                    controls=[
                                                                                        Icon(
                                                                                            Icons.VISIBILITY,
                                                                                            color=Colors.WHITE,
                                                                                            size=16,
                                                                                        ),
                                                                                        Text(
                                                                                            "View Details",
                                                                                            color=Colors.WHITE,
                                                                                            size=14,
                                                                                        ),
                                                                                    ],
                                                                                    spacing=5,
                                                                                ),
                                                                                style=ButtonStyle(
                                                                                    color={
                                                                                        "": Colors.WHITE,
                                                                                    },
                                                                                    bgcolor={
                                                                                        "": Colors.BLUE_400,
                                                                                    },
                                                                                    padding=padding.only(left=15, right=15, top=12, bottom=12),
                                                                                ),
                                                                                on_click=lambda e, diary=diary: self.show_diary_details(diary)
                                                                            ),
                                                                        ]
                                                                    )
                                                                )
                                                            ]
                                                        )
                                                    ),
                                                    margin=margin.only(bottom=16)
                                                )
                                                for diary in diaries
                                            ],
                                            expand=True,
                                            spacing=0,
                                            padding=padding.only(right=4)
                                        )
                                    ] if diaries else [
                                        Container(
                                            margin=margin.only(top=40),
                                            content=Column(
                                                horizontal_alignment=CrossAxisAlignment.CENTER,
                                                controls=[
                                                    Icon(
                                                        Icons.BOOK_OUTLINED,
                                                        size=64,
                                                        color=Colors.BLUE_GREY_200
                                                    ),
                                                    Container(
                                                        margin=margin.only(top=20, bottom=20),
                                                        content=Text(
                                                            "No diaries yet!",
                                                            size=16,
                                                            color=Colors.BLUE_GREY_400,
                                                            weight=FontWeight.BOLD
                                                        )
                                                    ),
                                                    Row(
                                                        alignment=MainAxisAlignment.CENTER,
                                                        controls=[
                                                            ElevatedButton(
                                                                "Create Your First Diary",
                                                                icon=Icons.ADD,
                                                                on_click=self.show_create_diary_view,
                                                                style=ButtonStyle(
                                                                    color={
                                                                        "": Colors.WHITE,
                                                                    },
                                                                    bgcolor={
                                                                        "": Colors.BLUE_400,
                                                                    },
                                                                    padding=padding.all(16),
                                                                )
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                            alignment=alignment.center
                                        )
                                    ]
                                ),
                                expand=True
                            ),
                            expand=True
                        )
                    ],
                    expand=True
                ),
                expand=True
            )
            
            print("Debug: Main container created successfully")
            
            # Create the view
            home_view = ft.View(
                "/home",
                [full_page_container],
                bgcolor=Colors.WHITE,
                padding=0
            )
            
            print("Debug: View created successfully")
            
            # Update the page
            return home_view
            
        except Exception as view_error:
            print(f"Debug: CRITICAL ERROR during view construction - {view_error}")
            import traceback
            traceback.print_exc()
            return{{ ... }}

ft.app(target=DiaryApp)