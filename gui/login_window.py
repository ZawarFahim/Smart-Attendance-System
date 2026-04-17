"""
Login Window UI.
Handles user authentication and routing to the respective dashboard.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from config.settings import COLORS, FONTS, APP_NAME
from utils.helpers import center_window
from services.auth_service import authenticate
from services.student_service import add_student
from services.faculty_service import add_faculty
from services.department_service import get_all_departments
from utils.auth import hash_password

class LoginWindow(tk.Tk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        
        self.title(f"Login | {APP_NAME}")
        self.geometry("400x500")
        self.configure(bg=COLORS['background'])
        self.resizable(False, False)
        center_window(self, 400, 500)

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Primary.TButton", font=FONTS['body_bold'], background=COLORS['secondary'], foreground=COLORS['text_light'])
        style.map("Primary.TButton", background=[("active", "#14a085")])

        # Header
        header_frame = tk.Frame(self, bg=COLORS['primary'], height=100)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        title_lbl = tk.Label(header_frame, text="ATTENDIFY", font=FONTS['h1'], 
                             bg=COLORS['primary'], fg=COLORS['text_light'])
        title_lbl.pack(pady=25)

        # Form
        form_frame = tk.Frame(self, bg=COLORS['background'], padx=40, pady=40)
        form_frame.pack(expand=True, fill='both')

        tk.Label(form_frame, text="Email / Username", font=FONTS['body_bold'], bg=COLORS['background']).pack(anchor='w', pady=(0, 5))
        self.email_entry = ttk.Entry(form_frame, font=FONTS['body'])
        self.email_entry.pack(fill='x', pady=(0, 20), ipady=5)

        tk.Label(form_frame, text="Password", font=FONTS['body_bold'], bg=COLORS['background']).pack(anchor='w', pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, font=FONTS['body'], show="*")
        self.password_entry.pack(fill='x', pady=(0, 30), ipady=5)
        self.password_entry.bind("<Return>", lambda _event: self._handle_login())

        login_btn = ttk.Button(form_frame, text="LOGIN", style="Primary.TButton", command=self._handle_login, cursor="hand2")
        login_btn.pack(fill='x', ipady=10)

        signup_btn = tk.Button(form_frame, text="SIGN UP", font=FONTS['body_bold'], 
                               bg=COLORS['background'], fg=COLORS['primary'], 
                               command=self._show_signup, relief='flat', cursor="hand2")
        signup_btn.pack(fill='x', ipady=10, pady=(10, 0))

    def _handle_login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please provide both email and password.")
            return

        user = authenticate(email, password)
        if user:
            self.destroy() # Close login window
            self.on_login_success(user)
        else:
            messagebox.showerror("Auth Failed", "Invalid credentials provided.")

    def _show_signup(self):
        signup_win = tk.Toplevel(self)
        signup_win.title("Sign Up | ATTENDIFY")
        signup_win.geometry("450x650")
        signup_win.configure(bg=COLORS['background'])
        signup_win.grab_set()
        center_window(signup_win, 450, 650)
        
        tk.Label(signup_win, text="Create New Account", font=FONTS['h2'], bg=COLORS['background'], fg=COLORS['primary']).pack(pady=20)
        
        form = tk.Frame(signup_win, bg=COLORS['background'], padx=40)
        form.pack(expand=True, fill='both')
        
        # Helper for fields
        def add_field(label_text, is_password=False):
            tk.Label(form, text=label_text, font=FONTS['body_bold'], bg=COLORS['background']).pack(anchor='w', pady=(5, 2))
            entry = ttk.Entry(form, font=FONTS['body'], show="*" if is_password else "")
            entry.pack(fill='x', pady=(0, 10), ipady=5)
            return entry
            
        fname_entry = add_field("First Name")
        lname_entry = add_field("Last Name")
        username_entry = add_field("Username")
        email_entry = add_field("Email")
        password_entry = add_field("Password", is_password=True)
        
        tk.Label(form, text="Role", font=FONTS['body_bold'], bg=COLORS['background']).pack(anchor='w', pady=(5, 2))
        role_combo = ttk.Combobox(form, values=["Student", "Faculty"], state="readonly", font=FONTS['body'])
        role_combo.pack(fill='x', pady=(0, 10), ipady=5)
        role_combo.set("Student")
        
        tk.Label(form, text="Department", font=FONTS['body_bold'], bg=COLORS['background']).pack(anchor='w', pady=(5, 2))
        departments = get_all_departments()
        dept_map = {d['dept_name']: d['dept_id'] for d in departments} if departments else {}
        dept_combo = ttk.Combobox(form, values=list(dept_map.keys()), state="readonly", font=FONTS['body'])
        dept_combo.pack(fill='x', pady=(0, 20), ipady=5)
        if dept_map:
            dept_combo.current(0)
            
        def do_signup():
            fn = fname_entry.get().strip()
            ln = lname_entry.get().strip()
            un = username_entry.get().strip()
            em = email_entry.get().strip()
            pw = password_entry.get()
            role = role_combo.get()
            dept_name = dept_combo.get()
            
            if not all([fn, ln, un, em, pw, role, dept_name]):
                messagebox.showerror("Error", "All fields are required.", parent=signup_win)
                return
            
            dept_id = dept_map.get(dept_name)
            hashed_password = hash_password(pw)
            success = False
            if role == "Student":
                success = add_student(un, em, hashed_password, fn, ln, dept_id)
            elif role == "Faculty":
                success = add_faculty(un, em, hashed_password, fn, ln, dept_id)
                
            if success:
                messagebox.showinfo("Success", "Account created successfully! You can now log in.", parent=signup_win)
                signup_win.destroy()
            else:
                messagebox.showerror("Error", "Failed to create account. Username or email might already be taken.", parent=signup_win)
                
        submit_btn = tk.Button(form, text="REGISTER", font=FONTS['body_bold'], 
                               bg=COLORS['secondary'], fg=COLORS['text_light'], 
                               command=do_signup, relief='flat', cursor="hand2")
        submit_btn.pack(fill='x', ipady=10, pady=10)
