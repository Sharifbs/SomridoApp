import sqlite3
import os
import io
import time
import smtplib
import calendar
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

# Professional ReportLab document engineering engine
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PIL import Image as PILImage, ImageTk

# Premium App Theme Configurations
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# ==========================================
# CUSTOM COMPONENT: MODAL DATEPICKER
# ==========================================
class CTkDatePicker(ctk.CTkToplevel):
    def __init__(self, master, callback_target):
        super().__init__(master)
        self.title("Select Target Date")
        self.geometry("340x380")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.callback_target = callback_target
        self.now = datetime.now()
        self.current_year = self.now.year
        self.current_month = self.now.month

        self.months_pool = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"]

        hdr_frame = ctk.CTkFrame(self, fg_color="transparent")
        hdr_frame.pack(fill="x", padx=10, pady=10)

        self.btn_prev = ctk.CTkButton(hdr_frame, text="◀", width=35, command=self.go_prev_month)
        self.btn_prev.pack(side="left")

        self.lbl_month_year = ctk.CTkLabel(hdr_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_month_year.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(hdr_frame, text="▶", width=35, command=self.go_next_month)
        self.btn_next.pack(side="right")

        year_frame = ctk.CTkFrame(self, fg_color="transparent")
        year_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(year_frame, text="Jump to Year:", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)

        year_options = [str(y) for y in range(self.now.year + 2, self.now.year - 50, -1)]
        self.drop_year_select = ctk.CTkOptionMenu(year_frame, values=year_options, width=90, height=28,
                                                  command=self.jump_to_year_select)
        self.drop_year_select.set(str(self.current_year))
        self.drop_year_select.pack(side="left", padx=5)

        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.draw_calendar_matrix()

    def jump_to_year_select(self, chosen_year):
        self.current_year = int(chosen_year)
        self.draw_calendar_matrix()

    def draw_calendar_matrix(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.lbl_month_year.configure(text=f"{self.months_pool[self.current_month - 1]} {self.current_year}")
        self.drop_year_select.set(str(self.current_year))

        days_headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for idx, d_head in enumerate(days_headers):
            lbl = ctk.CTkLabel(self.grid_frame, text=d_head, font=ctk.CTkFont(size=11, weight="bold"),
                               text_color="gray")
            lbl.grid(row=0, column=idx, pady=2, sticky="nsew")

        month_matrix = calendar.monthcalendar(self.current_year, self.current_month)
        for r_idx, week in enumerate(month_matrix):
            for c_idx, day_val in enumerate(week):
                if day_val == 0:
                    continue
                btn_day = ctk.CTkButton(
                    self.grid_frame, text=str(day_val), width=32, height=32,
                    fg_color="#1e293b", hover_color="#10b981",
                    command=lambda d=day_val: self.commit_date_selection(d)
                )
                btn_day.grid(row=r_idx + 1, column=c_idx, padx=2, pady=2)

        for i in range(7):
            self.grid_frame.grid_columnconfigure(i, weight=1)

    def go_prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.draw_calendar_matrix()

    def go_next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.draw_calendar_matrix()

    def commit_date_selection(self, selected_day):
        picked_dt = datetime(self.current_year, self.current_month, selected_day)
        self.callback_target(picked_dt.strftime("%Y-%m-%d"))
        self.destroy()


# ==========================================
# MAIN ENTERPRISE SYSTEM
# ==========================================
class SomridoPremiumSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Somrido - Ultimate Premium Financial Suite")
        self.geometry("1450x900")
        self.minsize(1300, 850)

        # Application State Core Var Maps
        self.selected_img_bytes = None
        self.active_edit_member_id = None
        self.active_edit_income_id = None
        self.active_edit_expense_id = None

        # Default Email Server Alert Parameters
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "your-somrido-email@gmail.com"
        self.sender_password = "your-app-password"

        self.db_init()
        self.build_premium_layout()
        self.start_digital_clock()
        self.select_navigation_frame("dashboard")
        self.refresh_all_data()

    # ==========================================
    # DATA LAYER MIGRATIONS & SCHEMA
    # ==========================================
    def db_init(self):
        self.conn = sqlite3.connect("somrido_premium.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                father_husband_name TEXT,
                mother_name TEXT,
                gender TEXT,
                dob TEXT,
                phone TEXT,
                email TEXT DEFAULT '',
                nid TEXT,
                blood_group TEXT,
                nominee_name TEXT,
                nominee_relation TEXT,
                nominee_phone TEXT,
                admission_fee_paid REAL DEFAULT 0.0,
                profile_pic BLOB,
                status TEXT DEFAULT 'Active',
                present_address TEXT,
                permanent_address TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                member_id TEXT,
                type TEXT,
                amount REAL,
                method TEXT,
                paid_month TEXT, 
                reference TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount REAL,
                details TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_categories (
                category_name TEXT PRIMARY KEY
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                source_method TEXT,
                amount REAL,
                reference TEXT
            )
        """)

        migration_columns = [
            ("email", "TEXT DEFAULT ''"),
            ("present_address", "TEXT DEFAULT ''"),
            ("permanent_address", "TEXT DEFAULT ''")
        ]
        for col_name, col_type in migration_columns:
            try:
                self.cursor.execute(f"ALTER TABLE members ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass

        self.cursor.execute("SELECT COUNT(*) FROM expense_categories")
        if self.cursor.fetchone()[0] == 0:
            default_categories = ["Office Rent", "Utility Bill", "Salary Disbursement", "Misc Expense", "Entertainment"]
            for cat in default_categories:
                self.cursor.execute("INSERT OR IGNORE INTO expense_categories VALUES (?)", (cat,))

        self.conn.commit()

    def get_next_member_id(self):
        self.cursor.execute("SELECT member_id FROM members")
        ids = self.cursor.fetchall()
        if not ids: return "S01"
        max_num = 0
        for (m_id,) in ids:
            try:
                num = int(m_id[1:])
                if num > max_num: max_num = num
            except ValueError:
                continue
        return f"S0{max_num + 1}" if max_num + 1 < 10 else f"S{max_num + 1}"

    # ==========================================
    # PDF CREATION ENGINE METHODS
    # ==========================================
    def generate_profile_pdf(self, save_path, m_id):
        self.cursor.execute("SELECT * FROM members WHERE member_id = ?", (m_id,))
        m = self.cursor.fetchone()
        if not m: return

        doc = SimpleDocTemplate(save_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40,
                                bottomMargin=40)
        story = []

        primary_color = colors.HexColor("#0f172a")
        accent_color = colors.HexColor("#10b981")
        border_color = colors.HexColor("#e2e8f0")
        bg_light = colors.HexColor("#f8fafc")

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=24, textColor=primary_color,
                                     leading=28, spaceAfter=2)
        subtitle_style = ParagraphStyle('DocSub', fontName='Helvetica', fontSize=9,
                                        textColor=colors.HexColor("#64748b"), leading=12, spaceAfter=20)
        section_heading = ParagraphStyle('SectionHeading', fontName='Helvetica-Bold', fontSize=13,
                                         textColor=primary_color, spaceBefore=15, spaceAfter=8)

        lbl_style = ParagraphStyle('LabelStyle', fontName='Helvetica-Bold', fontSize=9,
                                   textColor=colors.HexColor("#334155"))
        txt_style = ParagraphStyle('TxtStyle', fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#0f172a"))

        story.append(Paragraph("SOMRIDO", title_style))
        story.append(Paragraph("OFFICIAL MEMBER BIOGRAPHICAL PROFILE DOSSIER", subtitle_style))

        photo_flowable = Paragraph("<font color='#64748b'>[ Photo Box ]</font>", txt_style)
        if m[14]:
            try:
                photo_flowable = RLImage(io.BytesIO(m[14]), width=95, height=105)
                photo_flowable.hAlign = 'RIGHT'
            except:
                pass

        card_content = [
            [
                [
                    Paragraph(f"<font size=13 color='#10b981'><b>{m[1]}</b></font>", txt_style), Spacer(1, 6),
                    Paragraph(f"<b>Member ID:</b> {m[0]}", txt_style), Spacer(1, 4),
                    Paragraph(f"<b>Account Status:</b> Active Operational Account", txt_style), Spacer(1, 4),
                    Paragraph(f"<b>Registered Mobile:</b> {m[6]}", txt_style)
                ],
                photo_flowable
            ]
        ]
        summary_table = Table(card_content, colWidths=[380, 140])
        summary_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), bg_light),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1.5, accent_color),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("Primary Demographics & Global Identifiers", section_heading))

        biographic_matrix = [
            [Paragraph("Father / Husband Name", lbl_style), Paragraph(str(m[2] or 'N/A'), txt_style),
             Paragraph("Mother's Legal Name", lbl_style), Paragraph(str(m[3] or 'N/A'), txt_style)],
            [Paragraph("Gender Identity", lbl_style), Paragraph(str(m[4] or 'N/A'), txt_style),
             Paragraph("Date of Birth", lbl_style), Paragraph(str(m[5] or 'N/A'), txt_style)],
            [Paragraph("National NID Card No", lbl_style), Paragraph(str(m[8] or 'N/A'), txt_style),
             Paragraph("Blood Group Matrix", lbl_style), Paragraph(str(m[9] or 'N/A'), txt_style)],
            [Paragraph("Primary Email Address", lbl_style), Paragraph(str(m[7] or 'N/A'), txt_style),
             Paragraph("Admission Ledger Paid", lbl_style), Paragraph(f"{m[13]:,.2f} Tk", txt_style)],
            [Paragraph("Present Address Location", lbl_style), Paragraph(str(m[16] or 'N/A'), txt_style),
             Paragraph("Permanent Address Location", lbl_style), Paragraph(str(m[17] or 'N/A'), txt_style)]
        ]

        bio_table = Table(biographic_matrix, colWidths=[130, 130, 130, 130])
        bio_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 7),
            ('BACKGROUND', (0, 0), (0, -1), bg_light),
            ('BACKGROUND', (2, 0), (2, -1), bg_light),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(bio_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("Capital Beneficiary & Nominee Allocation Block", section_heading))
        nom_matrix = [
            [Paragraph("Nominee Full Name", lbl_style), Paragraph(str(m[10] or 'N/A'), txt_style)],
            [Paragraph("Assigned Relationship", lbl_style), Paragraph(str(m[11] or 'N/A'), txt_style)],
            [Paragraph("Nominee Phone Number", lbl_style), Paragraph(str(m[12] or 'N/A'), txt_style)]
        ]
        nom_table = Table(nom_matrix, colWidths=[150, 370])
        nom_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('BACKGROUND', (0, 0), (0, -1), bg_light),
            ('PADDING', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(nom_table)

        doc.build(story)

    def generate_pdf_receipt(self, save_path, tx_id, date, member_id, inc_type, amount, method, paid_month, reference):
        self.cursor.execute("SELECT name FROM members WHERE member_id = ?", (member_id,))
        m_name = (self.cursor.fetchone() or ["Unknown"])[0]
        doc = SimpleDocTemplate(save_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40,
                                bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()
        t_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#10b981"),
                                 alignment=1)

        story.append(Paragraph("SOMRIDO RECEIPT", t_style))
        story.append(Spacer(1, 15))
        tx_data = [
            ["Receipt No:", f"#SR-{tx_id}", "Date Posted:", date],
            ["Member ID:", member_id, "Member Name:", m_name],
            ["Fund Category:", inc_type, "Billing Period:", paid_month],
            ["Amount Paid:", f"{amount:,.2f} Tk", "Payment Channel:", method],
            ["Reference Note:", reference if reference else "N/A", "", ""]
        ]
        t = Table(tx_data, colWidths=[110, 150, 110, 150])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#64748b")),
            ('PADDING', (0, 0), (-1, -1), 8)
        ]))
        story.append(t)
        doc.build(story)

    def generate_audit_sheet_pdf(self, save_path, member_id, from_date, to_date, records, total_amount):
        self.cursor.execute("SELECT name, phone, email FROM members WHERE member_id = ?", (member_id,))
        m_info = self.cursor.fetchone() or ("Unknown", "N/A", "N/A")

        doc = SimpleDocTemplate(save_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40,
                                bottomMargin=40)
        story = []

        primary_color = colors.HexColor("#0f172a")
        border_color = colors.HexColor("#cbd5e1")
        bg_light = colors.HexColor("#f8fafc")

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('AuditTitle', fontName='Helvetica-Bold', fontSize=22, textColor=primary_color,
                                     leading=26)
        sub_style = ParagraphStyle('AuditSub', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#475569"),
                                   leading=14)
        lbl_style = ParagraphStyle('AuditLbl', fontName='Helvetica-Bold', fontSize=9, textColor=primary_color)
        txt_style = ParagraphStyle('AuditTxt', fontName='Helvetica', fontSize=9, textColor=primary_color)
        hdr_txt_style = ParagraphStyle('AuditHdr', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)

        story.append(Paragraph("SOMRIDO FINANCIAL AUDIT STATEMENT", title_style))
        story.append(
            Paragraph(f"Generated Chronological Statement Window: <b>{from_date}</b> to <b>{to_date}</b>", sub_style))
        story.append(Spacer(1, 15))

        meta_matrix = [
            [Paragraph("Member Reference ID", lbl_style), Paragraph(member_id, txt_style),
             Paragraph("Full Name Associated", lbl_style), Paragraph(m_info[0], txt_style)],
            [Paragraph("Mobile Connection", lbl_style), Paragraph(m_info[1], txt_style),
             Paragraph("Registered Email", lbl_style), Paragraph(m_info[2], txt_style)]
        ]
        meta_table = Table(meta_matrix, colWidths=[120, 140, 120, 140])
        meta_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('BACKGROUND', (0, 0), (0, -1), bg_light),
            ('BACKGROUND', (2, 0), (2, -1), bg_light),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        grid_data = [[
            Paragraph("TX ID", hdr_txt_style),
            Paragraph("POSTING DATE", hdr_txt_style),
            Paragraph("CATEGORY HEAD", hdr_txt_style),
            Paragraph("CHANNEL", hdr_txt_style),
            Paragraph("REFERENCE MEMO", hdr_txt_style),
            Paragraph("AMOUNT", hdr_txt_style)
        ]]

        for r in records:
            grid_data.append([
                Paragraph(f"#SR-{r[0]}", txt_style),
                Paragraph(str(r[1]), txt_style),
                Paragraph(str(r[2]), txt_style),
                Paragraph(str(r[4]), txt_style),
                Paragraph(str(r[5] or 'N/A'), txt_style),
                Paragraph(f"{r[3]:,.2f} Tk", txt_style)
            ])

        grid_data.append([
            Paragraph("<b>TOTAL BALANCED AGGREGATED IN SHEET</b>", lbl_style), "", "", "", "",
            Paragraph(f"<b>{total_amount:,.2f} Tk</b>", lbl_style)
        ])

        grid_table = Table(grid_data, colWidths=[65, 80, 100, 70, 115, 90])
        grid_style = [
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -2), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, -1), (4, -1)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f1f5f9")),
            ('BOX', (0, -1), (-1, -1), 1, primary_color)
        ]

        grid_table.setStyle(TableStyle(grid_style))
        story.append(grid_table)

        doc.build(story)

    def generate_global_report_pdf(self, save_path, title_text, from_date, to_date, headers, records, total_val=None):
        doc = SimpleDocTemplate(save_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40,
                                bottomMargin=40)
        story = []
        primary_color = colors.HexColor("#0f172a")
        border_color = colors.HexColor("#cbd5e1")

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('RepTitle', fontName='Helvetica-Bold', fontSize=20, textColor=primary_color,
                                     leading=24)
        sub_style = ParagraphStyle('RepSub', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#475569"),
                                   leading=14)
        txt_style = ParagraphStyle('RepTxt', fontName='Helvetica', fontSize=9, textColor=primary_color)
        hdr_txt_style = ParagraphStyle('RepHdr', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)

        story.append(Paragraph(title_text.upper(), title_style))
        story.append(Paragraph(f"Report Window Interval: <b>{from_date}</b> to <b>{to_date}</b>", sub_style))
        story.append(Spacer(1, 15))

        grid_data = [[Paragraph(h, hdr_txt_style) for h in headers]]
        for r in records:
            grid_data.append([Paragraph(str(val), txt_style) for val in r])

        if total_val is not None:
            span_count = max(1, len(headers) - 1)
            row = [Paragraph("<b>AGGREGATED TOTAL IN REPORT</b>", txt_style)]
            for _ in range(span_count - 1): row.append("")
            row.append(Paragraph(f"<b>{total_val:,.2f} Tk</b>", txt_style))
            grid_data.append(row)

        col_width = 530.0 / len(headers)
        col_widths = [col_width] * len(headers)

        table = Table(grid_data, colWidths=col_widths)
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1 if total_val is None else -2), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]
        if total_val is not None:
            t_style.append(('SPAN', (0, -1), (span_count - 1, -1)))
            t_style.append(('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f1f5f9")))
            t_style.append(('BOX', (0, -1), (-1, -1), 1, primary_color))

        table.setStyle(TableStyle(t_style))
        story.append(table)
        doc.build(story)

    # ==========================================
    # ENGINE RUNTIME UI GENERATOR
    # ==========================================
    def build_premium_layout(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#0f172a")
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.brand_lbl = ctk.CTkLabel(self.sidebar_frame, text="SOMRIDO\nFINANCIAL HUB",
                                      font=ctk.CTkFont(size=18, weight="bold"), text_color="#10b981")
        self.brand_lbl.pack(pady=(20, 5), padx=20)

        self.lbl_digital_clock = ctk.CTkLabel(self.sidebar_frame, text="00:00:00 AM",
                                              font=ctk.CTkFont(family="Courier", size=16, weight="bold"),
                                              text_color="#f59e0b")
        self.lbl_digital_clock.pack(pady=(0, 20))

        nav_items = [
            ("Dashboard View", "dashboard"),
            ("Member Profile Form", "members"),
            ("Collection Ledger", "accounts"),
            ("Overdue Subscription", "dues"),
            ("Individual Audits", "summary"),
            ("Expense Registry", "expenses"),
            ("Clearing Transfers", "transfer"),
            ("Reports Center", "reports")
        ]

        self.nav_buttons = {}
        for text, key in nav_items:
            btn = ctk.CTkButton(self.sidebar_frame, text=text, fg_color="transparent", text_color="gray90",
                                hover_color="#1e293b", anchor="w", height=42,
                                command=lambda k=key: self.select_navigation_frame(k))
            btn.pack(fill="x", padx=15, pady=2)
            self.nav_buttons[key] = btn

        self.main_container = ctk.CTkFrame(self, fg_color="#020617")
        self.main_container.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        self.frames = {
            "dashboard": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "members": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "accounts": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "dues": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "summary": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "transfer": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "expenses": ctk.CTkFrame(self.main_container, fg_color="transparent"),
            "reports": ctk.CTkFrame(self.main_container, fg_color="transparent")
        }
        self.configure_sub_modules()

    def start_digital_clock(self):
        def clock_loop():
            while True:
                time_str = datetime.now().strftime("%I:%M:%S %p")
                try:
                    self.lbl_digital_clock.configure(text=time_str)
                except:
                    break
                time.sleep(1)

        threading.Thread(target=clock_loop, daemon=True).start()

    def select_navigation_frame(self, target):
        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color="#10b981" if key == target else "transparent")
        for f in self.frames.values(): f.pack_forget()
        self.frames[target].pack(fill="both", expand=True, padx=20, pady=20)

        if target == "dues":
            self.calculate_and_render_dues_grid()
        elif target == "summary":
            self.trigger_member_audit(self.drop_summary_mid.get())
        elif target == "dashboard" or target == "reports":
            self.refresh_all_data()

    def configure_sub_modules(self):
        self.init_dashboard_view()
        self.init_members_view()
        self.init_accounts_view()
        self.init_dues_view()
        self.init_summary_view()
        self.init_transfer_view()
        self.init_expenses_view()
        self.init_reports_view()

    # ==========================================
    # DASHBOARD ENGINE (FIXED BORDER LOGIC HERE)
    # ==========================================
    def init_dashboard_view(self):
        lbl = ctk.CTkLabel(self.frames["dashboard"], text="Treasury Balance Matrix Monitoring",
                           font=ctk.CTkFont(size=22, weight="bold"))
        lbl.pack(anchor="w", pady=(10, 25))

        g = ctk.CTkFrame(self.frames["dashboard"], fg_color="transparent")
        g.pack(fill="x", pady=10)

        self.card_cash = ctk.CTkLabel(g, text="Cash Balance\n0.00 Tk", font=ctk.CTkFont(size=14, weight="bold"),
                                      height=90, width=210, fg_color="#1e293b", text_color="#f97316", corner_radius=10)
        self.card_cash.grid(row=0, column=0, padx=8, pady=10)
        self.card_bkash = ctk.CTkLabel(g, text="bKash Balance\n0.00 Tk", font=ctk.CTkFont(size=14, weight="bold"),
                                       height=90, width=210, fg_color="#1e293b", text_color="#ec4899", corner_radius=10)
        self.card_bkash.grid(row=0, column=1, padx=8, pady=10)
        self.card_bank = ctk.CTkLabel(g, text="Bank Balance\n0.00 Tk", font=ctk.CTkFont(size=14, weight="bold"),
                                      height=90, width=210, fg_color="#1e293b", text_color="#3b82f6", corner_radius=10)
        self.card_bank.grid(row=0, column=2, padx=8, pady=10)
        self.card_expense = ctk.CTkLabel(g, text="Total Expenses\n0.00 Tk", font=ctk.CTkFont(size=14, weight="bold"),
                                         height=90, width=210, fg_color="#1e293b", text_color="#ef4444",
                                         corner_radius=10)
        self.card_expense.grid(row=0, column=3, padx=8, pady=10)

        # FIX: Nested within CTkFrame containers to display custom tracking borders safely
        frame_total_coll = ctk.CTkFrame(g, height=90, fg_color="#0f172a", border_width=2, border_color="#10b981",
                                        corner_radius=10)
        frame_total_coll.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=10)
        frame_total_coll.grid_propagate(False)

        self.card_total_collection = ctk.CTkLabel(frame_total_coll, text="Total Fund Collection\n0.00 Tk",
                                                  font=ctk.CTkFont(size=14, weight="bold"), text_color="#10b981")
        self.card_total_collection.pack(fill="both", expand=True)

        frame_june_coll = ctk.CTkFrame(g, height=90, fg_color="#0f172a", border_width=2, border_color="#06b6d4",
                                       corner_radius=10)
        frame_june_coll.grid(row=1, column=2, columnspan=2, sticky="ew", padx=8, pady=10)
        frame_june_coll.grid_propagate(False)

        self.card_june_collection = ctk.CTkLabel(frame_june_coll, text="Fund Collection of June'26\n0.00 Tk",
                                                 font=ctk.CTkFont(size=14, weight="bold"), text_color="#06b6d4")
        self.card_june_collection.pack(fill="both", expand=True)

        self.card_balance = ctk.CTkLabel(self.frames["dashboard"], text="Net Liquid Capital\n0.00 Tk",
                                         font=ctk.CTkFont(size=18, weight="bold"), height=110, width=380,
                                         fg_color="#10b981", text_color="white", corner_radius=12)
        self.card_balance.pack(pady=30)

    # ==========================================
    # MEMBERS PROFILE FORMS ENGINE
    # ==========================================
    def init_members_view(self):
        form_scroll = ctk.CTkScrollableFrame(self.frames["members"], width=490, fg_color="#0f172a")
        form_scroll.pack(side="left", fill="y", padx=(0, 15))

        self.lbl_member_form_title = ctk.CTkLabel(form_scroll, text="Enroll New Profile Dossier",
                                                  font=ctk.CTkFont(size=16, weight="bold"), text_color="#10b981")
        self.lbl_member_form_title.pack(pady=10)
        self.lbl_next_id = ctk.CTkLabel(form_scroll, text="Member ID: Generating...", font=ctk.CTkFont(weight="bold"))
        self.lbl_next_id.pack(pady=5)

        self.img_canvas = ctk.CTkLabel(form_scroll, text="[ Photo Box\nPNG, JPG, JPEG ]", width=110, height=120,
                                       fg_color="#1e293b", corner_radius=8)
        self.img_canvas.pack(pady=10)
        ctk.CTkButton(form_scroll, text="Upload Profile Photo", height=28, fg_color="#334155", hover_color="#475569",
                      command=self.browse_profile_image).pack(pady=(0, 15))

        self.ent_m_name = self.create_form_input(form_scroll, "Member Full Name *")
        self.ent_m_father = self.create_form_input(form_scroll, "Father's / Husband's Full Name")
        self.ent_m_mother = self.create_form_input(form_scroll, "Mother's Full Name")

        ctk.CTkLabel(form_scroll, text="Gender Identity Grouping:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=25,
                                                                                                    pady=(4, 0))
        self.drop_m_gender = ctk.CTkOptionMenu(form_scroll, values=["Male", "Female", "Other"], height=35,
                                               fg_color="#1e293b")
        self.drop_m_gender.pack(fill="x", padx=25, pady=4)

        ctk.CTkLabel(form_scroll, text="Date of Birth (YYYY-MM-DD):", font=ctk.CTkFont(size=11)).pack(anchor="w",
                                                                                                      padx=25,
                                                                                                      pady=(4, 0))
        dob_layout_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        dob_layout_frame.pack(fill="x", padx=25, pady=4)

        self.ent_m_dob = ctk.CTkEntry(dob_layout_frame, height=35, placeholder_text="YYYY-MM-DD", fg_color="#1e293b",
                                      border_color="#334155")
        self.ent_m_dob.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_dob_cal = ctk.CTkButton(dob_layout_frame, text="📅", width=40, height=35, fg_color="#334155",
                                    command=lambda: CTkDatePicker(self, self.set_member_dob_field))
        btn_dob_cal.pack(side="right")

        self.ent_m_phone = self.create_form_input(form_scroll, "Mobile Connection Number *")
        self.ent_m_email = self.create_form_input(form_scroll, "Communication Email *")
        self.ent_m_nid = self.create_form_input(form_scroll, "National ID (NID) Card Number")
        self.ent_m_blood = self.create_form_input(form_scroll, "Blood Group Type")

        self.ent_m_present_addr = self.create_form_input(form_scroll, "Present Address Line")
        self.ent_m_perm_addr = self.create_form_input(form_scroll, "Permanent Address Line")

        self.ent_m_adm = self.create_form_input(form_scroll, "Admission Initial Capital Paid (Tk)")
        self.ent_m_adm.insert(0, "2000")

        ctk.CTkLabel(form_scroll, text="Capital Beneficiary Nominee Block", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#3b82f6").pack(pady=(15, 5))
        self.ent_nom_name = self.create_form_input(form_scroll, "Nominee Full Name")
        self.ent_nom_relation = self.create_form_input(form_scroll, "Relationship to Primary Member")
        self.ent_nom_phone = self.create_form_input(form_scroll, "Nominee Contact Mobile Num")

        self.btn_member_save = ctk.CTkButton(form_scroll, text="Save Member Enterprise Profile",
                                             font=ctk.CTkFont(weight="bold"), height=42, fg_color="#10b981",
                                             hover_color="#059669", command=self.save_member_profile)
        self.btn_member_save.pack(fill="x", padx=25, pady=15)

        self.btn_member_cancel = ctk.CTkButton(form_scroll, text="Cancel Changes", font=ctk.CTkFont(weight="bold"),
                                               height=35, fg_color="#ef4444", hover_color="#dc2626",
                                               command=self.reset_member_form_state)

        list_frame = ctk.CTkFrame(self.frames["members"], fg_color="transparent")
        list_frame.pack(side="right", fill="both", expand=True)

        ctrl_bar = ctk.CTkFrame(list_frame, height=50, fg_color="transparent")
        ctrl_bar.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(ctrl_bar, text="⬇ Download Premium Profile PDF", font=ctk.CTkFont(weight="bold"),
                      fg_color="#3b82f6", hover_color="#2563eb", command=self.download_selected_profile_pdf).pack(
            side="left", padx=5)
        ctk.CTkButton(ctrl_bar, text="✏️ Edit Selection Entry", font=ctk.CTkFont(weight="bold"), fg_color="#f59e0b",
                      hover_color="#d97706", command=self.load_member_to_edit).pack(side="left", padx=5)

        columns = ("member_id", "name", "phone", "email", "nid", "status")
        self.tree_members = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.apply_treeview_styles(self.tree_members, columns)
        self.tree_members.pack(fill="both", expand=True, padx=10, pady=10)

    def set_member_dob_field(self, date_string):
        self.ent_m_dob.delete(0, 'end')
        self.ent_m_dob.insert(0, date_string)

    # ==========================================
    # ACCOUNTS INFLOW COLLECTOR ENGINE
    # ==========================================
    def init_accounts_view(self):
        form_frame = ctk.CTkFrame(self.frames["accounts"], width=340, fg_color="#0f172a")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        self.lbl_income_form_title = ctk.CTkLabel(form_frame, text="Log Incoming Transactions",
                                                  font=ctk.CTkFont(size=15, weight="bold"), text_color="#10b981")
        self.lbl_income_form_title.pack(pady=15)

        ctk.CTkLabel(form_frame, text="Target Member ID Reference:", font=ctk.CTkFont(size=11)).pack(anchor="w",
                                                                                                     padx=20)
        self.drop_acc_mid = ctk.CTkOptionMenu(form_frame, values=["No Members Registered"], height=35,
                                              fg_color="#1e293b")
        self.drop_acc_mid.pack(fill="x", padx=20, pady=5)

        self.drop_acc_type = ctk.CTkOptionMenu(form_frame, values=["Subscription", "Donation"], height=35,
                                               fg_color="#1e293b")
        self.drop_acc_type.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(form_frame, text="Select Targeted Accounting Date:", font=ctk.CTkFont(size=11)).pack(anchor="w",
                                                                                                          padx=20)
        date_sel_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_sel_frame.pack(fill="x", padx=20, pady=5)
        self.ent_acc_date = ctk.CTkEntry(date_sel_frame, height=35, placeholder_text="YYYY-MM-DD")
        self.ent_acc_date.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.ent_acc_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        btn_cal = ctk.CTkButton(date_sel_frame, text="📅", width=40, height=35, fg_color="#334155",
                                command=lambda: CTkDatePicker(self, self.set_income_date_field))
        btn_cal.pack(side="right")

        self.ent_acc_amount = ctk.CTkEntry(form_frame, placeholder_text="Amount Received (Tk)", height=35)
        self.ent_acc_amount.pack(fill="x", padx=20, pady=8)
        self.drop_acc_method = ctk.CTkOptionMenu(form_frame, values=["Cash", "bKash", "Bank"], height=35,
                                                 fg_color="#1e293b")
        self.drop_acc_method.pack(fill="x", padx=20, pady=8)
        self.ent_acc_ref = ctk.CTkEntry(form_frame, placeholder_text="Memos / Trans IDs Reference", height=35)
        self.ent_acc_ref.pack(fill="x", padx=20, pady=8)

        self.btn_income_save = ctk.CTkButton(form_frame, text="Post Receipt Entry", font=ctk.CTkFont(weight="bold"),
                                             fg_color="#10b981", hover_color="#059669", height=42,
                                             command=self.save_income_record)
        self.btn_income_save.pack(fill="x", padx=20, pady=15)

        self.btn_income_cancel = ctk.CTkButton(form_frame, text="Cancel Modifications", fg_color="#ef4444",
                                               hover_color="#dc2626", height=35, command=self.reset_income_form_state)

        ledger_frame = ctk.CTkFrame(self.frames["accounts"], fg_color="transparent")
        ledger_frame.pack(side="right", fill="both", expand=True)

        ctrl_bar_inc = ctk.CTkFrame(ledger_frame, height=45, fg_color="transparent")
        ctrl_bar_inc.pack(fill="x", pady=5)
        ctk.CTkButton(ctrl_bar_inc, text="✏️ Edit Selected Ledger Record", font=ctk.CTkFont(weight="bold"),
                      fg_color="#f59e0b", hover_color="#d97706", command=self.load_income_to_edit).pack(side="left",
                                                                                                        padx=5)
        ctk.CTkButton(ctrl_bar_inc, text="⬇️ Invoice Download", font=ctk.CTkFont(weight="bold"), fg_color="#10b981",
                      hover_color="#059669", command=self.download_historical_receipt_invoice).pack(side="left", padx=5)

        self.lbl_acc_summary = ctk.CTkLabel(ledger_frame, text="Calculating balances...",
                                            font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_acc_summary.pack(pady=5)

        columns = ("id", "date", "member_id", "type", "amount", "method", "ref")
        self.tree_income = ttk.Treeview(ledger_frame, columns=columns, show="headings")
        self.apply_treeview_styles(self.tree_income, columns)
        self.tree_income.pack(fill="both", expand=True, padx=10, pady=10)

    def set_income_date_field(self, date_string):
        self.ent_acc_date.delete(0, 'end')
        self.ent_acc_date.insert(0, date_string)

    def download_historical_receipt_invoice(self):
        selection = self.tree_income.selection()
        if not selection:
            messagebox.showerror("Selection Error",
                                 "Please highlight/select an absolute transaction row from the grid list first.")
            return

        inc_id = self.tree_income.item(selection[0])['values'][0]
        self.cursor.execute("SELECT * FROM income WHERE id = ?", (inc_id,))
        row = self.cursor.fetchone()

        if row:
            tx_id, date, member_id, inc_type, amt, method, paid_month, ref = row
            safe_month = paid_month.replace("'", "_")
            file_path = filedialog.asksaveasfilename(initialfile=f"Historical_Receipt_{member_id}_{safe_month}.pdf",
                                                     defaultextension=".pdf")
            if not file_path: return
            self.generate_pdf_receipt(file_path, tx_id, date, member_id, inc_type, amt, method, paid_month, ref)
            messagebox.showinfo("Export Successful",
                                f"Invoice Transaction Receipt successfully compiled for ID Row #{tx_id}.")

    # ==========================================
    # SUBSCRIPTION DUE MONITOR & ALERT AUTOMATION
    # ==========================================
    def init_dues_view(self):
        hdr_bar = ctk.CTkFrame(self.frames["dues"], fg_color="#0f172a", height=60)
        hdr_bar.pack(fill="x", pady=(0, 10))

        title_lbl = ctk.CTkLabel(hdr_bar, text="Monthly Subscription Overdue Matrix",
                                 font=ctk.CTkFont(size=16, weight="bold"), text_color="#ef4444")
        title_lbl.pack(side="left", padx=15, pady=10)

        btn_send_all = ctk.CTkButton(hdr_bar, text="✉ Dispatch Overdue Emails", font=ctk.CTkFont(weight="bold"),
                                     fg_color="#ef4444", hover_color="#b91c1c", command=self.dispatch_bulk_due_alerts)
        btn_send_all.pack(side="right", padx=10)

        btn_config_mail = ctk.CTkButton(hdr_bar, text="⚙ SMTP Mail Config", fg_color="#334155",
                                        command=self.popup_smtp_config_panel)
        btn_config_mail.pack(side="right", padx=5)

        columns = ("member_id", "name", "phone", "email", "status", "due_status")
        self.tree_dues = ttk.Treeview(self.frames["dues"], columns=columns, show="headings")
        self.apply_treeview_styles(self.tree_dues, columns)
        self.tree_dues.pack(fill="both", expand=True, padx=5, pady=5)

    def popup_smtp_config_panel(self):
        panel = ctk.CTkToplevel(self)
        panel.title("SMTP Premium Configuration Parameters")
        panel.geometry("450x400")
        panel.resizable(False, False)
        panel.transient(self)
        panel.grab_set()

        ctk.CTkLabel(panel, text="SMTP Routing Credentials Server Configuration",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)

        ent_serv = ctk.CTkEntry(panel, placeholder_text="SMTP Server (e.g. smtp.gmail.com)", width=320)
        ent_serv.insert(0, self.smtp_server);
        ent_serv.pack(pady=6)

        ent_port = ctk.CTkEntry(panel, placeholder_text="Port (e.g. 587)", width=320)
        ent_port.insert(0, str(self.smtp_port));
        ent_port.pack(pady=6)

        ent_user = ctk.CTkEntry(panel, placeholder_text="Sender Email Address Account", width=320)
        ent_user.insert(0, self.sender_email);
        ent_user.pack(pady=6)

        ent_pass = ctk.CTkEntry(panel, placeholder_text="Google App Password Token String", show="*", width=320)
        ent_pass.insert(0, self.sender_password);
        ent_pass.pack(pady=6)

        def save_conf():
            self.smtp_server = ent_serv.get().strip()
            self.smtp_port = int(ent_port.get().strip() or 587)
            self.sender_email = ent_user.get().strip()
            self.sender_password = ent_pass.get().strip()
            messagebox.showinfo("Saved", "Local System Credentials Updated Successfully.")
            panel.destroy()

        ctk.CTkButton(panel, text="Commit Settings", fg_color="#10b981", command=save_conf).pack(pady=20)

    def calculate_and_render_dues_grid(self):
        for row in self.tree_dues.get_children():
            self.tree_dues.delete(row)

        now = datetime.now()
        current_month_token = f"{now.strftime('%B')}'_{now.strftime('%y')}"

        self.cursor.execute("SELECT member_id, name, phone, email, status FROM members WHERE status='Active'")
        active_members = self.cursor.fetchall()

        for m in active_members:
            m_id = m[0]
            self.cursor.execute(
                "SELECT COUNT(*) FROM income WHERE member_id=? AND type='Subscription' AND paid_month=?",
                (m_id, current_month_token))
            has_paid = self.cursor.fetchone()[0]

            if has_paid == 0:
                if now.day >= 15:
                    due_label = "🚨 CRITICAL OVERDUE (Past 15th)"
                else:
                    due_label = "⚠️ PENDING PAYMENT"
                self.tree_dues.insert("", "end", values=(m[0], m[1], m[2], m[3], m[4], due_label))

    def dispatch_bulk_due_alerts(self):
        records = self.tree_dues.get_children()
        if not records:
            messagebox.showinfo("Clear Ledger", "No Accounts are currently overdue for subscription payments.")
            return

        if datetime.now().day < 15:
            ans = messagebox.askyesno("Early Alert Notice",
                                      "It is currently before the 15th of the month. Do you still wish to dispatch custom notifications manually?")
            if not ans: return

        def async_mailer():
            success_count = 0;
            failed_count = 0
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("SMTP Fail", f"Authentication handshake failed: {e}"))
                return

            current_month_name = datetime.now().strftime("%B %Y")
            for r in records:
                vals = self.tree_dues.item(r)['values']
                m_name = vals[1];
                m_email = vals[3]
                if not m_email or "@" not in str(m_email):
                    failed_count += 1;
                    continue

                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = str(m_email)
                msg['Subject'] = f"URGENT: Somrido Subscription Alert - {current_month_name}"

                body = f"Dear {m_name},\n\nOur database records indicate that your profile has an outstanding subscription fee due for {current_month_name}.\n\nPlease clear your pending dues to maintain active operational status.\n\nRegards,\nSomrido Systems"
                msg.attach(MIMEText(body, 'plain'))
                try:
                    server.send_message(msg)
                    success_count += 1
                except:
                    failed_count += 1

            server.quit()
            self.after(0, lambda: messagebox.showinfo("Alert Dispatch Complete",
                                                      f"Broadcast Finalized.\nSuccessfully Sent: {success_count}\nFailed/Invalid: {failed_count}"))
            self.after(0, self.calculate_and_render_dues_grid)

        threading.Thread(target=async_mailer, daemon=True).start()

    # ==========================================
    # EXPENSES MODULE
    # ==========================================
    def init_expenses_view(self):
        form_frame = ctk.CTkFrame(self.frames["expenses"], width=340, fg_color="#0f172a")
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        self.lbl_expense_form_title = ctk.CTkLabel(form_frame, text="Log Expenditure Outflows",
                                                   font=ctk.CTkFont(size=14, weight="bold"), text_color="#10b981")
        self.lbl_expense_form_title.pack(pady=20)

        ctk.CTkLabel(form_frame, text="Expense Category Allocation Head:", font=ctk.CTkFont(size=11)).pack(anchor="w",
                                                                                                           padx=20)

        cat_selection_block = ctk.CTkFrame(form_frame, fg_color="transparent")
        cat_selection_block.pack(fill="x", padx=20, pady=5)
        self.drop_exp_cat = ctk.CTkOptionMenu(cat_selection_block, values=["Misc Expense"], height=35,
                                              fg_color="#1e293b")
        self.drop_exp_cat.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_add_head = ctk.CTkButton(cat_selection_block, text="+", width=35, height=35,
                                     font=ctk.CTkFont(size=16, weight="bold"), fg_color="#3b82f6",
                                     hover_color="#2563eb", command=self.popup_create_expense_head)
        btn_add_head.pack(side="right")

        self.ent_exp_amount = ctk.CTkEntry(form_frame, placeholder_text="Disbursement Amount (Tk)", height=35)
        self.ent_exp_amount.pack(fill="x", padx=20, pady=10)
        self.ent_exp_details = ctk.CTkEntry(form_frame, placeholder_text="Itemized Allocation Memos", height=35)
        self.ent_exp_details.pack(fill="x", padx=20, pady=10)

        self.btn_expense_save = ctk.CTkButton(form_frame, text="Log Expense Outflow", font=ctk.CTkFont(weight="bold"),
                                              height=40, fg_color="#10b981", command=self.save_expense_record)
        self.btn_expense_save.pack(fill="x", padx=20, pady=20)

        self.btn_expense_cancel = ctk.CTkButton(form_frame, text="Cancel Execution", fg_color="#ef4444",
                                                hover_color="#dc2626", height=35, command=self.reset_expense_form_state)

        list_frame = ctk.CTkFrame(self.frames["expenses"], fg_color="transparent")
        list_frame.pack(side="right", fill="both", expand=True)

        ctrl_bar_exp = ctk.CTkFrame(list_frame, height=45, fg_color="transparent")
        ctrl_bar_exp.pack(fill="x", pady=5)
        ctk.CTkButton(ctrl_bar_exp, text="✏️ Edit Selected", font=ctk.CTkFont(weight="bold"), fg_color="#f59e0b",
                      hover_color="#d97706", command=self.load_expense_to_edit).pack(side="left", padx=5)

        ctk.CTkLabel(ctrl_bar_exp, text="From:").pack(side="left", padx=2)
        self.ent_exp_filter_from = ctk.CTkEntry(ctrl_bar_exp, width=95, height=28)
        self.ent_exp_filter_from.insert(0, "2026-01-01");
        self.ent_exp_filter_from.pack(side="left", padx=2)
        ctk.CTkButton(ctrl_bar_exp, text="📅", width=25, height=28, fg_color="#334155",
                      command=lambda: CTkDatePicker(self, lambda s: (self.ent_exp_filter_from.delete(0, 'end'),
                                                                     self.ent_exp_filter_from.insert(0, s)))).pack(
            side="left", padx=(0, 5))

        ctk.CTkLabel(ctrl_bar_exp, text="To:").pack(side="left", padx=2)
        self.ent_exp_filter_to = ctk.CTkEntry(ctrl_bar_exp, width=95, height=28)
        self.ent_exp_filter_to.insert(0, datetime.now().strftime("%Y-%m-%d"));
        self.ent_exp_filter_to.pack(side="left", padx=2)
        ctk.CTkButton(ctrl_bar_exp, text="📅", width=25, height=28, fg_color="#334155",
                      command=lambda: CTkDatePicker(self, lambda s: (self.ent_exp_filter_to.delete(0, 'end'),
                                                                     self.ent_exp_filter_to.insert(0, s)))).pack(
            side="left", padx=(0, 5))

        ctk.CTkButton(ctrl_bar_exp, text="⬇️ Expense PDF View", font=ctk.CTkFont(weight="bold"), fg_color="#10b981",
                      hover_color="#059669", command=self.download_expense_range_pdf).pack(side="left", padx=5)

        columns = ("id", "date", "category", "amount", "details")
        self.tree_expenses = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.apply_treeview_styles(self.tree_expenses, columns)
        self.tree_expenses.pack(fill="both", expand=True, padx=10, pady=10)

    def popup_create_expense_head(self):
        dialog = ctk.CTkInputDialog(text="Enter New Operational Expense Category Name:", title="Add Category Head")
        input_val = dialog.get_input()
        if input_val and input_val.strip():
            cleaned_cat = input_val.strip()
            try:
                self.cursor.execute("INSERT INTO expense_categories VALUES (?)", (cleaned_cat,))
                self.conn.commit()
                self.refresh_expense_categories_dropdown()
                self.drop_exp_cat.set(cleaned_cat)
                messagebox.showinfo("Success", f"Category head '{cleaned_cat}' appended and archived permanently.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Category Head definition already active inside archived tables.")

    def refresh_expense_categories_dropdown(self):
        self.cursor.execute("SELECT category_name FROM expense_categories")
        cats = [r[0] for r in self.cursor.fetchall()]
        if cats: self.drop_exp_cat.configure(values=cats)

    def download_expense_range_pdf(self):
        f_date = self.ent_exp_filter_from.get().strip()
        t_date = self.ent_exp_filter_to.get().strip()

        self.cursor.execute(
            "SELECT date, category, details, amount FROM expenses WHERE date >= ? AND date <= ? ORDER BY date ASC",
            (f_date, t_date))
        records = self.cursor.fetchall()
        total_val = sum(r[3] for r in records)

        file_path = filedialog.asksaveasfilename(initialfile=f"Expense_Statement_{f_date}_to_{t_date}.pdf",
                                                 defaultextension=".pdf")
        if file_path:
            self.generate_global_report_pdf(file_path, "Itemized Expense Range Outflow Statement", f_date, t_date,
                                            ["DATE POSTED", "CATEGORY HEAD", "MEMO ALLOCATION DETAILS", "AMOUNT (TK)"],
                                            records, total_val)
            messagebox.showinfo("Exported", "Expense breakdown PDF compiled successfully.")

    # ==========================================
    # INDIVIDUAL MEMBER AUDIT MATRIX VIEW
    # ==========================================
    def init_summary_view(self):
        top_bar = ctk.CTkFrame(self.frames["summary"], height=95, fg_color="#0f172a")
        top_bar.pack(fill="x", pady=(0, 15))

        r1_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        r1_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(r1_frame, text="Select Audit Target Profile Summary:", font=ctk.CTkFont(weight="bold")).pack(
            side="left", padx=5)
        self.drop_summary_mid = ctk.CTkOptionMenu(r1_frame, values=["No Members Registered"], height=35,
                                                  fg_color="#1e293b", command=lambda v: self.trigger_member_audit(v))
        self.drop_summary_mid.pack(side="left", padx=5)

        self.lbl_member_total = ctk.CTkLabel(r1_frame, text="Lifetime Payment Contributed: 0.00 Tk",
                                             font=ctk.CTkFont(size=15, weight="bold"), text_color="#3b82f6")
        self.lbl_member_total.pack(side="right", padx=10)

        r2_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        r2_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(r2_frame, text="From Date:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(5, 2))
        self.ent_audit_from = ctk.CTkEntry(r2_frame, placeholder_text="YYYY-MM-DD", width=110, height=30)
        self.ent_audit_from.insert(0, "2026-01-01");
        self.ent_audit_from.pack(side="left", padx=2)
        ctk.CTkButton(r2_frame, text="📅", width=30, height=30, fg_color="#334155",
                      command=lambda: CTkDatePicker(self, self.set_audit_from_field)).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(r2_frame, text="To Date:", font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
        self.ent_audit_to = ctk.CTkEntry(r2_frame, placeholder_text="YYYY-MM-DD", width=110, height=30)
        self.ent_audit_to.insert(0, datetime.now().strftime("%Y-%m-%d"));
        self.ent_audit_to.pack(side="left", padx=2)
        ctk.CTkButton(r2_frame, text="📅", width=30, height=30, fg_color="#334155",
                      command=lambda: CTkDatePicker(self, self.set_audit_to_field)).pack(side="left", padx=0)

        ctk.CTkButton(r2_frame, text="Filter Range", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#334155",
                      hover_color="#475569", width=110, height=30,
                      command=lambda: self.trigger_member_audit(self.drop_summary_mid.get())).pack(side="left", padx=15)
        ctk.CTkButton(r2_frame, text="⬇️ Audit Sheet PDF", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#10b981",
                      hover_color="#059669", width=130, height=30, command=self.download_filtered_audit_sheet_pdf).pack(
            side="right", padx=10)

        columns = ("txid", "date", "type", "amount", "method", "ref")
        self.tree_member_summary = ttk.Treeview(self.frames["summary"], columns=columns, show="headings")
        self.apply_treeview_styles(self.tree_member_summary, columns)
        self.tree_member_summary.pack(fill="both", expand=True, padx=10, pady=10)

    def set_audit_from_field(self, date_string):
        self.ent_audit_from.delete(0, 'end');
        self.ent_audit_from.insert(0, date_string)
        self.trigger_member_audit(self.drop_summary_mid.get())

    def set_audit_to_field(self, date_string):
        self.ent_audit_to.delete(0, 'end');
        self.ent_audit_to.insert(0, date_string)
        self.trigger_member_audit(self.drop_summary_mid.get())

    def download_filtered_audit_sheet_pdf(self):
        target_mid = self.drop_summary_mid.get()
        if target_mid == "No Members Registered": return
        f_date = self.ent_audit_from.get().strip()
        t_date = self.ent_audit_to.get().strip()

        self.cursor.execute(
            "SELECT id, date, type, amount, method, reference FROM income WHERE member_id=? AND date >= ? AND date <= ? ORDER BY date ASC",
            (target_mid, f_date, t_date))
        records = self.cursor.fetchall()
        total_sum = sum(r[3] for r in records)

        file_path = filedialog.asksaveasfilename(initialfile=f"Audit_Sheet_{target_mid}.pdf", defaultextension=".pdf")
        if file_path:
            self.generate_audit_sheet_pdf(file_path, target_mid, f_date, t_date, records, total_sum)
            messagebox.showinfo("Audit Sheet Saved", f"Single sheet statement compiled for Member {target_mid}.")

    def trigger_member_audit(self, selected_mid):
        for row in self.tree_member_summary.get_children(): self.tree_member_summary.delete(row)
        if selected_mid == "No Members Registered": return
        f_date = self.ent_audit_from.get().strip()
        t_date = self.ent_audit_to.get().strip()

        self.cursor.execute(
            "SELECT id, date, type, amount, method, reference FROM income WHERE member_id=? AND date >= ? AND date <= ? ORDER BY date DESC",
            (selected_mid, f_date, t_date))
        records = self.cursor.fetchall()

        member_range_total = 0.0
        for row in records:
            self.tree_member_summary.insert("", "end", values=row)
            member_range_total += row[3]
        self.lbl_member_total.configure(text=f"Selected Range Contribution: {member_range_total:,} Tk")

    # ==========================================
    # REPORTS MASTER TERMINAL MODULE
    # ==========================================
    def init_reports_view(self):
        lbl = ctk.CTkLabel(self.frames["reports"], text="Master Reports & Statement Engine",
                           font=ctk.CTkFont(size=20, weight="bold"))
        lbl.pack(anchor="w", pady=(10, 15))

        ctrl_panel = ctk.CTkFrame(self.frames["reports"], fg_color="#0f172a", height=85)
        ctrl_panel.pack(fill="x", pady=5)

        inner_box = ctk.CTkFrame(ctrl_panel, fg_color="transparent")
        inner_box.pack(pady=12, padx=10, fill="x")

        ctk.CTkLabel(inner_box, text="Global Start Date:", font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
        self.ent_rep_from = ctk.CTkEntry(inner_box, width=110, height=30)
        self.ent_rep_from.insert(0, "2026-06-01");
        self.ent_rep_from.pack(side="left", padx=2)
        ctk.CTkButton(inner_box, text="📅", width=30, height=30, fg_color="#334155", command=lambda: CTkDatePicker(self,
                                                                                                                  lambda
                                                                                                                      s: (
                                                                                                                      self.ent_rep_from.delete(
                                                                                                                          0,
                                                                                                                          'end'),
                                                                                                                      self.ent_rep_from.insert(
                                                                                                                          0,
                                                                                                                          s)))).pack(
            side="left", padx=(0, 15))

        ctk.CTkLabel(inner_box, text="Global End Date:", font=ctk.CTkFont(size=11)).pack(side="left", padx=2)
        self.ent_rep_to = ctk.CTkEntry(inner_box, width=110, height=30)
        self.ent_rep_to.insert(0, datetime.now().strftime("%Y-%m-%d"));
        self.ent_rep_to.pack(side="left", padx=2)
        ctk.CTkButton(inner_box, text="📅", width=30, height=30, fg_color="#334155", command=lambda: CTkDatePicker(self,
                                                                                                                  lambda
                                                                                                                      s: (
                                                                                                                      self.ent_rep_to.delete(
                                                                                                                          0,
                                                                                                                          'end'),
                                                                                                                      self.ent_rep_to.insert(
                                                                                                                          0,
                                                                                                                          s)))).pack(
            side="left", padx=0)

        bt_frame = ctk.CTkScrollableFrame(self.frames["reports"], fg_color="transparent")
        bt_frame.pack(fill="both", expand=True, pady=15)

        reports_manifest = [
            ("📊 Date-wise Total Fund Received Statement", "fund_received", "#3b82f6"),
            ("📜 Total Collection History Audit Report", "collection_history", "#10b981"),
            ("🚨 Total Active Outstanding Due List", "due_list", "#ef4444"),
            ("💸 Total Itemized Expense Ledger List", "expense_list", "#f59e0b")
        ]

        for text, key, color in reports_manifest:
            row_f = ctk.CTkFrame(bt_frame, fg_color="#0f172a", height=65)
            row_f.pack(fill="x", pady=6, padx=5)
            row_f.pack_propagate(False)

            ctk.CTkLabel(row_f, text=text, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=20)
            ctk.CTkButton(row_f, text="📥 Generate Statement PDF", font=ctk.CTkFont(weight="bold"), fg_color=color,
                          hover_color=color, width=180, height=36,
                          command=lambda k=key: self.execute_report_generation(k)).pack(side="right", padx=15, pady=12)

    def execute_report_generation(self, key):
        f_date = self.ent_rep_from.get().strip()
        t_date = self.ent_rep_to.get().strip()

        if key == "fund_received":
            self.cursor.execute(
                "SELECT date, type, method, SUM(amount) FROM income WHERE date >= ? AND date <= ? GROUP BY date, type, method ORDER BY date ASC",
                (f_date, t_date))
            records = self.cursor.fetchall()
            total_val = sum(r[3] for r in records)
            file_path = filedialog.asksaveasfilename(initialfile=f"DateWise_Fund_Received_{f_date}_to_{t_date}.pdf",
                                                     defaultextension=".pdf")
            if file_path:
                self.generate_global_report_pdf(file_path, "Date-Wise Total Fund Received Summary", f_date, t_date,
                                                ["DATE RECORDED", "FUND CATEGORY HEAD", "COLLECTION CHANNEL",
                                                 "SUMMED RECEIVED AMOUNT"], records, total_val)
                messagebox.showinfo("Compiled", "PDF Generated.")

        elif key == "collection_history":
            self.cursor.execute(
                "SELECT date, member_id, type, method, amount FROM income WHERE date >= ? AND date <= ? ORDER BY date ASC",
                (f_date, t_date))
            records = self.cursor.fetchall()
            total_val = sum(r[4] for r in records)
            file_path = filedialog.asksaveasfilename(initialfile=f"Total_Collection_History_{f_date}_to_{t_date}.pdf",
                                                     defaultextension=".pdf")
            if file_path:
                self.generate_global_report_pdf(file_path, "Chronological Collection History Ledger", f_date, t_date,
                                                ["POSTING DATE", "MEMBER REF ID", "FUND ALIGNED", "CHANNEL",
                                                 "AMOUNT (TK)"], records, total_val)
                messagebox.showinfo("Compiled", "PDF Generated.")

        elif key == "due_list":
            now = datetime.now()
            self.cursor.execute("SELECT member_id, name, phone, email FROM members WHERE status='Active'")
            m_pool = self.cursor.fetchall()
            due_records = []

            for m in m_pool:
                self.cursor.execute(
                    "SELECT COUNT(*) FROM income WHERE member_id=? AND type='Subscription' AND date >= ? AND date <= ?",
                    (m[0], f_date, t_date))
                if self.cursor.fetchone()[0] == 0:
                    due_records.append([m[0], m[1], m[2], m[3], "🚨 UNPAID SUBSCRIPTION"])

            file_path = filedialog.asksaveasfilename(initialfile=f"Outstanding_Due_List_{f_date}_to_{t_date}.pdf",
                                                     defaultextension=".pdf")
            if file_path:
                self.generate_global_report_pdf(file_path, "Outstanding Subscription Due Matrices List", f_date, t_date,
                                                ["MEMBER ID", "FULL NAME NAME", "PHONE CONTACT",
                                                 "EMAIL ROUTING ADDRESS", "CURRENT STATUS STATUS"], due_records, None)
                messagebox.showinfo("Compiled", "PDF Generated.")

        elif key == "expense_list":
            self.cursor.execute(
                "SELECT date, category, details, amount FROM expenses WHERE date >= ? AND date <= ? ORDER BY date ASC",
                (f_date, t_date))
            records = self.cursor.fetchall()
            total_val = sum(r[3] for r in records)
            file_path = filedialog.asksaveasfilename(initialfile=f"Total_Expense_List_{f_date}_to_{t_date}.pdf",
                                                     defaultextension=".pdf")
            if file_path:
                self.generate_global_report_pdf(file_path, "Comprehensive Expense Outflow Registries", f_date, t_date,
                                                ["DISBURSEMENT DATE", "CATEGORY ALLOCATION HEAD",
                                                 "ITEMIZED ALLOCATION MEMOS", "AMOUNT OUT (TK)"], records, total_val)
                messagebox.showinfo("Compiled", "PDF Generated.")

    # ==========================================
    # TRANSACTIONS TRANSFERS MODULE
    # ==========================================
    def init_transfer_view(self):
        form_frame = ctk.CTkFrame(self.frames["transfer"], width=340, fg_color="#0f172a")
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        ctk.CTkLabel(form_frame, text="Clear Liquidity Pools to Master Bank", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#10b981").pack(pady=20)
        self.drop_trans_source = ctk.CTkOptionMenu(form_frame, values=["bKash", "Cash"], height=35, fg_color="#1e293b")
        self.drop_trans_source.pack(fill="x", padx=20, pady=8)
        self.ent_trans_amount = ctk.CTkEntry(form_frame, placeholder_text="Transfer Clearing Amount (Tk)", height=35)
        self.ent_trans_amount.pack(fill="x", padx=20, pady=12)
        self.ent_trans_ref = ctk.CTkEntry(form_frame, placeholder_text="Bank Slip Verification Note", height=35)
        self.ent_trans_ref.pack(fill="x", padx=20, pady=12)
        ctk.CTkButton(form_frame, text="Execute Internal Ledger Settlement", font=ctk.CTkFont(weight="bold"),
                      fg_color="#3b82f6", hover_color="#2563eb", height=42, command=self.execute_bank_transfer).pack(
            fill="x", padx=20, pady=25)

        list_frame = ctk.CTkFrame(self.frames["transfer"], fg_color="transparent")
        list_frame.pack(side="right", fill="both", expand=True)
        columns = ("id", "date", "source", "amount", "ref")
        self.tree_transfers = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.apply_treeview_styles(self.tree_transfers, columns)
        self.tree_transfers.pack(fill="both", expand=True, padx=10, pady=10)

    def apply_treeview_styles(self, tree, columns):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0f172a", fieldbackground="#0f172a", foreground="#f8fafc", rowheight=32,
                        borderwidth=0, font=('Segoe UI', 10))
        style.configure("Treeview.Heading", background="#1e293b", foreground="#10b981", font=('Segoe UI', 10, 'bold'),
                        borderwidth=0)
        style.map("Treeview", background=[('selected', '#334155')], foreground=[('selected', '#10b981')])
        for col in columns:
            display_name = col.replace("member_id", "MEMBER ID").upper()
            tree.heading(col, text=display_name)
            tree.column(col, anchor="center", width=120)

    def create_form_input(self, master, placeholder):
        e = ctk.CTkEntry(master, placeholder_text=placeholder, height=35, fg_color="#1e293b", border_color="#334155")
        e.pack(fill="x", padx=25, pady=6)
        return e

    def browse_profile_image(self):
        f_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if f_path:
            try:
                pil_img = PILImage.open(f_path).resize((110, 120), PILImage.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                self.img_canvas.configure(image=tk_img, text="")
                self.img_canvas.image = tk_img

                img_byte_arr = io.BytesIO()
                if pil_img.mode in ("RGBA", "P"): pil_img = pil_img.convert("RGB")
                pil_img.save(img_byte_arr, format='JPEG', quality=85)
                self.selected_img_bytes = img_byte_arr.getvalue()
            except Exception as e:
                messagebox.showerror("Image Error", str(e))

    # ==========================================
    # COMPONENT LOADERS & UPDATERS
    # ==========================================
    def load_member_to_edit(self):
        selection = self.tree_members.selection()
        if not selection:
            messagebox.showerror("Selection Error",
                                 "Please click/select an active member row entry from the grid log map first.")
            return
        m_id = self.tree_members.item(selection[0])['values'][0]
        self.cursor.execute("SELECT * FROM members WHERE member_id = ?", (m_id,))
        row = self.cursor.fetchone()

        if row:
            self.active_edit_member_id = m_id
            self.lbl_member_form_title.configure(text=f"Modify Registered Profile ({m_id})", text_color="#f59e0b")
            self.btn_member_save.configure(text="Apply Changes", fg_color="#f59e0b")
            self.btn_member_cancel.pack(fill="x", padx=25, pady=2)

            self.ent_m_name.delete(0, 'end');
            self.ent_m_name.insert(0, str(row[1]))
            self.ent_m_father.delete(0, 'end');
            self.ent_m_father.insert(0, str(row[2] or ''))
            self.ent_m_mother.delete(0, 'end');
            self.ent_m_mother.insert(0, str(row[3] or ''))
            self.drop_m_gender.set(row[4] if row[4] else "Male")
            self.ent_m_dob.delete(0, 'end');
            self.ent_m_dob.insert(0, str(row[5] or ''))
            self.ent_m_phone.delete(0, 'end');
            self.ent_m_phone.insert(0, str(row[6] or ''))
            self.ent_m_email.delete(0, 'end');
            self.ent_m_email.insert(0, str(row[7] or ''))
            self.ent_m_nid.delete(0, 'end');
            self.ent_m_nid.insert(0, str(row[8] or ''))
            self.ent_m_blood.delete(0, 'end');
            self.ent_m_blood.insert(0, str(row[9] or ''))
            self.ent_nom_name.delete(0, 'end');
            self.ent_nom_name.insert(0, str(row[10] or ''))
            self.ent_nom_relation.delete(0, 'end');
            self.ent_nom_relation.insert(0, str(row[11] or ''))
            self.ent_nom_phone.delete(0, 'end');
            self.ent_nom_phone.insert(0, str(row[12] or ''))
            self.ent_m_adm.delete(0, 'end');
            self.ent_m_adm.insert(0, str(row[13]))
            self.ent_m_present_addr.delete(0, 'end');
            self.ent_m_present_addr.insert(0, str(row[16] or ''))
            self.ent_m_perm_addr.delete(0, 'end');
            self.ent_m_perm_addr.insert(0, str(row[17] or ''))

            if row[14]:
                self.selected_img_bytes = row[14]
                try:
                    p_img = PILImage.open(io.BytesIO(row[14])).resize((110, 120), PILImage.Resampling.LANCZOS)
                    tk_bi = ImageTk.PhotoImage(p_img)
                    self.img_canvas.configure(image=tk_bi, text="")
                    self.img_canvas.image = tk_bi
                except:
                    pass

    def reset_member_form_state(self):
        self.active_edit_member_id = None
        self.lbl_member_form_title.configure(text="Enroll New Profile Dossier", text_color="#10b981")
        self.btn_member_save.configure(text="Save Member Profile", fg_color="#10b981")
        self.btn_member_cancel.pack_forget()
        self.selected_img_bytes = None
        self.img_canvas.configure(image="", text="[ Photo Box ]")
        for entry in [self.ent_m_name, self.ent_m_father, self.ent_m_mother, self.ent_m_dob, self.ent_m_phone,
                      self.ent_m_email, self.ent_m_nid, self.ent_m_blood, self.ent_nom_name, self.ent_nom_relation,
                      self.ent_nom_phone, self.ent_m_present_addr, self.ent_m_perm_addr]:
            entry.delete(0, 'end')
        self.refresh_all_data()

    def load_income_to_edit(self):
        selection = self.tree_income.selection()
        if not selection:
            messagebox.showerror("Selection Error", "Please click/select an active receipt row first.")
            return
        inc_id = self.tree_income.item(selection[0])['values'][0]
        self.cursor.execute("SELECT * FROM income WHERE id = ?", (inc_id,))
        row = self.cursor.fetchone()
        if row:
            self.active_edit_income_id = inc_id
            self.lbl_income_form_title.configure(text=f"Update Record (#{inc_id})", text_color="#f59e0b")
            self.btn_income_save.configure(text="Apply Modifications Updates", fg_color="#f59e0b")
            self.btn_income_cancel.pack(fill="x", padx=20, pady=2)
            self.drop_acc_mid.set(row[2]);
            self.drop_acc_type.set(row[3])
            self.ent_acc_date.delete(0, 'end');
            self.ent_acc_date.insert(0, row[1])
            self.ent_acc_amount.delete(0, 'end');
            self.ent_acc_amount.insert(0, str(row[4]))
            self.drop_acc_method.set(row[5]);
            self.ent_acc_ref.delete(0, 'end');
            self.ent_acc_ref.insert(0, row[7] if row[7] else '')

    def reset_income_form_state(self):
        self.active_edit_income_id = None
        self.lbl_income_form_title.configure(text="Log Incoming Transactions", text_color="#10b981")
        self.btn_income_save.configure(text="Post Receipt Entry", fg_color="#10b981")
        self.btn_income_cancel.pack_forget()
        self.ent_acc_amount.delete(0, 'end');
        self.ent_acc_ref.delete(0, 'end')
        self.refresh_all_data()

    def load_expense_to_edit(self):
        selection = self.tree_expenses.selection()
        if not selection: return
        exp_id = self.tree_expenses.item(selection[0])['values'][0]
        self.cursor.execute("SELECT * FROM expenses WHERE id = ?", (exp_id,))
        row = self.cursor.fetchone()
        if row:
            self.active_edit_expense_id = exp_id
            self.lbl_expense_form_title.configure(text=f"Modify Cost Row (#{exp_id})", text_color="#f59e0b")
            self.btn_expense_save.configure(text="Save Modifications", fg_color="#f59e0b")
            self.btn_expense_cancel.pack(fill="x", padx=20, pady=2)
            self.drop_exp_cat.set(row[2]);
            self.ent_exp_amount.delete(0, 'end');
            self.ent_exp_amount.insert(0, str(row[3]))
            self.ent_exp_details.delete(0, 'end');
            self.ent_exp_details.insert(0, row[4] if row[4] else '')

    def reset_expense_form_state(self):
        self.active_edit_expense_id = None
        self.lbl_expense_form_title.configure(text="Log Expenditure Outflows", text_color="#10b981")
        self.btn_expense_save.configure(text="Log Expense Inflow", fg_color="#10b981")
        self.btn_expense_cancel.pack_forget()
        self.ent_exp_amount.delete(0, 'end');
        self.ent_exp_details.delete(0, 'end')
        self.refresh_all_data()

    # ==========================================
    # DATA WRITERS LOGIC IMPLEMENTATION
    # ==========================================
    def save_member_profile(self):
        name = self.ent_m_name.get().strip()
        f_name = self.ent_m_father.get().strip()
        m_name = self.ent_m_mother.get().strip()
        gender = self.drop_m_gender.get()
        dob = self.ent_m_dob.get().strip()
        phone = self.ent_m_phone.get().strip()
        email = self.ent_m_email.get().strip()
        nid = self.ent_m_nid.get().strip()
        blood = self.ent_m_blood.get().strip()
        adm_fee = self.ent_m_adm.get().strip()
        nom_name = self.ent_nom_name.get().strip()
        nom_rel = self.ent_nom_relation.get().strip()
        nom_ph = self.ent_nom_phone.get().strip()
        pres_addr = self.ent_m_present_addr.get().strip()
        perm_addr = self.ent_m_perm_addr.get().strip()

        if not name or not phone:
            messagebox.showerror("Validation Error", "Full Name and Contact Mobile fields are strictly required.")
            return
        try:
            fee = float(adm_fee or 0.0)
        except ValueError:
            fee = 0.0

        if self.active_edit_member_id:
            self.cursor.execute("""
                UPDATE members SET name=?, father_husband_name=?, mother_name=?, gender=?, dob=?, phone=?, email=?,
                                   nid=?, blood_group=?, nominee_name=?, nominee_relation=?, nominee_phone=?, 
                                   admission_fee_paid=?, profile_pic=?, present_address=?, permanent_address=?
                WHERE member_id=?
            """, (name, f_name, m_name, gender, dob, phone, email, nid, blood, nom_name, nom_rel, nom_ph, fee,
                  self.selected_img_bytes, pres_addr, perm_addr, self.active_edit_member_id))
            messagebox.showinfo("Success", "Operational Profile updated.")
            self.reset_member_form_state()
        else:
            auto_id = self.get_next_member_id()
            self.cursor.execute("""
                INSERT INTO members (member_id, name, father_husband_name, mother_name, gender, dob, phone, email, nid, blood_group, nominee_name, nominee_relation, nominee_phone, admission_fee_paid, profile_pic, status, present_address, permanent_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?, ?)
            """, (auto_id, name, f_name, m_name, gender, dob, phone, email, nid, blood, nom_name, nom_rel, nom_ph, fee,
                  self.selected_img_bytes, 'Active', pres_addr, perm_addr))
            messagebox.showinfo("Success", f"Profile registered under ID: {auto_id}")
            self.reset_member_form_state()
        self.conn.commit()

    def save_income_record(self):
        selected_mid = self.drop_acc_mid.get()
        if selected_mid == "No Members Registered": return
        inc_type = self.drop_acc_type.get()
        amount_str = self.ent_acc_amount.get().strip()
        method = self.drop_acc_method.get()
        ref = self.ent_acc_ref.get().strip()
        date_str = self.ent_acc_date.get().strip()

        try:
            amt = float(amount_str)
            if amt <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Input valid amount value.")
            return

        try:
            p_date = datetime.strptime(date_str, "%Y-%m-%d")
            paid_month = f"{p_date.strftime('%B')}'_{p_date.strftime('%y')}"
        except:
            paid_month = "N/A"

        if self.active_edit_income_id:
            self.cursor.execute(
                "UPDATE income SET date=?, member_id=?, type=?, amount=?, method=?, paid_month=?, reference=? WHERE id=?",
                (date_str, selected_mid, inc_type, amt, method, paid_month, ref, self.active_edit_income_id))
            self.conn.commit()
            self.reset_income_form_state()
        else:
            safe_month = paid_month.replace("'", "_")
            file_path = filedialog.asksaveasfilename(initialfile=f"Receipt_{selected_mid}_{safe_month}.pdf",
                                                     defaultextension=".pdf")
            if not file_path: return
            self.cursor.execute(
                "INSERT INTO income (date, member_id, type, amount, method, paid_month, reference) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (date_str, selected_mid, inc_type, amt, method, paid_month, ref))
            self.conn.commit()
            self.generate_pdf_receipt(file_path, self.cursor.lastrowid, date_str, selected_mid, inc_type, amt, method,
                                      paid_month, ref)
            self.reset_income_form_state()

    def save_expense_record(self):
        cat = self.drop_exp_cat.get()
        amount_str = self.ent_exp_amount.get().strip()
        details = self.ent_exp_details.get().strip()
        date_str = datetime.now().strftime("%Y-%m-%d")

        try:
            amt = float(amount_str)
        except ValueError:
            return

        if self.active_edit_expense_id:
            self.cursor.execute("UPDATE expenses SET category=?, amount=?, details=? WHERE id=?",
                                (cat, amt, details, self.active_edit_expense_id))
        else:
            self.cursor.execute("INSERT INTO expenses (date, category, amount, details) VALUES (?, ?, ?, ?)",
                                (date_str, cat, amt, details))
        self.conn.commit()
        self.reset_expense_form_state()

    def execute_bank_transfer(self):
        source = self.drop_trans_source.get()
        amount_str = self.ent_trans_amount.get().strip()
        ref = self.ent_trans_ref.get().strip()
        date_str = datetime.now().strftime("%Y-%m-%d")
        try:
            amt = float(amount_str)
        except ValueError:
            return
        self.cursor.execute("INSERT INTO transfers (date, source_method, amount, reference) VALUES (?, ?, ?, ?)",
                            (date_str, source, amt, ref or "Clearance Transfer"))
        self.conn.commit()
        self.refresh_all_data()

    def download_selected_profile_pdf(self):
        selected_item = self.tree_members.selection()
        if not selected_item: return
        m_id = self.tree_members.item(selected_item[0])['values'][0]
        file_path = filedialog.asksaveasfilename(initialfile=f"Premium_BioData_{m_id}.pdf", defaultextension=".pdf")
        if file_path:
            self.generate_profile_pdf(file_path, m_id)
            messagebox.showinfo("Export Successful", "Official Document Generated.")

    # ==========================================
    # CORE SYSTEM LEDGER REFRESH ENGINE
    # ==========================================
    def refresh_all_data(self):
        next_id = self.get_next_member_id()
        self.lbl_next_id.configure(text=f"Assigned Next Member ID: {next_id}")
        self.refresh_expense_categories_dropdown()
        self.calculate_and_render_dues_grid()

        for row in self.tree_members.get_children(): self.tree_members.delete(row)
        self.cursor.execute("SELECT member_id, name, phone, email, nid, status FROM members")
        all_members = self.cursor.fetchall()

        member_ids_list = []
        for row in all_members:
            self.tree_members.insert("", "end", values=row)
            member_ids_list.append(row[0])

        if member_ids_list:
            self.drop_acc_mid.configure(values=member_ids_list)
            self.drop_summary_mid.configure(values=member_ids_list)
        else:
            self.drop_acc_mid.configure(values=["No Members Registered"])
            self.drop_summary_mid.configure(values=["No Members Registered"])

        for row in self.tree_income.get_children(): self.tree_income.delete(row)
        self.cursor.execute("SELECT id, date, member_id, type, amount, method, reference FROM income ORDER BY id DESC")
        for row in self.cursor.fetchall(): self.tree_income.insert("", "end", values=row)

        for row in self.tree_transfers.get_children(): self.tree_transfers.delete(row)
        self.cursor.execute("SELECT * FROM transfers ORDER BY id DESC")
        for row in self.cursor.fetchall(): self.tree_transfers.insert("", "end", values=row)

        for row in self.tree_expenses.get_children(): self.tree_expenses.delete(row)
        self.cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
        for row in self.cursor.fetchall(): self.tree_expenses.insert("", "end", values=row)

        self.cursor.execute("SELECT SUM(amount) FROM income WHERE method='Cash'")
        raw_cash = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(amount) FROM income WHERE method='bKash'")
        raw_bkash = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(amount) FROM income WHERE method='Bank'")
        raw_bank = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("SELECT SUM(amount) FROM income")
        total_fund_collection = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("SELECT SUM(amount) FROM income WHERE date >= '2026-06-01' AND date <= '2026-06-30'")
        june_fund_collection = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute("SELECT SUM(amount) FROM income WHERE type='Subscription'")
        sum_sub = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(amount) FROM income WHERE type='Donation'")
        sum_don = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(amount) FROM transfers WHERE source_method='Cash'")
        trans_out_cash = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(amount) FROM transfers WHERE source_method='bKash'")
        trans_out_bkash = self.cursor.fetchone()[0] or 0.0
        self.cursor.execute("SELECT SUM(amount) FROM expenses")
        total_exp = self.cursor.fetchone()[0] or 0.0

        final_cash = raw_cash - trans_out_cash - total_exp
        final_bkash = raw_bkash - trans_out_bkash
        final_bank = raw_bank + trans_out_cash + trans_out_bkash
        net_liquid_capital = final_cash + final_bkash + final_bank

        self.lbl_acc_summary.configure(
            text=f"Summary Balance Reports: Subscriptions: {sum_sub:,} Tk  |  Donations: {sum_don:,} Tk")
        self.card_cash.configure(text=f"Cash Balance\n{final_cash:,} Tk")
        self.card_bkash.configure(text=f"bKash Balance\n{final_bkash:,} Tk")
        self.card_bank.configure(text=f"Bank Balance\n{final_bank:,} Tk")
        self.card_expense.configure(text=f"Total Expenses\n{total_exp:,} Tk")
        self.card_balance.configure(text=f"Net Liquid Capital\n{net_liquid_capital:,} Tk")

        self.card_total_collection.configure(text=f"Total Fund Collection\n{total_fund_collection:,} Tk")
        self.card_june_collection.configure(text=f"Fund Collection of June'26\n{june_fund_collection:,} Tk")


import customtkinter as ctk
from tkinter import messagebox


class DesktopLoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # উইন্ডো সেটিংস এবং স্ক্রিনের মাঝে পজিশন করা
        self.title("Somrido Premium Suite - Secure Login")
        self.geometry("450x550")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")  # আপনার ড্যাশবোর্ডের সাথে ম্যাচিং ডার্ক থিম

        # পাসওয়ার্ড দেখানোর ট্র্যাকিং ভ্যারিয়েবল
        self.password_shown = False

        # --- মূল ফ্রেম (কার্ড ডিজাইন) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ১. লোগো বা আইকন প্লেসহোল্ডার এবং টাইটেল
        self.logo_label = ctk.CTkLabel(
            self.main_frame,
            text="📊",
            font=ctk.CTkFont(size=45)
        )
        self.logo_label.pack(pady=(30, 5))

        self.label_title = ctk.CTkLabel(
            self.main_frame,
            text="Somrido Accounts",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#4CAF50"  # আপনার সেই চেনা সিগনেচার গ্রিন কালার
        )
        self.label_title.pack(pady=(0, 5))

        self.label_subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Premium Management Portal",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.label_subtitle.pack(pady=(0, 25))

        # ২. ইউজারনেম ইনপুট ফিল্ড
        self.username_label = ctk.CTkLabel(self.main_frame, text="Username", font=ctk.CTkFont(size=12, weight="bold"),
                                           text_color="gray")
        self.username_label.pack(anchor="w", padx=45, pady=(5, 2))

        self.entry_username = ctk.CTkEntry(
            self.main_frame,
            width=320,
            height=40,
            placeholder_text="Enter 'somrido'",
            border_color="#333333",
            fg_color="#2b2b2b"
        )
        self.entry_username.pack(pady=(0, 15))

        # ৩. পাসওয়ার্ড ইনপুট ফিল্ড
        self.password_label = ctk.CTkLabel(self.main_frame, text="Password", font=ctk.CTkFont(size=12, weight="bold"),
                                           text_color="gray")
        self.password_label.pack(anchor="w", padx=45, pady=(5, 2))

        # পাসওয়ার্ড কন্টেইনার ফ্রেম (ইনপুট + শো বাটন একসাথে রাখার জন্য)
        self.pass_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.pass_frame.pack(pady=(0, 5))

        self.entry_password = ctk.CTkEntry(
            self.pass_frame,
            width=275,
            height=40,
            placeholder_text="Enter Password",
            show="*",
            border_color="#333333",
            fg_color="#2b2b2b"
        )
        self.entry_password.pack(side="left")

        # পাসওয়ার্ড শো/হাইড বাটন (👁️ আইকন সহ)
        self.btn_show_pass = ctk.CTkButton(
            self.pass_frame,
            text="👁️",
            width=40,
            height=40,
            fg_color="#2b2b2b",
            hover_color="#333333",
            border_width=1,
            border_color="#333333",
            command=self.toggle_password
        )
        self.btn_show_pass.pack(side="left", padx=(5, 0))

        # ৪. ফরগট পাসওয়ার্ড অপশন (Forgot Password)
        self.btn_forgot = ctk.CTkButton(
            self.main_frame,
            text="Forgot Password?",
            font=ctk.CTkFont(size=12, underline=True),
            fg_color="transparent",
            hover_color="#1e1e1e",
            text_color="gray",
            width=100,
            command=self.action_forgot
        )
        self.btn_forgot.pack(anchor="e", padx=45, pady=(0, 20))

        # ৫. প্রিমিয়াম লগইন বাটন
        self.btn_login = ctk.CTkButton(
            self.main_frame,
            text="SIGN IN",
            width=320,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#3e8e41",
            corner_radius=8,
            command=self.check_login
        )
        self.btn_login.pack(pady=10)

        # ৬. সাইন আপ সেকশন (Sign Up)
        self.signup_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.signup_frame.pack(pady=(20, 10))

        self.lbl_signup_text = ctk.CTkLabel(self.signup_frame, text="Don't have an account?", text_color="gray",
                                            font=ctk.CTkFont(size=12))
        self.lbl_signup_text.pack(side="left")

        self.btn_signup = ctk.CTkButton(
            self.signup_frame,
            text="Sign Up",
            font=ctk.CTkFont(size=12, weight="bold", underline=True),
            fg_color="transparent",
            hover_color="#1e1e1e",
            text_color="#4CAF50",
            width=50,
            command=self.action_signup
        )
        self.btn_signup.pack(side="left", padx=(2, 0))

    def toggle_password(self):
        # পাসওয়ার্ড দেখানো বা লুকানোর লজিক
        if self.password_shown:
            self.entry_password.configure(show="*")
            self.btn_show_pass.configure(text="👁️")
            self.password_shown = False
        else:
            self.entry_password.configure(show="")
            self.btn_show_pass.configure(text="🔒")
            self.password_shown = True

    def check_login(self):
        # আপনার দেওয়া নির্দিষ্ট ইউজারনেম এবং পাসওয়ার্ড ভ্যালিডেশন
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if username == "somrido" and password == "admin321":
            self.destroy()  # লগইন সফল হলে উইন্ডো বন্ধ হবে
            open_main_system()  # আসল ড্যাশবোর্ড ওপেন হবে
        else:
            messagebox.showerror("Access Denied", "Incorrect Username or Password!")

    def action_forgot(self):
        # ফরগট পাসওয়ার্ডে ক্লিক করলে যা দেখাবে
        messagebox.showinfo("Reset Password", "Please contact the Master Developer to reset your Admin credentials.")

    def action_signup(self):
        # সাইন আপে ক্লিক করলে যা দেখাবে
        messagebox.showwarning("Registration Locked", "New registrations are currently locked. Contact Administrator.")


def open_main_system():
    # এটি আপনার আসল প্রিমিয়াম ড্যাশবোর্ড ক্লাসকে কল করে সচল করবে
    app = SomridoPremiumSystem()
    app.mainloop()


# পাইথন ফাইল রান করার মূল গেটওয়ে
if __name__ == "__main__":
    login_screen = DesktopLoginWindow()
    login_screen.mainloop()
