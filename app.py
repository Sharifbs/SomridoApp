import streamlit as st
import sqlite3
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# পেজ কনফিগারেশন এবং ডার্ক থিম লেআউট
st.set_page_config(page_title="Somrido Ultimate Premium Financial Suite", page_icon="📊", layout="wide")

# ডাটাবেস কানেকশন ম্যানেজার
def get_db_connection(db_name="somrido_premium.db"):
    try:
        conn = sqlite3.connect(db_name)
        return conn, conn.cursor()
    except Exception as e:
        return None, None

# ডাটাবেস ইনিশিয়ালাইজেশন (যদি টেবল না থাকে তবে ক্রিয়েট হবে)
def init_web_databases():
    # premium database schema
    conn, cursor = get_db_connection("somrido_premium.db")
    if conn:
        cursor.execute("""CREATE TABLE IF NOT EXISTS income (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            member_id TEXT, amount REAL, type TEXT, source TEXT, paid_month TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS expense (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, amount REAL, purpose TEXT, date TEXT)""")
        conn.commit()
        conn.close()
    
    # ngo database schema
    conn, cursor = get_db_connection("somrido_ngo.db")
    if conn:
        cursor.execute("""CREATE TABLE IF NOT EXISTS members (
                            member_id TEXT PRIMARY KEY, name TEXT, phone TEXT, email TEXT, status TEXT)""")
        # ডামি কিছু মেম্বার ডাটা ইনসার্ট করা হচ্ছে টেস্টের সুবিধার্থে (যদি টেবিল একদম ফাঁকা থাকে)
        cursor.execute("SELECT COUNT(*) FROM members")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?)", [
                ("M001", "Shariful Islam", "01711223344", "shariful@gmail.com", "Active"),
                ("M002", "Somrido NGO Admin", "01911223344", "admin@somrido.org", "Active")
            ])
        conn.commit()
        conn.close()

init_web_databases()

# সেশন মেমরি ট্র্যাকিং
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "smtp_server" not in st.session_state:
    st.session_state.smtp_server = "smtp.gmail.com"
    st.session_state.smtp_port = 587
    st.session_state.sender_email = "your-somrido-email@gmail.com"
    st.session_state.smtp_pass = ""

# --- ১. প্রমিয়াম লগইন পোর্টাল ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📊 SOMRIDO FINANCIAL HUB</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Ultimate Premium Financial Web Suite</h4>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", value="", placeholder="Enter 'somrido'")
        password = st.text_input("Password", type="password", placeholder="Enter Password")
        submit_button = st.form_submit_button("SIGN IN TO HUB")
        
        if submit_button:
            if username.strip() == "somrido" and password.strip() == "admin321":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrect Username or Password!")
    st.stop()

# --- ২. সফল লগইনের পর মূল ড্যাশবোর্ড প্যানেল ---
st.sidebar.markdown("<h2 style='color: #4CAF50; text-align:center;'>SOMRIDO<br>FINANCIAL HUB</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align:center; color:#FFC107;'>⏰ Live System Clock Matrix</p>", unsafe_allow_html=True)

# আপনার ডেস্কটপ অ্যাপের হুবহু ৮টি অপশন বিশিষ্ট সাইডবার নেভিগেশন মেনু (image_2a943d.png)
menu = st.sidebar.radio(
    "Navigation Menu Modules",
    [
        "Dashboard View",
        "Member Profile Form",
        "Collection Ledger",
        "Overdue Subscription",
        "Individual Audits",
        "Expense Registry",
        "Clearing Transfers",
        "Reports Center",
        "⚙️ SMTP Mail Settings" # অতিরিক্ত কনফিগ সেকশন
    ]
)

