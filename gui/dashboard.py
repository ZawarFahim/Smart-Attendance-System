"""
Base Dashboard Layout using Tkinter.
Provides the skeleton for sidebar navigation and main content area.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from config.settings import COLORS, FONTS, WINDOW_GEOMETRY
from utils.helpers import clear_frame, center_window
from services.auth_service import change_password, verify_current_password

class BaseDashboard(tk.Tk):
    def __init__(self, title, user_info, on_logout=None):
        super().__init__()
        self.user_info = user_info
        self.on_logout_callback = on_logout
        
        self.title(f"ATTENDIFY - {title}")
        self.geometry(WINDOW_GEOMETRY)
        center_window(self, 1024, 768)
        
        # Apply sv-ttk theme
        sv_ttk.set_theme("dark")
        
        style = ttk.Style()
        style.configure("PageTitle.TLabel", font=FONTS['h1'])
        style.configure("CardHeader.TLabel", font=FONTS['h2'])
        style.configure("CardBody.TLabel", font=FONTS['body'])
        
        # Maintain backwards compatibility for styles used in child classes
        style.configure("Card.TFrame")
        style.configure("Content.TFrame")
        style.configure("Sidebar.TFrame")
        style.configure("Sidebar.TButton", font=FONTS['body_bold'])

        # Layout Grids
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Build Sidebar
        self.sidebar_frame = ttk.Frame(self, style="Sidebar.TFrame")
        self.sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)

        # Build Content Area
        self.content_frame = ttk.Frame(self, style="Content.TFrame")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self._build_sidebar_header()
        self.setup_menu()

    def toggle_theme(self):
        if sv_ttk.get_theme() == "dark":
            sv_ttk.set_theme("light")
        else:
            sv_ttk.set_theme("dark")

    def _build_sidebar_header(self):
        """Header with User Info."""
        header_lbl = ttk.Label(self.sidebar_frame, 
                              text=f"Welcome,\n{self.user_info['username']}", 
                              font=FONTS['h2'], justify="center")
        header_lbl.pack(fill='x', pady=20, padx=10)
        
        logout_btn = ttk.Button(self.sidebar_frame, text="Log Out", 
                                style="Sidebar.TButton", command=self.logout)
        logout_btn.pack(side='bottom', fill='x', pady=10)
        
        change_pw_btn = ttk.Button(self.sidebar_frame, text="Change Password", 
                                   style="Sidebar.TButton", command=self.show_change_password)
        change_pw_btn.pack(side='bottom', fill='x', pady=(10, 0))

        theme_btn = ttk.Button(self.sidebar_frame, text="Toggle Theme", 
                               style="Sidebar.TButton", command=self.toggle_theme)
        theme_btn.pack(side='bottom', fill='x', pady=(10, 0))

    def show_change_password(self):
        def view():
            title = ttk.Label(self.content_frame, text="Change Password", style="PageTitle.TLabel")
            title.pack(pady=(30, 14))

            form_frame = ttk.Frame(self.content_frame, style="Card.TFrame", padding=24)
            form_frame.pack(pady=12, padx=20, fill='x')

            ttk.Label(
                form_frame,
                text="Use a strong password (at least 8 characters).",
                style="CardBody.TLabel"
            ).pack(anchor='w', pady=(0, 14))

            ttk.Label(form_frame, text="Current Password", style="CardBody.TLabel").pack(anchor='w')
            current_entry = ttk.Entry(form_frame, show="*", font=FONTS['body'])
            current_entry.pack(fill='x', pady=(4, 12), ipady=4)

            ttk.Label(form_frame, text="New Password", style="CardBody.TLabel").pack(anchor='w')
            pw_entry = ttk.Entry(form_frame, show="*", font=FONTS['body'])
            pw_entry.pack(fill='x', pady=(4, 12), ipady=4)

            ttk.Label(form_frame, text="Confirm New Password", style="CardBody.TLabel").pack(anchor='w')
            confirm_entry = ttk.Entry(form_frame, show="*", font=FONTS['body'])
            confirm_entry.pack(fill='x', pady=(4, 8), ipady=4)
            
            def do_change():
                current_pw = current_entry.get()
                pw = pw_entry.get()
                cpw = confirm_entry.get()
                if not current_pw or not pw or not cpw:
                    messagebox.showerror("Error", "All fields are required.")
                    return
                if pw != cpw:
                    messagebox.showerror("Error", "Passwords do not match!")
                    return
                if len(pw) < 8:
                    messagebox.showerror("Error", "Password must be at least 8 characters long.")
                    return
                if not verify_current_password(self.user_info['user_id'], current_pw):
                    messagebox.showerror("Error", "Current password is incorrect.")
                    return
                
                success = change_password(self.user_info['user_id'], pw)
                if success:
                    messagebox.showinfo("Success", "Password updated successfully!")
                    current_entry.delete(0, 'end')
                    pw_entry.delete(0, 'end')
                    confirm_entry.delete(0, 'end')
                else:
                    messagebox.showerror("Error", "Failed to update password.")

            btn = ttk.Button(form_frame, text="Update Password", style="Accent.TButton", command=do_change)
            btn.pack(anchor='e', pady=16)
            
        self.switch_view(view)

    def add_menu_item(self, text, command):
        btn = ttk.Button(self.sidebar_frame, text=text, style="Sidebar.TButton", command=command)
        btn.pack(fill='x', pady=5, padx=10)

    def setup_menu(self):
        """Override in subclasses to add specific menu items."""
        pass

    def switch_view(self, view_func):
        """Clears the content frame and loads a new view."""
        clear_frame(self.content_frame)
        view_func()

    def logout(self):
        self.destroy()
        if self.on_logout_callback:
            self.on_logout_callback()
