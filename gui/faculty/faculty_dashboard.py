"""
Faculty Dashboard to mark attendance and manage sections.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from gui.dashboard import BaseDashboard
from config.settings import FONTS, COLORS
from services.attendance_service import (
    get_assigned_sections,
    create_session,
    get_students_for_section,
    submit_attendance,
    get_faculty_session_history
)
from services.timetable_service import get_timetable_for_faculty
from services.leave_service import create_leave_request, get_leave_requests_for_user
from services.notification_service import get_notifications, mark_as_read
from utils.validators import is_valid_date
from datetime import datetime

class FacultyDashboard(BaseDashboard):
    def __init__(self, user_info, on_logout=None):
        super().__init__("Faculty Portal", user_info, on_logout)
    
    def setup_menu(self):
        self.add_menu_item("Overview", self.show_overview)
        self.add_menu_item("My Sections", self.show_sections)
        self.add_menu_item("My Timetable", self.show_timetable)
        self.add_menu_item("Mark Attendance", self.show_mark_attendance)
        self.add_menu_item("Session History", self.show_session_history)
        self.add_menu_item("Leave Requests", self.show_leave_requests)
        self.add_menu_item("Notifications", self.show_notifications)
        
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
            tree.column(col, width=140, anchor='center')
        return tree

    def show_overview(self):
        def view():
            ttk.Label(self.content_frame, text="Faculty Overview", style="PageTitle.TLabel").pack(pady=(24, 16))
            sections = get_assigned_sections(self.user_info['user_id'])
            sessions = get_faculty_session_history(self.user_info['user_id'])
            timetable_rows = get_timetable_for_faculty(self.user_info['user_id'])

            cards = ttk.Frame(self.content_frame, style="Content.TFrame")
            cards.pack(fill='x', padx=16, pady=6)
            items = [
                ("Assigned Sections", len(sections)),
                ("Timetable Slots", len(timetable_rows)),
                ("Attendance Sessions", len(sessions)),
            ]
            for idx, (label, value) in enumerate(items):
                card = ttk.Frame(cards, style="Card.TFrame", padding=16)
                card.grid(row=0, column=idx, padx=8, sticky='nsew')
                ttk.Label(card, text=label, style="CardBody.TLabel").pack(anchor='w')
                ttk.Label(card, text=str(value), style="CardHeader.TLabel").pack(anchor='w', pady=(8, 0))
                cards.grid_columnconfigure(idx, weight=1)
        self.switch_view(view)

    def show_sections(self):
        def view():
            ttk.Label(self.content_frame, text="Assigned Sections", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Section ID", "Course Code", "Course Name", "Semester")
            tree = self._build_table(self.content_frame, columns)
            sections = get_assigned_sections(self.user_info['user_id'])
            for s in sections:
                tree.insert("", "end", values=(s['section_id'], s['course_code'], s['course_name'], s['semester']))
                
        self.switch_view(view)

    def show_timetable(self):
        def view():
            ttk.Label(self.content_frame, text="My Timetable", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Section ID", "Course Code", "Course Name", "Day", "Start", "End", "Room")
            tree = self._build_table(self.content_frame, columns)
            rows = get_timetable_for_faculty(self.user_info['user_id'])
            for row in rows:
                tree.insert("", "end", values=(
                    row['section_id'],
                    row['course_code'],
                    row['course_name'],
                    row['day_of_week'],
                    str(row['start_time'])[:5],
                    str(row['end_time'])[:5],
                    row['room_name']
                ))
        self.switch_view(view)

    def show_mark_attendance(self):
        def view():
            ttk.Label(self.content_frame, text="Mark Attendance", style="PageTitle.TLabel").pack(pady=(24, 16))

            form_frame = ttk.Frame(self.content_frame, style="Card.TFrame", padding=16)
            form_frame.pack(fill='x', padx=20, pady=(0, 12))

            sections = get_assigned_sections(self.user_info['user_id'])
            section_map = {f"{s['section_id']} - {s['course_code']} {s['semester']}": s['section_id'] for s in sections}

            ttk.Label(form_frame, text="Select Section", style="CardBody.TLabel").pack(anchor='w', pady=(0, 4))
            section_combo = ttk.Combobox(form_frame, values=list(section_map.keys()), state='readonly')
            section_combo.pack(fill='x', pady=(0, 10))
            if section_map:
                section_combo.current(0)
            
            def load_students():
                section_key = section_combo.get().strip()
                if not section_key:
                    messagebox.showerror("Error", "Please select a section.")
                    return
                sec_id = section_map[section_key]
                students = get_students_for_section(sec_id)
                
                for widget in list_frame.winfo_children():
                    widget.destroy()
                
                if not students:
                    tk.Label(list_frame, text="No students found.", bg=COLORS['background']).pack()
                    return
                
                import datetime
                now = datetime.datetime.now()
                start_time = now.time().replace(second=0, microsecond=0)
                end_time = (now + datetime.timedelta(hours=1)).time().replace(second=0, microsecond=0)
                session_id = create_session(sec_id, now.date(), start_time, end_time, self.user_info['user_id'])
                
                if not session_id:
                    messagebox.showerror("Session Error", "Could not create attendance session.")
                    return
                
                tk.Label(list_frame, text=f"Session #{session_id} Created. Mark below:", bg=COLORS['background'], font=FONTS['body_bold']).pack(pady=10)
                
                # Create rows of students
                self.attendance_vars = {} # student_id -> status
                for s in students:
                    row = tk.Frame(list_frame, bg=COLORS['background'])
                    row.pack(fill='x', pady=2)
                    tk.Label(row, text=f"{s['first_name']} {s['last_name']} (ID: {s['student_id']})", bg=COLORS['background'], width=30, anchor='w').pack(side='left')
                    
                    status_var = tk.StringVar(value="Present")
                    self.attendance_vars[s['student_id']] = status_var
                    
                    ttk.Radiobutton(row, text="Present", variable=status_var, value="Present").pack(side='left', padx=5)
                    ttk.Radiobutton(row, text="Absent", variable=status_var, value="Absent").pack(side='left', padx=5)
                    ttk.Radiobutton(row, text="Late", variable=status_var, value="Late").pack(side='left', padx=5)

                def save_all():
                    failed = 0
                    for sid, var in self.attendance_vars.items():
                        if not submit_attendance(session_id, sid, var.get()):
                            failed += 1
                    if failed:
                        messagebox.showwarning("Partial Save", f"{failed} attendance rows failed to save.")
                    else:
                        messagebox.showinfo("Success", "Attendance saved successfully!")
                
                ttk.Button(list_frame, text="Save All Attendance", command=save_all).pack(pady=20)

            ttk.Button(form_frame, text="Load Students", style="Accent.TButton", command=load_students).pack(anchor='e')
            
            list_frame = tk.Frame(self.content_frame, bg=COLORS['background'])
            list_frame.pack(expand=True, fill='both', padx=20, pady=20)
            
        self.switch_view(view)

    def show_session_history(self):
        def view():
            ttk.Label(self.content_frame, text="Attendance Session History", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Session ID", "Date", "Start", "End", "Section", "Course Code", "Course Name")
            tree = self._build_table(self.content_frame, columns)
            sessions = get_faculty_session_history(self.user_info['user_id'])
            for sess in sessions:
                tree.insert("", "end", values=(
                    sess['session_id'],
                    sess['session_date'],
                    str(sess['start_time'])[:5],
                    str(sess['end_time'])[:5],
                    sess['section_id'],
                    sess['course_code'],
                    sess['course_name']
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
                    ), tags=("read" if row['is_read'] else "unread",))
                tree.tag_configure("read", foreground="#7f8c8d")
                tree.tag_configure("unread", foreground="#2c3e50")

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