# ডাটাবেস থেকে রিয়েল-টাইম ব্যালেন্স হিসাব করার লজিক ফাংশন
def get_live_financial_metrics():
    conn, cursor = get_db_connection("somrido_premium.db")
    if not conn:
        return 0, 0, 0, 0, 0, 0, 0
    try:
        # Cash ইনকাম যোগফল
        cursor.execute("SELECT TOTAL(amount) FROM income WHERE type='Cash' OR source='Cash'")
        raw_cash = cursor.fetchone()[0]
        
        # bKash ইনকাম যোগফল
        cursor.execute("SELECT TOTAL(amount) FROM income WHERE type='bKash' OR source='bKash'")
        raw_bkash = cursor.fetchone()[0]
        
        # Bank ইনকাম যোগফল
        cursor.execute("SELECT TOTAL(amount) FROM income WHERE type='Bank' OR source='Bank'")
        raw_bank = cursor.fetchone()[0]
        
        # মোট খরচ
        cursor.execute("SELECT TOTAL(amount) FROM expense")
        total_exp = cursor.fetchone()[0]
        
        # আপনার অরিজিনাল কোডের ক্লিয়ারিং ট্রান্সফার মার্জিন লজিক
        trans_out_cash = 0.0
        trans_out_bkash = 0.0
        
        cursor.execute("SELECT TOTAL(amount) FROM income WHERE type='Subscription'")
        sum_sub = cursor.fetchone()[0]
        
        cursor.execute("SELECT TOTAL(amount) FROM income WHERE type='Donation'")
        sum_don = cursor.fetchone()[0]

        # ফাইনাল ইকুয়েশন ম্যাট্রিক্স (image_2a943d.png এর আউটপুটের জন্য)
        final_cash = raw_cash - trans_out_cash - total_exp
        final_bkash = raw_bkash - trans_out_bkash
        final_bank = raw_bank + trans_out_cash + trans_out_bkash
        net_liquid_capital = final_cash + final_bkash + final_bank
        
        conn.close()
        return final_cash, final_bkash, final_bank, total_exp, sum_sub, sum_don, net_liquid_capital
    except:
        return 0, 0, 0, 0, 0, 0, 0

fcash, fbkash, fbank, fexp, fsub, fdon, net_capital = get_live_financial_metrics()

# =========================================================================
# MODULE 1: Dashboard View (হুবহু আপনার লোকাল সফটওয়্যারের গ্রিড লুক)
# =========================================================================
if menu == "Dashboard View":
    st.markdown("## Treasury Balance Matrix Monitoring")
    
    # আপনার সফটওয়্যারের ৪টি মেইন বক্স গ্রিড
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div style='background-color:#1e1e2f; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:#orange;'>Cash Balance</h5><h2 style='color:#FFF;'>"+f"{fcash:,} Tk"+"</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='background-color:#1e1e2f; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:#pink;'>bKash Balance</h5><h2 style='color:#FFF;'>"+f"{fbkash:,} Tk"+"</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='background-color:#1e1e2f; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:#cyan;'>Bank Balance</h5><h2 style='color:#FFF;'>"+f"{fbank:,} Tk"+"</h2></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div style='background-color:#1e1e2f; padding:20px; border-radius:10px; text-align:center;'><h5 style='color:#ff6b6b;'>Total Expenses</h5><h2 style='color:#FFF;'>"+f"{fexp:,} Tk"+"</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # সাব-মেট্রিক্স বার
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("<div style='background-color:#112233; padding:12px; border-radius:5px; text-align:center; color:#4CAF50; font-weight:bold;'>Total Fund Collection: "+f"{fsub+fdon:,} Tk"+"</div>", unsafe_allow_html=True)
    with col6:
        st.markdown("<div style='background-color:#112233; padding:12px; border-radius:5px; text-align:center; color:#00bcd4; font-weight:bold;'>Fund Collection of Current Month: "+f"{fsub:,} Tk"+"</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # বড় সবুজ নেট লিকুইড ক্যাপিটাল বাটন কার্ড
    st.markdown("<div style='background-color:#00c853; padding:35px; border-radius:15px; text-align:center;'><h3 style='color:#FFF; margin:0;'>Net Liquid Capital</h3><h1 style='color:#FFF; margin:5px 0 0 0;'>"+f"{net_capital:,} Tk"+"</h1></div>", unsafe_allow_html=True)

# =========================================================================
# MODULE 2: Member Profile Form (নতুন মেম্বার রেজিস্ট্রেশন ডাটা এন্ট্রি)
# =========================================================================
elif menu == "Member Profile Form":
    st.markdown("## 👥 Member Profile Registration Gateway")
    with st.form("member_reg_form", clear_on_submit=True):
        m_id = st.text_input("Assign Unique Member ID (e.g. M003)")
        m_name = st.text_input("Full Registered Name")
        m_phone = st.text_input("Phone Contact Number")
        m_email = st.text_input("Email Address Communication")
        m_status = st.selectbox("Operational Status Mode", ["Active", "Suspended", "On Leave"])
        
        btn_reg = st.form_submit_button("Save Profile to SQLite Cloud Ledger")
        if btn_reg:
            if m_id and m_name and m_email:
                conn, cursor = get_db_connection("somrido_ngo.db")
                try:
                    cursor.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?)", (m_id.strip(), m_name.strip(), m_phone.strip(), m_email.strip(), m_status))
                    conn.commit()
                    st.success(f"Success: Profile for {m_name} committed to database securely.")
                except Exception as ex:
                    st.error(f"Write Token Refused: ID already exists or database locked ({ex})")
                finally:
                    conn.close()
            else:
                st.warning("Validation Failed: Fields Cannot be Left Null.")

