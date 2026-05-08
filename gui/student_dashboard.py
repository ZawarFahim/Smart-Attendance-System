"""
Student Dashboard to view attendance.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from gui.dashboard import BaseDashboard
from config.settings import FONTS, COLORS
from services.attendance_service import (
    get_attendance_history,
    get_attendance_history_all,
    get_student_sections,
    get_student_attendance_summary,
)
from services.timetable_service import get_timetable_for_student
from services.user_service import create_leave_request, get_leave_requests_for_user, get_eligible_sections_for_student
from services.user_service import get_notifications, mark_as_read
from services.report_service import (
    get_student_prerequisite_status,
    get_blocked_enrollments_for_student,
)
from utils.validators import is_valid_date
from datetime import datetime
from PIL import Image, ImageTk
from services.image_service import upload_profile_image, get_student_profile_image
from tkinter import filedialog

class StudentDashboard(BaseDashboard):
    def __init__(self, user_info, on_logout=None):
        super().__init__("Student Portal", user_info, on_logout)
    
    def setup_menu(self):
        self.add_menu_item("Overview", self.show_overview)
        self.add_menu_item("My Attendance", self.show_attendance)
        self.add_menu_item("Attendance Summary", self.show_attendance_summary)
        self.add_menu_item("Course Eligibility", self.show_prerequisites)
        self.add_menu_item("My Timetable", self.show_timetable)
        self.add_menu_item("Leave Requests", self.show_leave_requests)
        self.add_menu_item("Notifications", self.show_notifications)
        
        self.add_menu_item("My Profile", self.show_profile)
        
        # Default view
        self.show_overview()

    def _build_table(self, parent, columns):
        wrapper = ttk.Frame(parent, style="Card.TFrame")
        wrapper.pack(expand=True, fill='both', padx=20, pady=(0, 20))

        tree = ttk.Treeview(wrapper, columns=columns, show='headings', height=12)
        vsb = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(wrapper, orient="horizontal", command=tree.xview)
        tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')
        return tree

    def show_overview(self):
        def view():
            ttk.Label(self.content_frame, text="Student Overview", style="PageTitle.TLabel").pack(pady=(24, 16))
            sections = get_student_sections(self.user_info['user_id'])
            attendance_rows = get_attendance_history(self.user_info['user_id'])
            timetable_rows = get_timetable_for_student(self.user_info['user_id'])
            summary_rows = get_student_attendance_summary(self.user_info['user_id'])
            avg_att = 0.0
            if summary_rows:
                avg_att = sum(float(row['attendance_percentage']) for row in summary_rows) / len(summary_rows)

            cards = ttk.Frame(self.content_frame, style="Content.TFrame")
            cards.pack(fill='x', padx=16, pady=6)
            items = [
                ("Enrolled Sections", len(sections)),
                ("Attendance Records", len(attendance_rows)),
                ("Timetable Slots", len(timetable_rows)),
                ("Avg Attendance %", f"{avg_att:.2f}%"),
            ]
            for idx, (label, value) in enumerate(items):
                card = ttk.Frame(cards, style="Card.TFrame", padding=16)
                card.grid(row=0, column=idx, padx=8, sticky='nsew')
                ttk.Label(card, text=label, style="CardBody.TLabel").pack(anchor='w')
                ttk.Label(card, text=str(value), style="CardHeader.TLabel").pack(anchor='w', pady=(8, 0))
                cards.grid_columnconfigure(idx, weight=1)
        self.switch_view(view)

    def show_attendance(self):
        def view():
            ttk.Label(self.content_frame, text="Attendance History (Current + Archive)", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Date", "Course Code", "Course Name", "Status", "Source")
            tree = self._build_table(self.content_frame, columns)
            history = get_attendance_history_all(self.user_info['user_id'])
            for record in history:
                tree.insert(
                    "",
                    "end",
                    values=(
                        record['session_date'],
                        record['course_code'],
                        record['course_name'],
                        record['status_name'],
                        record['source'],
                    ),
                )
                
        self.switch_view(view)

    def show_attendance_summary(self):
        def view():
            ttk.Label(self.content_frame, text="Attendance Summary", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Section ID", "Course Code", "Course Name", "Attendance %")
            tree = self._build_table(self.content_frame, columns)
            rows = get_student_attendance_summary(self.user_info['user_id'])
            for row in rows:
                tree.insert("", "end", values=(
                    row['section_id'],
                    row['course_code'],
                    row['course_name'],
                    f"{row['attendance_percentage']}%"
                ))
        self.switch_view(view)

    def show_prerequisites(self):
        def view():
            ttk.Label(self.content_frame, text="Course Eligibility & Prerequisites", style="PageTitle.TLabel").pack(pady=(24, 16))

            notebook = ttk.Notebook(self.content_frame)
            notebook.pack(expand=True, fill='both', padx=16, pady=10)

            # Tab 1: Eligibility per Course
            tab_status = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_status, text="Prerequisite Status")
            cols_status = ("Course Code", "Course Name", "Total Prereqs", "Completed", "Eligible")
            tree_status = self._build_table(tab_status, cols_status)
            for row in get_student_prerequisite_status(self.user_info['user_id']):
                tree_status.insert(
                    "",
                    "end",
                    values=(
                        row['course_code'],
                        row['course_name'],
                        row['prereq_count'],
                        row['completed_prereq_count'],
                        "Yes" if row['is_eligible'] else "No",
                    ),
                )

            # Tab 2: Eligible Sections (enrollment suggestions)
            tab_eligible = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_eligible, text="Eligible Sections")
            cols_eligible = ("Section ID", "Course Code", "Course Name", "Semester", "Year")
            tree_eligible = self._build_table(tab_eligible, cols_eligible)
            for row in get_eligible_sections_for_student(self.user_info['user_id']):
                tree_eligible.insert(
                    "",
                    "end",
                    values=(
                        row['section_id'],
                        row['course_code'],
                        row['course_name'],
                        row['semester'],
                        row['academic_year'],
                    ),
                )

            # Tab 3: Blocked Enrollments with missing prerequisites
            tab_blocked = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_blocked, text="Blocked Enrollments")
            cols_blocked = ("Section ID", "Course Code", "Course Name", "Semester", "Year", "Missing Prereqs")
            tree_blocked = self._build_table(tab_blocked, cols_blocked)
            for row in get_blocked_enrollments_for_student(self.user_info['user_id']):
                tree_blocked.insert(
                    "",
                    "end",
                    values=(
                        row['section_id'],
                        row['course_code'],
                        row['course_name'],
                        row['semester'],
                        row['academic_year'],
                        row['missing_prerequisites'],
                    ),
                )

        self.switch_view(view)

    def show_timetable(self):
        def view():
            ttk.Label(self.content_frame, text="My Timetable", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Course Code", "Day", "Start", "End", "Room")
            tree = self._build_table(self.content_frame, columns)
            rows = get_timetable_for_student(self.user_info['user_id'])
            for row in rows:
                tree.insert("", "end", values=(
                    row['course_code'],
                    row['day_of_week'],
                    str(row['start_time'])[:5],
                    str(row['end_time'])[:5],
                    row['room_name']
                ))
        self.switch_view(view)

    def show_leave_requests(self):
        def view():
            ttk.Label(self.content_frame, text="Leave Requests", style="PageTitle.TLabel").pack(pady=(24, 16))

            form = ttk.Frame(self.content_frame, style="Card.TFrame", padding=16)
            form.pack(fill='x', padx=20, pady=(0, 12))
            ttk.Label(form, text="Start Date (YYYY-MM-DD)", style="CardBody.TLabel").grid(row=0, column=0, sticky='w')
            start_entry = ttk.Entry(form, font=FONTS['body'])
            start_entry.grid(row=0, column=1, sticky='ew', padx=(12, 0), pady=4)

            ttk.Label(form, text="End Date (YYYY-MM-DD)", style="CardBody.TLabel").grid(row=1, column=0, sticky='w')
            end_entry = ttk.Entry(form, font=FONTS['body'])
            end_entry.grid(row=1, column=1, sticky='ew', padx=(12, 0), pady=4)

            ttk.Label(form, text="Reason", style="CardBody.TLabel").grid(row=2, column=0, sticky='nw')
            reason_text = tk.Text(form, height=4, font=FONTS['body'])
            reason_text.grid(row=2, column=1, sticky='ew', padx=(12, 0), pady=4)
            form.grid_columnconfigure(1, weight=1)

            columns = ("Leave ID", "Start Date", "End Date", "Reason", "Status", "Reviewed By", "Submitted At")
            tree = self._build_table(self.content_frame, columns)

            def load_leave_requests():
                tree.delete(*tree.get_children())
                rows = get_leave_requests_for_user(self.user_info['user_id'])
                for row in rows:
                    tree.insert("", "end", values=(
                        row['leave_id'],
                        row['start_date'],
                        row['end_date'],
                        row['reason'],
                        row['status'],
                        row['reviewed_by'] if row['reviewed_by'] else '-',
                        row['created_at']
                    ), tags=(row['status'],))
                tree.tag_configure("Pending", foreground="#f39c12")
                tree.tag_configure("Approved", foreground="#27ae60")
                tree.tag_configure("Rejected", foreground="#c0392b")

            def submit_leave():
                start_date = start_entry.get().strip()
                end_date = end_entry.get().strip()
                reason = reason_text.get("1.0", "end").strip()
                if not start_date or not end_date or not reason:
                    messagebox.showerror("Validation Error", "Please fill all leave request fields.")
                    return
                if not is_valid_date(start_date) or not is_valid_date(end_date):
                    messagebox.showerror("Validation Error", "Date format must be YYYY-MM-DD.")
                    return
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Validation Error", "Please enter valid calendar dates.")
                    return
                if end_dt < start_dt:
                    messagebox.showerror("Validation Error", "End date cannot be earlier than start date.")
                    return
                if create_leave_request(self.user_info['user_id'], start_date, end_date, reason):
                    start_entry.delete(0, 'end')
                    end_entry.delete(0, 'end')
                    reason_text.delete("1.0", "end")
                    load_leave_requests()
                else:
                    messagebox.showerror("Error", "Failed to submit leave request.")

            ttk.Button(form, text="Submit Request", style="Accent.TButton", command=submit_leave).grid(row=3, column=1, sticky='e', pady=(10, 0))
            load_leave_requests()
        self.switch_view(view)

    def show_notifications(self):
        def view():
            ttk.Label(self.content_frame, text="Notifications", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("ID", "Message", "Read", "Created At")
            tree = self._build_table(self.content_frame, columns)

            actions = ttk.Frame(self.content_frame, style="Content.TFrame")
            actions.pack(fill='x', padx=20, pady=(0, 16))
            selected_notification_id = None

            def load_notifications():
                tree.delete(*tree.get_children())
                for row in get_notifications(self.user_info['user_id']):
                    tree.insert("", "end", values=(
                        row['notification_id'],
                        row['message'],
                        "Yes" if row['is_read'] else "No",
                        row['created_at']
                    ))

            def on_select(_event=None):
                nonlocal selected_notification_id
                sel = tree.selection()
                if not sel:
                    return
                selected_notification_id = int(tree.item(sel[0], "values")[0])

            def set_read():
                if selected_notification_id and mark_as_read(selected_notification_id):
                    load_notifications()

            ttk.Button(actions, text="Mark as Read", style="Accent.TButton", command=set_read).pack(side='left')
            tree.bind("<<TreeviewSelect>>", on_select)
            load_notifications()
        self.switch_view(view)

    def show_profile(self):
        def view():
            ttk.Label(self.content_frame, text="My Profile", style="PageTitle.TLabel").pack(pady=(24, 16))
            
            card = ttk.Frame(self.content_frame, style="Card.TFrame", padding=20)
            card.pack(fill='x', padx=20, pady=10)
            
            img_frame = ttk.Frame(card)
            img_frame.pack(side='left', padx=(0, 20))
            
            self.img_label = ttk.Label(img_frame, text="No Image", background="#ddd", width=20, anchor='center')
            self.img_label.pack(pady=(0, 10))
            
            def load_image():
                img_path = get_student_profile_image(self.user_info['user_id'])
                if img_path:
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((150, 150))
                        photo = ImageTk.PhotoImage(img)
                        self.img_label.config(image=photo, text="")
                        self.img_label.image = photo
                    except Exception as e:
                        self.img_label.config(text="Error loading image")
                else:
                    self.img_label.config(text="No Image", image='')
                    self.img_label.image = None
            
            def upload_image():
                file_path = filedialog.askopenfilename(
                    title="Select Profile Image",
                    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
                )
                if file_path:
                    success, msg = upload_profile_image(self.user_info['user_id'], file_path)
                    if success:
                        messagebox.showinfo("Success", msg)
                        load_image()
                    else:
                        messagebox.showerror("Error", msg)
                        
            ttk.Button(img_frame, text="Upload Image", command=upload_image).pack()
            
            info_frame = ttk.Frame(card)
            info_frame.pack(side='left', fill='both', expand=True)
            
            ttk.Label(info_frame, text=f"Username: {self.user_info.get('username', '')}", font=FONTS['h3']).pack(anchor='w', pady=(0, 5))
            ttk.Label(info_frame, text=f"Role: {self.user_info.get('role', '')}", font=FONTS['body']).pack(anchor='w', pady=(0, 5))
            
            load_image()
            
        self.switch_view(view)
