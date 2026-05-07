"""
Admin Dashboard to manage students, faculty, and view system logs.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from gui.dashboard import BaseDashboard
from config.settings import FONTS, COLORS
from services.user_service import get_all_students
from services.user_service import get_all_faculty
from services.user_service import (
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
    get_audit_logs,
    get_all_enrollments,
    add_enrollment,
    get_eligible_sections_for_student
)
from services.user_service import get_all_leave_requests, review_leave_request
from services.user_service import create_notification, broadcast_notification
from tkinter import filedialog
from services.report_service import (
    get_overall_attendance_stats,
    get_department_attendance_rates,
    export_attendance_to_csv,
    get_faculty_workload_report,
    get_faculty_workload_semester_summary,
    get_faculty_monthly_sessions,
    get_department_ranking,
    get_student_trends,
    get_course_prerequisite_map,
    get_student_prerequisite_status
)
from services.attendance_service import archive_attendance_for_semester
from services.backup_service import backup_postgres_to_firebase, restore_firebase_to_postgres

class AdminDashboard(BaseDashboard):
    def __init__(self, user_info, on_logout=None):
        super().__init__("Admin Panel", user_info, on_logout)
    
    def setup_menu(self):
        self.add_menu_item("Overview", self.show_overview)
        self.add_menu_item("Manage Students", self.show_manage_students)
        self.add_menu_item("Manage Faculty", self.show_manage_faculty)
        self.add_menu_item("Academic Setup", self.show_academic_setup)
        self.add_menu_item("Prereqs & Enrollment", self.show_prerequisites)
        self.add_menu_item("Leave Requests", self.show_leave_requests)
        self.add_menu_item("Audit Logs", self.show_audit_logs)
        self.add_menu_item("Analytics", self.show_analytics)
        self.add_menu_item("Attendance Archive", self.show_archive)
        self.add_menu_item("Broadcast", self.show_broadcast)
        self.add_menu_item("Firebase Sync", self.show_firebase_sync)
        
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
            
            # Search Bar
            search_frame = ttk.Frame(self.content_frame, style="Card.TFrame", padding=10)
            search_frame.pack(fill='x', padx=20, pady=(0, 10))
            ttk.Label(search_frame, text="Search:", style="CardBody.TLabel").pack(side='left', padx=(0, 10))
            search_entry = ttk.Entry(search_frame, font=FONTS['body'], width=30)
            search_entry.pack(side='left', padx=(0, 10))
            
            columns = ("ID", "Username", "First Name", "Last Name", "Enrollment Date", "Department")
            tree = self._build_table(self.content_frame, columns)
            students = get_all_students()
            
            def load_students(filter_text=""):
                tree.delete(*tree.get_children())
                for s in students:
                    if filter_text.lower() in s['username'].lower() or filter_text.lower() in s['first_name'].lower() or filter_text.lower() in s['last_name'].lower():
                        tree.insert("", "end", values=(s['student_id'], s['username'], s['first_name'], s['last_name'], s['enrollment_date'], s['dept_name']))
            
            def on_search(*args):
                load_students(search_entry.get())
                
            search_entry.bind('<KeyRelease>', on_search)
            load_students()
                
        self.switch_view(view)

    def show_manage_faculty(self):
        def view():
            ttk.Label(self.content_frame, text="Faculty", style="PageTitle.TLabel").pack(pady=(24, 16))
            
            # Search Bar
            search_frame = ttk.Frame(self.content_frame, style="Card.TFrame", padding=10)
            search_frame.pack(fill='x', padx=20, pady=(0, 10))
            ttk.Label(search_frame, text="Search:", style="CardBody.TLabel").pack(side='left', padx=(0, 10))
            search_entry = ttk.Entry(search_frame, font=FONTS['body'], width=30)
            search_entry.pack(side='left', padx=(0, 10))
            
            columns = ("ID", "Username", "First Name", "Last Name", "Hire Date", "Department")
            tree = self._build_table(self.content_frame, columns)
            faculty = get_all_faculty()
            
            def load_faculty(filter_text=""):
                tree.delete(*tree.get_children())
                for f in faculty:
                    if filter_text.lower() in f['username'].lower() or filter_text.lower() in f['first_name'].lower() or filter_text.lower() in f['last_name'].lower():
                        tree.insert("", "end", values=(f['faculty_id'], f['username'], f['first_name'], f['last_name'], f['hire_date'], f['dept_name']))
            
            def on_search(*args):
                load_faculty(search_entry.get())
                
            search_entry.bind('<KeyRelease>', on_search)
            load_faculty()
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

    def show_prerequisites(self):
        def view():
            ttk.Label(self.content_frame, text="Prerequisites & Enrollment", style="PageTitle.TLabel").pack(pady=(24, 12))

            notebook = ttk.Notebook(self.content_frame)
            notebook.pack(expand=True, fill='both', padx=16, pady=10)

            # Tab 1: Course Prerequisite Map
            tab_map = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_map, text="Course Prerequisite Map")
            cols_map = ("Course Code", "Course Name", "Prereq Code", "Prereq Name")
            tree_map = self._build_table(tab_map, cols_map)
            for row in get_course_prerequisite_map():
                tree_map.insert("", "end", values=(
                    row['course_code'],
                    row['course_name'],
                    row['prereq_course_code'],
                    row['prereq_course_name'],
                ))

            # Tab 2: Manage Enrollments (with prerequisite enforcement)
            tab_enroll = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_enroll, text="Enrollments")

            top_frame = ttk.Frame(tab_enroll, style="Card.TFrame", padding=12)
            top_frame.pack(fill='x', padx=16, pady=(10, 5))

            ttk.Label(top_frame, text="Student ID", style="CardBody.TLabel").grid(row=0, column=0, sticky='w')
            student_entry = ttk.Entry(top_frame, font=FONTS['body'])
            student_entry.grid(row=0, column=1, sticky='ew', padx=(8, 16))

            ttk.Label(top_frame, text="Section ID", style="CardBody.TLabel").grid(row=0, column=2, sticky='w')
            section_entry = ttk.Entry(top_frame, font=FONTS['body'])
            section_entry.grid(row=0, column=3, sticky='ew', padx=(8, 0))

            top_frame.grid_columnconfigure(1, weight=1)
            top_frame.grid_columnconfigure(3, weight=1)

            def handle_enroll():
                sid = student_entry.get().strip()
                sec = section_entry.get().strip()
                if not sid or not sec:
                    messagebox.showerror("Validation Error", "Provide both Student ID and Section ID.")
                    return
                if not sid.isdigit() or not sec.isdigit():
                    messagebox.showerror("Validation Error", "IDs must be numeric.")
                    return
                if add_enrollment(int(sid), int(sec)):
                    messagebox.showinfo("Success", "Enrollment created successfully (prerequisites validated in database).")
                    load_enrollments()
                else:
                    messagebox.showerror(
                        "Enrollment Failed",
                        "Could not enroll student. Check prerequisites, uniqueness, and IDs."
                    )

            ttk.Button(top_frame, text="Enroll Student", style="Accent.TButton", command=handle_enroll)\
                .grid(row=0, column=4, padx=(12, 0))

            columns = ("Enrollment ID", "Student", "Course Code", "Course Name", "Semester")
            tree_enroll = self._build_table(tab_enroll, columns)

            def load_enrollments():
                tree_enroll.delete(*tree_enroll.get_children())
                for row in get_all_enrollments():
                    tree_enroll.insert("", "end", values=(
                        row['enrollment_id'],
                        row['student_name'],
                        row['course_code'],
                        row['course_name'],
                        row['semester'],
                    ))

            load_enrollments()

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

    def show_analytics(self):
        def view():
            ttk.Label(self.content_frame, text="Attendance Analytics", style="PageTitle.TLabel").pack(pady=(24, 16))
            
            # Export Section
            export_frame = ttk.Frame(self.content_frame, style="Card.TFrame", padding=16)
            export_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            ttk.Label(export_frame, text="Data Export", style="CardHeader.TLabel").pack(side='left')
            
            def handle_export():
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    title="Save Attendance Report"
                )
                if not filepath:
                    return
                success, msg = export_attendance_to_csv(filepath)
                if success:
                    messagebox.showinfo("Export Successful", msg)
                else:
                    messagebox.showerror("Export Failed", msg)
            
            ttk.Button(export_frame, text="Export Full Attendance Report (CSV)", style="Accent.TButton", command=handle_export).pack(side='right')

            # Advanced SQL Reports Section
            notebook = ttk.Notebook(self.content_frame)
            notebook.pack(expand=True, fill='both', padx=16, pady=10)

            # Tab 1: Faculty Workload (Ranked)
            tab_workload = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_workload, text="Faculty Workload (Ranked)")
            cols_workload = ("Faculty ID", "First Name", "Last Name", "Total Sections", "Total Credits", "Weekly Hours", "Weekly Slots", "Workload Rank")
            tree_workload = self._build_table(tab_workload, cols_workload)
            for row in get_faculty_workload_report():
                tree_workload.insert(
                    "",
                    "end",
                    values=(
                        row['faculty_id'],
                        row['first_name'],
                        row['last_name'],
                        row['total_sections'],
                        row['total_credits'],
                        f"{row['weekly_teaching_hours']:.2f}",
                        row['weekly_class_slots'],
                        row['workload_rank'],
                    ),
                )

            # Tab 2: Semester Workload Summary
            tab_sem = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_sem, text="Workload by Semester")
            cols_sem = ("Faculty ID", "First Name", "Last Name", "Semester", "Year", "Sections", "Courses", "Weekly Hours", "Weekly Slots")
            tree_sem = self._build_table(tab_sem, cols_sem)
            for row in get_faculty_workload_semester_summary():
                tree_sem.insert(
                    "",
                    "end",
                    values=(
                        row['faculty_id'],
                        row['first_name'],
                        row['last_name'],
                        row['semester'],
                        row['academic_year'],
                        row['total_sections'],
                        row['total_courses'],
                        f"{row['weekly_teaching_hours']:.2f}",
                        row['weekly_class_slots'],
                    ),
                )

            # Tab 3: Monthly Sessions
            tab_month = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_month, text="Monthly Faculty Sessions")
            cols_month = ("Faculty ID", "Month Start", "Total Sessions", "Distinct Sections")
            tree_month = self._build_table(tab_month, cols_month)
            for row in get_faculty_monthly_sessions():
                tree_month.insert(
                    "",
                    "end",
                    values=(
                        row['faculty_id'],
                        row['month_start'],
                        row['total_sessions_created'],
                        row['distinct_sections'],
                    ),
                )

            # Tab 4: Department Rankings
            tab_dept = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_dept, text="Department Attendance Rankings")
            cols_dept = ("Department", "Course Code", "Course Name", "Total Records", "Present Count", "Percentage", "Rank in Dept")
            tree_dept = self._build_table(tab_dept, cols_dept)
            for row in get_department_ranking():
                tree_dept.insert("", "end", values=(row['dept_name'], row['course_code'], row['course_name'], row['total_attendance_records'], row['total_present'], f"{row['dept_course_attendance_percentage']:.2f}%", row['rank_in_dept']))

            # Tab 5: Student Attendance Trends
            tab_trends = ttk.Frame(notebook, style="Content.TFrame")
            notebook.add(tab_trends, text="Student Attendance Trends (LAG)")
            cols_trends = ("Student ID", "Section ID", "Session Date", "Current Status", "Previous Status")
            tree_trends = self._build_table(tab_trends, cols_trends)
            for row in get_student_trends():
                tree_trends.insert("", "end", values=(row['student_id'], row['section_id'], row['session_date'], row['status_name'], row['previous_status']))

        self.switch_view(view)

    def show_broadcast(self):
        def view():
            ttk.Label(self.content_frame, text="System Broadcast", style="PageTitle.TLabel").pack(pady=(24, 16))
            
            form = ttk.Frame(self.content_frame, style="Card.TFrame", padding=24)
            form.pack(fill='x', padx=20, pady=12)
            
            ttk.Label(form, text="Send an important notification to all users of a specific role.", style="CardBody.TLabel").pack(anchor='w', pady=(0, 16))
            
            ttk.Label(form, text="Target Audience", style="CardBody.TLabel").pack(anchor='w', pady=(0, 4))
            role_combo = ttk.Combobox(form, values=["All", "Student", "Faculty"], state='readonly', font=FONTS['body'])
            role_combo.pack(fill='x', pady=(0, 16))
            role_combo.set("All")
            
            ttk.Label(form, text="Message", style="CardBody.TLabel").pack(anchor='w', pady=(0, 4))
            message_text = tk.Text(form, height=6, font=FONTS['body'])
            message_text.pack(fill='x', pady=(0, 16))
            
            def send_broadcast():
                role = role_combo.get().strip()
                message = message_text.get("1.0", "end").strip()
                
                if not message:
                    messagebox.showerror("Validation Error", "Message cannot be empty.")
                    return
                
                if messagebox.askyesno("Confirm Broadcast", f"Are you sure you want to broadcast this to {role}?"):
                    if broadcast_notification(role, message):
                        messagebox.showinfo("Success", "Broadcast sent successfully!")
                        message_text.delete("1.0", "end")
                    else:
                        messagebox.showerror("Error", "Failed to send broadcast.")
            
            ttk.Button(form, text="Send Broadcast", style="Accent.TButton", command=send_broadcast).pack(anchor='e')

        self.switch_view(view)

    def show_archive(self):
        def view():
            ttk.Label(self.content_frame, text="Attendance Archive & Freeze", style="PageTitle.TLabel").pack(pady=(24, 16))

            control = ttk.Frame(self.content_frame, style="Card.TFrame", padding=16)
            control.pack(fill='x', padx=20, pady=(0, 16))

            ttk.Label(control, text="Semester", style="CardBody.TLabel").grid(row=0, column=0, sticky='w')
            semester_combo = ttk.Combobox(control, values=["Spring", "Summer", "Fall", "Winter"], state='readonly', font=FONTS['body'])
            semester_combo.grid(row=0, column=1, sticky='w', padx=(8, 24))
            semester_combo.set("Fall")

            ttk.Label(control, text="Academic Year", style="CardBody.TLabel").grid(row=0, column=2, sticky='w')
            year_entry = ttk.Entry(control, font=FONTS['body'])
            year_entry.grid(row=0, column=3, sticky='w', padx=(8, 24))
            year_entry.insert(0, "2026-2027")

            ttk.Label(control, text="Reason", style="CardBody.TLabel").grid(row=1, column=0, sticky='w', pady=(8, 0))
            reason_entry = ttk.Entry(control, font=FONTS['body'])
            reason_entry.grid(row=1, column=1, columnspan=3, sticky='ew', padx=(8, 0), pady=(8, 0))

            control.grid_columnconfigure(3, weight=1)

            def do_archive():
                sem = semester_combo.get().strip()
                year = year_entry.get().strip()
                reason = reason_entry.get().strip()
                if not sem or not year:
                    messagebox.showerror("Validation Error", "Semester and Academic Year are required.")
                    return
                if not messagebox.askyesno("Confirm Archive", f"Archive attendance for {sem} {year}?"):
                    return
                if archive_attendance_for_semester(sem, year, self.user_info['user_id'], reason):
                    messagebox.showinfo("Success", "Archive operation completed.")
                else:
                    messagebox.showerror("Error", "Failed to archive attendance. See server logs for details.")

            ttk.Button(control, text="Archive Attendance", style="Accent.TButton", command=do_archive)\
                .grid(row=0, column=4, rowspan=2, padx=(12, 0), sticky='e')

        self.switch_view(view)

    def show_firebase_sync(self):
        def view():
            ttk.Label(self.content_frame, text="Firebase Synchronization", style="PageTitle.TLabel").pack(pady=(24, 16))
            
            card = ttk.Frame(self.content_frame, style="Card.TFrame", padding=20)
            card.pack(fill='x', padx=20, pady=10)
            
            ttk.Label(card, text="PostgreSQL ↔ Firebase Sync", style="CardHeader.TLabel").pack(anchor='w', pady=(0, 10))
            ttk.Label(card, text="Use these tools to backup your entire PostgreSQL database to Firebase Firestore, or restore from Firestore to PostgreSQL. Note: Firebase must be properly configured.", style="CardBody.TLabel", wraplength=600).pack(anchor='w', pady=(0, 20))
            
            btn_frame = ttk.Frame(card, style="Card.TFrame")
            btn_frame.pack(fill='x')
            
            def do_backup():
                if messagebox.askyesno("Confirm Backup", "This will upload all PostgreSQL records to Firebase. Depending on database size, this may take a moment. Proceed?"):
                    try:
                        count = backup_postgres_to_firebase()
                        messagebox.showinfo("Backup Complete", f"Successfully synced {count} records to Firebase.")
                    except Exception as e:
                        messagebox.showerror("Backup Failed", f"An error occurred: {str(e)}")
                        
            def do_restore():
                if messagebox.askyesno("Confirm Restore", "This will download all records from Firebase and insert them into PostgreSQL (duplicates ignored). Proceed?"):
                    try:
                        count = restore_firebase_to_postgres()
                        messagebox.showinfo("Restore Complete", f"Successfully restored {count} records to PostgreSQL.")
                    except Exception as e:
                        messagebox.showerror("Restore Failed", f"An error occurred: {str(e)}")
            
            ttk.Button(btn_frame, text="Backup to Firebase", style="Accent.TButton", command=do_backup).pack(side='left', padx=(0, 10))
            ttk.Button(btn_frame, text="Restore from Firebase", command=do_restore).pack(side='left')

        self.switch_view(view)