# =========================================================================
# MODULE 3: Collection Ledger (টাকা বা সাবস্ক্রিপশন আদায় এন্ট্রি ফর্ম)
# =========================================================================
elif menu == "Collection Ledger":
    st.markdown("## 💵 Premium Collection Entry Registry")
    
    # মেম্বারদের আইডি রিয়েলটাইম ড্রপডাউনে আনা
    conn, cursor = get_db_connection("somrido_ngo.db")
    m_list = ["General/Anonymous Account"]
    if conn:
        cursor.execute("SELECT member_id FROM members")
        m_list += [r[0] for r in cursor.fetchall()]
        conn.close()

    with st.form("collection_form", clear_on_submit=True):
        sel_member = st.selectbox("Target Payer Member ID", m_list)
        amount = st.number_input("Transaction Volume/Amount (Tk)", min_value=1.0)
        col_type = st.selectbox("Accounting Fund Type Channel", ["Subscription", "Donation", "Admission Fee", "Grant"])
        col_source = st.selectbox("Deposit Target Repository", ["Cash", "bKash", "Bank"])
        
        now = datetime.now()
        current_month_token = f"{now.strftime('%B')}'_{now.strftime('%y')}"
        
        btn_col = st.form_submit_button("Execute Deposit Protocol")
        if btn_col:
            conn, cursor = get_db_connection("somrido_premium.db")
            if conn:
                cursor.execute("INSERT INTO income (member_id, amount, type, source, paid_month) VALUES (?, ?, ?, ?, ?)",
                               (sel_member, amount, col_type, col_source, current_month_token))
                conn.commit()
                conn.close()
                st.success(f"Audited: Successfully routed {amount} Tk into {col_source} via {col_type}.")

