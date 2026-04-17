"""
Admin Dashboard to manage students, faculty, and view system logs.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from gui.dashboard import BaseDashboard
from config.settings import FONTS, COLORS
from services.student_service import get_all_students
from services.faculty_service import get_all_faculty
from services.admin_service import (
    get_all_courses,
    add_course,
    update_course,
    delete_course,
    get_all_rooms,
    add_room,
    update_room,
    delete_room,
    get_all_sections,
    add_section,
    update_section,
    delete_section,
    get_all_timetable,
    add_timetable_entry,
    update_timetable_entry,
    delete_timetable_entry,
    get_admin_overview_counts,
    get_all_departments,
    get_audit_logs
)
from services.leave_service import get_all_leave_requests, review_leave_request
from services.notification_service import create_notification

class AdminDashboard(BaseDashboard):
    def __init__(self, user_info, on_logout=None):
        super().__init__("Admin Panel", user_info, on_logout)
    
    def setup_menu(self):
        self.add_menu_item("Overview", self.show_overview)
        self.add_menu_item("Manage Students", self.show_manage_students)
        self.add_menu_item("Manage Faculty", self.show_manage_faculty)
        self.add_menu_item("Academic Setup", self.show_academic_setup)
        self.add_menu_item("Leave Requests", self.show_leave_requests)
        self.add_menu_item("Audit Logs", self.show_audit_logs)
        
        # Default view
        self.show_overview()

    def show_overview(self):
        def view():
            ttk.Label(self.content_frame, text="Admin Overview", style="PageTitle.TLabel").pack(pady=(24, 16))
            counts = get_admin_overview_counts()
            cards = ttk.Frame(self.content_frame, style="Content.TFrame")
            cards.pack(fill='x', padx=16, pady=6)

            items = [
                ("Students", counts.get('students_count', 0)),
                ("Faculty", counts.get('faculty_count', 0)),
                ("Courses", counts.get('courses_count', 0)),
                ("Sections", counts.get('sections_count', 0)),
                ("Timetable Slots", counts.get('timetable_count', 0)),
            ]

            for idx, (label, value) in enumerate(items):
                card = ttk.Frame(cards, style="Card.TFrame", padding=16)
                card.grid(row=0, column=idx, padx=8, sticky='nsew')
                ttk.Label(card, text=label, style="CardBody.TLabel").pack(anchor='w')
                ttk.Label(card, text=str(value), style="CardHeader.TLabel").pack(anchor='w', pady=(8, 0))
                cards.grid_columnconfigure(idx, weight=1)
        self.switch_view(view)

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

    def show_manage_students(self):
        def view():
            ttk.Label(self.content_frame, text="Students", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("ID", "Username", "First Name", "Last Name", "Enrollment Date", "Department")
            tree = self._build_table(self.content_frame, columns)
            students = get_all_students()
            for s in students:
                tree.insert("", "end", values=(s['student_id'], s['username'], s['first_name'], s['last_name'], s['enrollment_date'], s['dept_name']))
                
        self.switch_view(view)

    def show_manage_faculty(self):
        def view():
            ttk.Label(self.content_frame, text="Faculty", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("ID", "Username", "First Name", "Last Name", "Hire Date", "Department")
            tree = self._build_table(self.content_frame, columns)
            faculty = get_all_faculty()
            for f in faculty:
                tree.insert("", "end", values=(f['faculty_id'], f['username'], f['first_name'], f['last_name'], f['hire_date'], f['dept_name']))
        self.switch_view(view)

    def show_academic_setup(self):
        def view():
            ttk.Label(self.content_frame, text="Academic Setup", style="PageTitle.TLabel").pack(pady=(24, 12))
            info_card = ttk.Frame(self.content_frame, style="Card.TFrame", padding=12)
            info_card.pack(fill='x', padx=16, pady=(0, 8))
            ttk.Label(
                info_card,
                text="Manage Courses, Rooms, Sections, and Timetable here. Select a row to Edit/Delete, or clear form to Add new.",
                style="CardBody.TLabel"
            ).pack(anchor='w')

            notebook = ttk.Notebook(self.content_frame)
            notebook.pack(expand=True, fill='both', padx=16, pady=10)

            course_tab = ttk.Frame(notebook, style="Content.TFrame")
            room_tab = ttk.Frame(notebook, style="Content.TFrame")
            section_tab = ttk.Frame(notebook, style="Content.TFrame")
            timetable_tab = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(course_tab, text="Courses")
            notebook.add(room_tab, text="Rooms")
            notebook.add(section_tab, text="Sections")
            notebook.add(timetable_tab, text="Timetable")

            self._build_course_tab(course_tab)
            self._build_room_tab(room_tab)
            self._build_section_tab(section_tab)
            self._build_timetable_tab(timetable_tab)
        self.switch_view(view)

    def _build_course_tab(self, parent):
        selected_course_id = None
        form_card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        form_card.pack(fill='x', padx=12, pady=12)
        title_label = ttk.Label(form_card, text="Add Course", style="CardHeader.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))

        ttk.Label(form_card, text="Course Code", style="CardBody.TLabel").grid(row=1, column=0, sticky='w', pady=4)
        code_entry = ttk.Entry(form_card, font=FONTS['body'])
        code_entry.grid(row=1, column=1, sticky='ew', pady=4, padx=(12, 0))

        ttk.Label(form_card, text="Course Name", style="CardBody.TLabel").grid(row=2, column=0, sticky='w', pady=4)
        name_entry = ttk.Entry(form_card, font=FONTS['body'])
        name_entry.grid(row=2, column=1, sticky='ew', pady=4, padx=(12, 0))

        ttk.Label(form_card, text="Credits", style="CardBody.TLabel").grid(row=3, column=0, sticky='w', pady=4)
        credits_entry = ttk.Entry(form_card, font=FONTS['body'])
        credits_entry.grid(row=3, column=1, sticky='ew', pady=4, padx=(12, 0))

        departments = get_all_departments()
        dept_map = {d['dept_name']: d['dept_id'] for d in departments}
        ttk.Label(form_card, text="Department", style="CardBody.TLabel").grid(row=4, column=0, sticky='w', pady=4)
        dept_combo = ttk.Combobox(form_card, values=list(dept_map.keys()), state='readonly')
        dept_combo.grid(row=4, column=1, sticky='ew', pady=4, padx=(12, 0))
        if dept_map:
            dept_combo.current(0)

        form_card.grid_columnconfigure(1, weight=1)
        columns = ("Course ID", "Code", "Name", "Credits", "Department")
        tree = self._build_table(parent, columns)

        def load_courses():
            tree.delete(*tree.get_children())
            for course in get_all_courses():
                tree.insert("", "end", values=(
                    course['course_id'],
                    course['course_code'],
                    course['course_name'],
                    course['credits'],
                    course['dept_name']
                ))

        def submit_course():
            nonlocal selected_course_id
            code = code_entry.get().strip().upper()
            name = name_entry.get().strip()
            credits = credits_entry.get().strip()
            dept_name = dept_combo.get().strip()
            if not code or not name or not credits or not dept_name:
                messagebox.showerror("Validation Error", "Please fill all fields.")
                return
            if not credits.isdigit() or int(credits) <= 0:
                messagebox.showerror("Validation Error", "Credits must be a positive number.")
                return
            if selected_course_id is None:
                if add_course(code, name, int(credits), dept_map[dept_name]):
                    messagebox.showinfo("Success", "Course added successfully.")
                    reset_course_form()
                    load_courses()
                else:
                    messagebox.showerror("Error", "Failed to add course. Code may already exist.")
            else:
                if update_course(selected_course_id, code, name, int(credits), dept_map[dept_name]):
                    messagebox.showinfo("Success", "Course updated successfully.")
                    reset_course_form()
                    load_courses()
                else:
                    messagebox.showerror("Error", "Failed to update course.")

        def on_course_select(_event=None):
            nonlocal selected_course_id
            selection = tree.selection()
            if not selection:
                return
            values = tree.item(selection[0], "values")
            selected_course_id = int(values[0])
            code_entry.delete(0, 'end')
            code_entry.insert(0, values[1])
            name_entry.delete(0, 'end')
            name_entry.insert(0, values[2])
            credits_entry.delete(0, 'end')
            credits_entry.insert(0, values[3])
            dept_name = values[4]
            if dept_name in dept_map:
                dept_combo.set(dept_name)
            title_label.config(text="Edit Course")
            submit_btn.config(text="Update Course")

        def reset_course_form():
            nonlocal selected_course_id
            selected_course_id = None
            code_entry.delete(0, 'end')
            name_entry.delete(0, 'end')
            credits_entry.delete(0, 'end')
            if dept_map:
                dept_combo.current(0)
            title_label.config(text="Add Course")
            submit_btn.config(text="Add Course")
            tree.selection_remove(*tree.selection())

        def remove_course():
            nonlocal selected_course_id
            if selected_course_id is None:
                messagebox.showwarning("Selection Required", "Select a course to delete.")
                return
            if not messagebox.askyesno("Confirm Delete", "Delete selected course?"):
                return
            if delete_course(selected_course_id):
                messagebox.showinfo("Success", "Course deleted successfully.")
                reset_course_form()
                load_courses()
            else:
                messagebox.showerror("Error", "Failed to delete course. It may be in use by sections.")

        actions = ttk.Frame(form_card, style="Card.TFrame")
        actions.grid(row=5, column=1, sticky='e', pady=(14, 0))
        submit_btn = ttk.Button(actions, text="Add Course", style="Accent.TButton", command=submit_course)
        submit_btn.pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Delete", command=remove_course).pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Clear", command=reset_course_form).pack(side='left')
        tree.bind("<<TreeviewSelect>>", on_course_select)
        load_courses()

    def _build_room_tab(self, parent):
        selected_room_id = None
        form_card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        form_card.pack(fill='x', padx=12, pady=12)
        title_label = ttk.Label(form_card, text="Add Room", style="CardHeader.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))

        ttk.Label(form_card, text="Room Name", style="CardBody.TLabel").grid(row=1, column=0, sticky='w', pady=4)
        room_entry = ttk.Entry(form_card, font=FONTS['body'])
        room_entry.grid(row=1, column=1, sticky='ew', pady=4, padx=(12, 0))

        ttk.Label(form_card, text="Capacity", style="CardBody.TLabel").grid(row=2, column=0, sticky='w', pady=4)
        cap_entry = ttk.Entry(form_card, font=FONTS['body'])
        cap_entry.grid(row=2, column=1, sticky='ew', pady=4, padx=(12, 0))

        form_card.grid_columnconfigure(1, weight=1)
        columns = ("Room ID", "Room", "Capacity")
        tree = self._build_table(parent, columns)

        def load_rooms():
            tree.delete(*tree.get_children())
            for room in get_all_rooms():
                tree.insert("", "end", values=(room['room_id'], room['room_name'], room['capacity']))

        def submit_room():
            nonlocal selected_room_id
            room_name = room_entry.get().strip().upper()
            capacity = cap_entry.get().strip()
            if not room_name or not capacity:
                messagebox.showerror("Validation Error", "Please fill all fields.")
                return
            if not capacity.isdigit() or int(capacity) <= 0:
                messagebox.showerror("Validation Error", "Capacity must be a positive number.")
                return
            if selected_room_id is None:
                if add_room(room_name, int(capacity)):
                    messagebox.showinfo("Success", "Room added successfully.")
                    reset_room_form()
                    load_rooms()
                else:
                    messagebox.showerror("Error", "Failed to add room. Name may already exist.")
            else:
                if update_room(selected_room_id, room_name, int(capacity)):
                    messagebox.showinfo("Success", "Room updated successfully.")
                    reset_room_form()
                    load_rooms()
                else:
                    messagebox.showerror("Error", "Failed to update room.")

        def on_room_select(_event=None):
            nonlocal selected_room_id
            selection = tree.selection()
            if not selection:
                return
            values = tree.item(selection[0], "values")
            selected_room_id = int(values[0])
            room_entry.delete(0, 'end')
            room_entry.insert(0, values[1])
            cap_entry.delete(0, 'end')
            cap_entry.insert(0, values[2])
            title_label.config(text="Edit Room")
            submit_btn.config(text="Update Room")

        def reset_room_form():
            nonlocal selected_room_id
            selected_room_id = None
            room_entry.delete(0, 'end')
            cap_entry.delete(0, 'end')
            title_label.config(text="Add Room")
            submit_btn.config(text="Add Room")
            tree.selection_remove(*tree.selection())

        def remove_room():
            nonlocal selected_room_id
            if selected_room_id is None:
                messagebox.showwarning("Selection Required", "Select a room to delete.")
                return
            if not messagebox.askyesno("Confirm Delete", "Delete selected room?"):
                return
            if delete_room(selected_room_id):
                messagebox.showinfo("Success", "Room deleted successfully.")
                reset_room_form()
                load_rooms()
            else:
                messagebox.showerror("Error", "Failed to delete room. It may be used by sections/timetable.")

        actions = ttk.Frame(form_card, style="Card.TFrame")
        actions.grid(row=3, column=1, sticky='e', pady=(14, 0))
        submit_btn = ttk.Button(actions, text="Add Room", style="Accent.TButton", command=submit_room)
        submit_btn.pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Delete", command=remove_room).pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Clear", command=reset_room_form).pack(side='left')
        tree.bind("<<TreeviewSelect>>", on_room_select)
        load_rooms()

    def _build_section_tab(self, parent):
        selected_section_id = None
        form_card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        form_card.pack(fill='x', padx=12, pady=12)
        title_label = ttk.Label(form_card, text="Add Section", style="CardHeader.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))

        courses = get_all_courses()
        course_map = {f"{c['course_code']} - {c['course_name']}": c['course_id'] for c in courses}
        faculty_rows = get_all_faculty()
        faculty_map = {f"{f['first_name']} {f['last_name']} ({f['username']})": f['faculty_id'] for f in faculty_rows}
        rooms = get_all_rooms()
        room_map = {r['room_name']: r['room_id'] for r in rooms}

        ttk.Label(form_card, text="Course", style="CardBody.TLabel").grid(row=1, column=0, sticky='w', pady=4)
        course_combo = ttk.Combobox(form_card, values=list(course_map.keys()), state='readonly')
        course_combo.grid(row=1, column=1, sticky='ew', pady=4, padx=(12, 0))
        if course_map:
            course_combo.current(0)

        ttk.Label(form_card, text="Faculty", style="CardBody.TLabel").grid(row=2, column=0, sticky='w', pady=4)
        faculty_combo = ttk.Combobox(form_card, values=list(faculty_map.keys()), state='readonly')
        faculty_combo.grid(row=2, column=1, sticky='ew', pady=4, padx=(12, 0))
        if faculty_map:
            faculty_combo.current(0)

        ttk.Label(form_card, text="Room", style="CardBody.TLabel").grid(row=3, column=0, sticky='w', pady=4)
        room_combo = ttk.Combobox(form_card, values=list(room_map.keys()), state='readonly')
        room_combo.grid(row=3, column=1, sticky='ew', pady=4, padx=(12, 0))
        if room_map:
            room_combo.current(0)

        ttk.Label(form_card, text="Semester", style="CardBody.TLabel").grid(row=4, column=0, sticky='w', pady=4)
        semester_combo = ttk.Combobox(form_card, values=["Spring", "Summer", "Fall", "Winter"], state='readonly')
        semester_combo.grid(row=4, column=1, sticky='ew', pady=4, padx=(12, 0))
        semester_combo.set("Spring")

        ttk.Label(form_card, text="Academic Year", style="CardBody.TLabel").grid(row=5, column=0, sticky='w', pady=4)
        year_entry = ttk.Entry(form_card, font=FONTS['body'])
        year_entry.grid(row=5, column=1, sticky='ew', pady=4, padx=(12, 0))
        year_entry.insert(0, "2025-26")

        form_card.grid_columnconfigure(1, weight=1)
        columns = ("Section ID", "Course Code", "Course Name", "Faculty", "Room", "Semester", "Year")
        tree = self._build_table(parent, columns)

        def load_sections():
            tree.delete(*tree.get_children())
            for section in get_all_sections():
                tree.insert("", "end", values=(
                    section['section_id'],
                    section['course_code'],
                    section['course_name'],
                    section['faculty_name'],
                    section['room_name'],
                    section['semester'],
                    section['academic_year']
                ))

        def submit_section():
            nonlocal selected_section_id
            course_key = course_combo.get().strip()
            faculty_key = faculty_combo.get().strip()
            room_key = room_combo.get().strip()
            semester = semester_combo.get().strip()
            academic_year = year_entry.get().strip()
            if not all([course_key, faculty_key, room_key, semester, academic_year]):
                messagebox.showerror("Validation Error", "Please fill all fields.")
                return
            if selected_section_id is None:
                if add_section(course_map[course_key], faculty_map[faculty_key], room_map[room_key], semester, academic_year):
                    messagebox.showinfo("Success", "Section added successfully.")
                    reset_section_form()
                    load_sections()
                else:
                    messagebox.showerror("Error", "Failed to add section. Check uniqueness constraints.")
            else:
                if update_section(selected_section_id, course_map[course_key], faculty_map[faculty_key], room_map[room_key], semester, academic_year):
                    messagebox.showinfo("Success", "Section updated successfully.")
                    reset_section_form()
                    load_sections()
                else:
                    messagebox.showerror("Error", "Failed to update section. Check uniqueness constraints.")

        code_to_course_key = {c['course_code']: f"{c['course_code']} - {c['course_name']}" for c in courses}
        name_to_room_key = {r['room_name']: r['room_name'] for r in rooms}
        name_to_faculty_key = {f"{f['first_name']} {f['last_name']}": f"{f['first_name']} {f['last_name']} ({f['username']})" for f in faculty_rows}

        def on_section_select(_event=None):
            nonlocal selected_section_id
            selection = tree.selection()
            if not selection:
                return
            values = tree.item(selection[0], "values")
            selected_section_id = int(values[0])
            course_key = code_to_course_key.get(values[1])
            faculty_key = name_to_faculty_key.get(values[3])
            room_key = name_to_room_key.get(values[4])
            if course_key:
                course_combo.set(course_key)
            if faculty_key:
                faculty_combo.set(faculty_key)
            if room_key:
                room_combo.set(room_key)
            semester_combo.set(values[5])
            year_entry.delete(0, 'end')
            year_entry.insert(0, values[6])
            title_label.config(text="Edit Section")
            submit_btn.config(text="Update Section")

        def reset_section_form():
            nonlocal selected_section_id
            selected_section_id = None
            if course_map:
                course_combo.current(0)
            if faculty_map:
                faculty_combo.current(0)
            if room_map:
                room_combo.current(0)
            semester_combo.set("Spring")
            year_entry.delete(0, 'end')
            year_entry.insert(0, "2025-26")
            title_label.config(text="Add Section")
            submit_btn.config(text="Add Section")
            tree.selection_remove(*tree.selection())

        def remove_section():
            nonlocal selected_section_id
            if selected_section_id is None:
                messagebox.showwarning("Selection Required", "Select a section to delete.")
                return
            if not messagebox.askyesno("Confirm Delete", "Delete selected section?"):
                return
            if delete_section(selected_section_id):
                messagebox.showinfo("Success", "Section deleted successfully.")
                reset_section_form()
                load_sections()
            else:
                messagebox.showerror("Error", "Failed to delete section. It may be used by enrollments/timetable.")

        actions = ttk.Frame(form_card, style="Card.TFrame")
        actions.grid(row=6, column=1, sticky='e', pady=(14, 0))
        submit_btn = ttk.Button(actions, text="Add Section", style="Accent.TButton", command=submit_section)
        submit_btn.pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Delete", command=remove_section).pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Clear", command=reset_section_form).pack(side='left')
        tree.bind("<<TreeviewSelect>>", on_section_select)
        load_sections()

    def _build_timetable_tab(self, parent):
        selected_timetable_id = None
        form_card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        form_card.pack(fill='x', padx=12, pady=12)
        title_label = ttk.Label(form_card, text="Add Timetable Slot", style="CardHeader.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 12))

        sections = get_all_sections()
        section_map = {
            f"{s['section_id']} - {s['course_code']} ({s['semester']} {s['academic_year']})": s['section_id']
            for s in sections
        }
        section_id_to_key = {v: k for k, v in section_map.items()}

        rooms = get_all_rooms()
        room_map = {r['room_name']: r['room_id'] for r in rooms}

        ttk.Label(form_card, text="Section", style="CardBody.TLabel").grid(row=1, column=0, sticky='w', pady=4)
        section_combo = ttk.Combobox(form_card, values=list(section_map.keys()), state='readonly')
        section_combo.grid(row=1, column=1, sticky='ew', pady=4, padx=(12, 0))
        if section_map:
            section_combo.current(0)

        ttk.Label(form_card, text="Day", style="CardBody.TLabel").grid(row=2, column=0, sticky='w', pady=4)
        day_combo = ttk.Combobox(
            form_card,
            values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            state='readonly'
        )
        day_combo.grid(row=2, column=1, sticky='ew', pady=4, padx=(12, 0))
        day_combo.set("Monday")

        ttk.Label(form_card, text="Start Time (HH:MM)", style="CardBody.TLabel").grid(row=3, column=0, sticky='w', pady=4)
        start_entry = ttk.Entry(form_card, font=FONTS['body'])
        start_entry.grid(row=3, column=1, sticky='ew', pady=4, padx=(12, 0))
        start_entry.insert(0, "09:00")

        ttk.Label(form_card, text="End Time (HH:MM)", style="CardBody.TLabel").grid(row=4, column=0, sticky='w', pady=4)
        end_entry = ttk.Entry(form_card, font=FONTS['body'])
        end_entry.grid(row=4, column=1, sticky='ew', pady=4, padx=(12, 0))
        end_entry.insert(0, "10:00")

        ttk.Label(form_card, text="Room", style="CardBody.TLabel").grid(row=5, column=0, sticky='w', pady=4)
        room_combo = ttk.Combobox(form_card, values=list(room_map.keys()), state='readonly')
        room_combo.grid(row=5, column=1, sticky='ew', pady=4, padx=(12, 0))
        if room_map:
            room_combo.current(0)

        form_card.grid_columnconfigure(1, weight=1)
        columns = ("Timetable ID", "Section ID", "Course Code", "Course Name", "Day", "Start", "End", "Room")
        tree = self._build_table(parent, columns)

        def is_valid_time(value):
            parts = value.split(":")
            if len(parts) != 2 or (not parts[0].isdigit()) or (not parts[1].isdigit()):
                return False
            hour = int(parts[0])
            minute = int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59

        def load_timetable():
            tree.delete(*tree.get_children())
            for slot in get_all_timetable():
                tree.insert("", "end", values=(
                    slot['timetable_id'],
                    slot['section_id'],
                    slot['course_code'],
                    slot['course_name'],
                    slot['day_of_week'],
                    str(slot['start_time'])[:5],
                    str(slot['end_time'])[:5],
                    slot['room_name']
                ))

        def submit_timetable():
            nonlocal selected_timetable_id
            section_key = section_combo.get().strip()
            day = day_combo.get().strip()
            start_time = start_entry.get().strip()
            end_time = end_entry.get().strip()
            room_key = room_combo.get().strip()
            if not all([section_key, day, start_time, end_time, room_key]):
                messagebox.showerror("Validation Error", "Please fill all fields.")
                return
            if not is_valid_time(start_time) or not is_valid_time(end_time):
                messagebox.showerror("Validation Error", "Time format must be HH:MM.")
                return
            if end_time <= start_time:
                messagebox.showerror("Validation Error", "End time must be after start time.")
                return

            section_id = section_map[section_key]
            room_id = room_map[room_key]

            if selected_timetable_id is None:
                success = add_timetable_entry(section_id, day, start_time, end_time, room_id)
                success_message = "Timetable slot added successfully."
                fail_message = "Failed to add timetable slot."
            else:
                success = update_timetable_entry(selected_timetable_id, section_id, day, start_time, end_time, room_id)
                success_message = "Timetable slot updated successfully."
                fail_message = "Failed to update timetable slot."

            if success:
                messagebox.showinfo("Success", success_message)
                reset_timetable_form()
                load_timetable()
            else:
                messagebox.showerror("Error", fail_message)

        def on_timetable_select(_event=None):
            nonlocal selected_timetable_id
            selection = tree.selection()
            if not selection:
                return
            values = tree.item(selection[0], "values")
            selected_timetable_id = int(values[0])
            section_id_value = values[1]
            room_name_value = values[7]
            if isinstance(section_id_value, int):
                key = section_id_to_key.get(section_id_value)
                if key:
                    section_combo.set(key)
            elif str(section_id_value).isdigit():
                key = section_id_to_key.get(int(section_id_value))
                if key:
                    section_combo.set(key)
            if room_name_value in room_map:
                room_combo.set(room_name_value)
            day_combo.set(values[4])
            start_entry.delete(0, 'end')
            start_entry.insert(0, values[5])
            end_entry.delete(0, 'end')
            end_entry.insert(0, values[6])
            title_label.config(text="Edit Timetable Slot")
            submit_btn.config(text="Update Slot")

        def reset_timetable_form():
            nonlocal selected_timetable_id
            selected_timetable_id = None
            if section_map:
                section_combo.current(0)
            if room_map:
                room_combo.current(0)
            day_combo.set("Monday")
            start_entry.delete(0, 'end')
            start_entry.insert(0, "09:00")
            end_entry.delete(0, 'end')
            end_entry.insert(0, "10:00")
            title_label.config(text="Add Timetable Slot")
            submit_btn.config(text="Add Slot")
            tree.selection_remove(*tree.selection())

        def remove_timetable():
            nonlocal selected_timetable_id
            if selected_timetable_id is None:
                messagebox.showwarning("Selection Required", "Select a timetable row to delete.")
                return
            if not messagebox.askyesno("Confirm Delete", "Delete selected timetable slot?"):
                return
            if delete_timetable_entry(selected_timetable_id):
                messagebox.showinfo("Success", "Timetable slot deleted successfully.")
                reset_timetable_form()
                load_timetable()
            else:
                messagebox.showerror("Error", "Failed to delete timetable slot.")

        actions = ttk.Frame(form_card, style="Card.TFrame")
        actions.grid(row=6, column=1, sticky='e', pady=(14, 0))
        submit_btn = ttk.Button(actions, text="Add Slot", style="Accent.TButton", command=submit_timetable)
        submit_btn.pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Delete", command=remove_timetable).pack(side='left', padx=(0, 8))
        ttk.Button(actions, text="Clear", command=reset_timetable_form).pack(side='left')

        tree.bind("<<TreeviewSelect>>", on_timetable_select)
        load_timetable()

    def show_audit_logs(self):
        def view():
            ttk.Label(self.content_frame, text="Audit Logs", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Log ID", "Username", "Action", "Table", "Record ID", "Timestamp")
            tree = self._build_table(self.content_frame, columns)
            for log in get_audit_logs():
                tree.insert("", "end", values=(
                    log['log_id'],
                    log['username'],
                    log['action'],
                    log['table_name'],
                    log['record_id'],
                    log['timestamp']
                ))
        self.switch_view(view)

    def show_leave_requests(self):
        def view():
            selected_leave_id = None
            selected_status = None
            selected_requester_user_id = None
            leave_rows_cache = []
            ttk.Label(self.content_frame, text="Leave Requests", style="PageTitle.TLabel").pack(pady=(24, 16))
            columns = ("Leave ID", "Requester", "Role", "Start Date", "End Date", "Reason", "Status", "Reviewed By", "Submitted At")
            tree = self._build_table(self.content_frame, columns)

            actions = ttk.Frame(self.content_frame, style="Content.TFrame")
            actions.pack(fill='x', padx=20, pady=(0, 16))

            def load_leave_requests():
                nonlocal leave_rows_cache
                tree.delete(*tree.get_children())
                leave_rows_cache = get_all_leave_requests()
                for row in leave_rows_cache:
                    tree.insert("", "end", values=(
                        row['leave_id'],
                        row['requester_username'],
                        row['requester_role'],
                        row['start_date'],
                        row['end_date'],
                        row['reason'],
                        row['status'],
                        row['reviewed_by'],
                        row['created_at']
                    ), tags=(row['status'],))
                tree.tag_configure("Pending", foreground="#f39c12")
                tree.tag_configure("Approved", foreground="#27ae60")
                tree.tag_configure("Rejected", foreground="#c0392b")

            def on_select(_event=None):
                nonlocal selected_leave_id, selected_status, selected_requester_user_id
                sel = tree.selection()
                if not sel:
                    return
                values = tree.item(sel[0], "values")
                selected_leave_id = int(values[0])
                selected_status = values[6]
                selected_requester_user_id = None
                for row in leave_rows_cache:
                    if int(row['leave_id']) == selected_leave_id:
                        selected_requester_user_id = row['requester_user_id']
                        break

            def review(status):
                if selected_leave_id is None:
                    messagebox.showwarning("Selection Required", "Select a leave request first.")
                    return
                if selected_status != "Pending":
                    messagebox.showwarning("Already Reviewed", "Only pending requests can be reviewed.")
                    return
                if review_leave_request(selected_leave_id, status, self.user_info['user_id']):
                    if selected_requester_user_id:
                        create_notification(
                            selected_requester_user_id,
                            f"Your leave request #{selected_leave_id} has been {status.lower()} by admin."
                        )
                    messagebox.showinfo("Success", f"Leave request {status.lower()}.")
                    load_leave_requests()
                else:
                    messagebox.showerror("Error", "Failed to review leave request.")

            ttk.Button(actions, text="Approve", style="Accent.TButton", command=lambda: review("Approved")).pack(side='left', padx=(0, 10))
            ttk.Button(actions, text="Reject", command=lambda: review("Rejected")).pack(side='left')

            tree.bind("<<TreeviewSelect>>", on_select)
            load_leave_requests()
        self.switch_view(view)