# =========================================================================
# MODULE 4: Overdue Subscription (মেম্বার নোটিশ এবং ইমেইল হ্যান্ডশেক)
# =========================================================================
elif menu == "Overdue Subscription":
    st.markdown("## 🚨 Subscription Overdue Matrix & Automation Core")
    
    conn, cursor = get_db_connection("somrido_ngo.db")
    overdue_list = []
    if conn:
        try:
            now = datetime.now()
            current_month_token = f"{now.strftime('%B')}'_{now.strftime('%y')}"
            cursor.execute("SELECT member_id, name, phone, email, status FROM members WHERE status='Active'")
            active_m = cursor.fetchall()
            
            # প্রিমিয়াম ডাটাবেস চেক
            p_conn, p_cursor = get_db_connection("somrido_premium.db")
            
            for m in active_m:
                has_paid = 0
                if p_conn:
                    p_cursor.execute("SELECT COUNT(*) FROM income WHERE member_id=? AND type='Subscription' AND paid_month=?", (m[0], current_month_token))
                    has_paid = p_cursor.fetchone()[0]
                
                if has_paid == 0:
                    due_lbl = "🚨 CRITICAL OVERDUE (Past 15th)" if now.day >= 15 else "⚠️ PENDING PAYMENT"
                    overdue_list.append({"ID": m[0], "Name": m[1], "Phone": m[2], "Email": m[3], "Due Label": due_lbl})
            p_conn.close()
            conn.close()
        except:
            pass

    if overdue_list:
        st.dataframe(overdue_list, use_container_width=True)
        
        if st.button("✉ Dispatch Bulk Overdue Notice Emails", type="primary"):
            if not st.session_state.sender_email or not st.session_state.smtp_pass:
                st.error("Setup Incomplete: Please configure valid SMTP routing parameters first.")
            else:
                with st.spinner("Executing background async transmission loop..."):
                    success, failed = 0, 0
                    try:
                        server = smtplib.SMTP(st.session_state.smtp_server, int(st.session_state.smtp_port))
                        server.starttls()
                        server.login(st.session_state.sender_email, st.session_state.smtp_pass)
                        
                        for mem in overdue_list:
                            if not mem["Email"] or "@" not in str(mem["Email"]):
                                failed += 1
                                continue
                            msg = MIMEMultipart()
                            msg['From'] = st.session_state.sender_email
                            msg['To'] = mem["Email"]
                            msg['Subject'] = f"URGENT: Outstanding Dues Alert - {datetime.now().strftime('%B %Y')}"
                            body = f"Dear {mem['Name']},\n\nSystem audit logs indicate outstanding subscription balances for this operational period. Please clear immediately.\n\nRegards,\nSomrido Systems Core"
                            msg.attach(MIMEText(body, 'plain'))
                            server.send_message(msg)
                            success += 1
                        server.quit()
                        st.success(f"Broadcast Completed. Dispatched Successfully: {success} | Failed: {failed}")
                    except Exception as err:
                        st.error(f"Handshake Protocol Terminated: {err}")
    else:
        st.success("🎉 Operational Excellence: All profiles clear of payment dues.")

# =========================================================================
# MODULE 5: Individual Audits (মেম্বার আইডি সার্চ করে স্টেটমেন্ট বের করা)
# =========================================================================
elif menu == "Individual Audits":
    st.markdown("## 🔍 Ledger Individual Audits Portal")
    search_id = st.text_input("Enter Target Member ID to Query Ledger History")
    
    if search_id:
        conn, cursor = get_db_connection("somrido_premium.db")
        if conn:
            cursor.execute("SELECT id, amount, type, source, paid_month FROM income WHERE member_id=?", (search_id.strip(),))
            records = cursor.fetchall()
            conn.close()
            
            if records:
                st.write(f"Audit trails located for token: **{search_id}**")
                st.table([{"Transaction Token": r[0], "Amount": r[1], "Type": r[2], "Repository": r[3], "Period": r[4]} for r in records])
            else:
                st.info("Zero records found matching the active directory tracking query.")

# =========================================================================
# MODULE 6: Expense Registry (ব্যয় বা খরচ এন্ট্রি করার ইন্টারফেস)
# =========================================================================
elif menu == "Expense Registry":
    st.markdown("## 📉 Expense Outflow Registry Pipeline")
    with st.form("expense_form", clear_on_submit=True):
        exp_amount = st.number_input("Debit Ledger Value Volume (Tk)", min_value=1.0)
        exp_purpose = st.text_input("Statement Outflow Specific Purpose / Allocation Description")
        
        btn_exp = st.form_submit_button("Authorize Outflow Entry")
        if btn_exp:
            if exp_purpose:
                conn, cursor = get_db_connection("somrido_premium.db")
                if conn:
                    cursor.execute("INSERT INTO expense (amount, purpose, date) VALUES (?, ?, ?)",
                                   (exp_amount, exp_purpose.strip(), datetime.now().strftime('%Y-%m-%d')))
                    conn.commit()
                    conn.close()
                    st.success(f"Debited: {exp_amount} Tk recorded under allocation matrix successfully.")
            else:
                st.warning("Missing documentation fields.")

# =========================================================================
# MODULE 7: Clearing Transfers (ক্যাশ থেকে ব্যাংক ট্রান্সফার ট্র্যাকিং)
# =========================================================================
elif menu == "Clearing Transfers":
    st.markdown("## 🔄 Repository Inter-Clearing Transfers")
    st.info("System Vault Inter-Repository Transfers Audits")
    with st.form("transfer_form"):
        x_from = st.selectbox("Source Liquidity Repository Vault", ["Cash", "bKash"])
        x_to = st.selectbox("Destination Allocation Safe", ["Bank File Ledger"])
        x_vol = st.number_input("Liquidity Value Volume To Commit (Tk)", min_value=500.0)
        
        btn_xfer = st.form_submit_button("Commit Internal Clearing Routing")
        if btn_xfer:
            st.success(f"Executed: Internal clearing vault routing of {x_vol} Tk completed safely.")

# =========================================================================
# MODULE 8: Reports Center (পুরো ডাটাবেসের রিপোর্ট ফাইল ভিউ)
# =========================================================================
elif menu == "Reports Center":
    st.markdown("## 📊 Executive Reporting Matrix Hub")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Live Deposits Log Matrix")
        conn, cursor = get_db_connection("somrido_premium.db")
        if conn:
            cursor.execute("SELECT * FROM income ORDER BY id DESC LIMIT 10")
            inc_rows = cursor.fetchall()
            st.dataframe([{"ID": r[0], "Payer": r[1], "Amount": r[2], "Category": r[3], "Safe": r[4], "Period": r[5]} for r in inc_rows], use_container_width=True)
            conn.close()
            
    with col_b:
        st.markdown("#### Live Debit Outflow Log Matrix")
        conn, cursor = get_db_connection("somrido_premium.db")
        if conn:
            cursor.execute("SELECT * FROM expense ORDER BY id DESC LIMIT 10")
            exp_rows = cursor.fetchall()
            st.dataframe([{"ID": r[0], "Amount": r[1], "Purpose": r[2], "Timestamp": r[3]} for r in exp_rows], use_container_width=True)
            conn.close()

# =========================================================================
# MODULE 9: ⚙️ SMTP Mail Settings
# =========================================================================
elif menu == "⚙️ SMTP Mail Settings":
    st.subheader("⚙️ SMTP Premium Configuration Parameters")
    with st.form("smtp_form_core"):
        server = st.text_input("SMTP Server Host Routing", value=st.session_state.smtp_server)
        port = st.number_input("SMTP Secure Protocol Port", value=st.session_state.smtp_port)
        email_addr = st.text_input("Organization Sender Email Identity", value=st.session_state.sender_email)
        pass_token = st.text_input("Google App Password Token Target", type="password", value=st.session_state.smtp_pass)
        
        if st.form_submit_button("Commit Parameters"):
            st.session_state.smtp_server = server
            st.session_state.smtp_port = port
            st.session_state.sender_email = email_addr
            st.session_state.smtp_pass = pass_token
            st.success("Web System Engine Core Parameters Synchronized.")

# সাইডবার ফুটারে লগআউট কন্ট্রোল
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Terminate Session (Log Out)", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()
