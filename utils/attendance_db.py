"""
Davomat tizimi uchun database moduli
"""
import sqlite3
from datetime import datetime, timedelta
import secrets
import os

try:
    from config import DATABASE_PATH
except ImportError:
    DATABASE_PATH = "data/main.db"


class AttendanceDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.create_attendance_tables()

    def create_attendance_tables(self):
        """Davomat uchun kerakli jadvallarni yaratish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Talabalar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                student_id TEXT UNIQUE,
                direction TEXT NOT NULL,
                group_name TEXT NOT NULL,
                phone TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Yo'nalishlar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS directions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Guruhlar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                direction TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, direction)
            )
        """)

        # Dars sessiyalari
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                subject TEXT NOT NULL,
                teacher_name TEXT,
                direction TEXT NOT NULL,
                group_name TEXT NOT NULL,
                session_date DATE NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TEXT,
                qr_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Davomat yozuvlari
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                status TEXT DEFAULT 'present',
                marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(user_id),
                FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id),
                UNIQUE(student_id, session_id)
            )
        """)

        # Feedback xabarlar jadvali (USER -> REKTOR)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT,
                user_username TEXT,
                message_type TEXT DEFAULT 'text',
                message_text TEXT,
                file_id TEXT,
                status TEXT DEFAULT 'pending',
                rector_reply TEXT,
                replied_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Default yo'nalishlar
        default_directions = [
            "Axborot texnologiyalari",
            "Iqtisodiyot",
            "Huquqshunoslik",
            "Pedagogika",
            "Psixologiya",
            "Filologiya"
        ]
        for direction in default_directions:
            cursor.execute(
                "INSERT OR IGNORE INTO directions (name) VALUES (?)",
                (direction,)
            )

        conn.commit()
        conn.close()

    # ==================== TALABALAR ====================

    def register_student(self, user_id: int, full_name: str, student_id: str,
                        direction: str, group_name: str, phone: str = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO students 
                (user_id, full_name, student_id, direction, group_name, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, full_name, student_id, direction, group_name, phone))
            conn.commit()
            return True
        except Exception as e:
            print(f"Xatolik: {e}")
            return False
        finally:
            conn.close()

    def get_student(self, user_id: int) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "user_id": row[0],
                "full_name": row[1],
                "student_id": row[2],
                "direction": row[3],
                "group_name": row[4],
                "phone": row[5],
                "registered_at": row[6]
            }
        return None

    def is_student_registered(self, user_id: int) -> bool:
        return self.get_student(user_id) is not None

    def get_students_by_group(self, direction: str, group_name: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM students 
            WHERE direction = ? AND group_name = ?
            ORDER BY full_name
        """, (direction, group_name))
        rows = cursor.fetchall()
        conn.close()

        return [{
            "user_id": row[0],
            "full_name": row[1],
            "student_id": row[2],
            "direction": row[3],
            "group_name": row[4]
        } for row in rows]

    # ==================== YO'NALISHLAR VA GURUHLAR ====================

    def get_all_directions(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM directions ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def add_direction(self, name: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO directions (name) VALUES (?)", (name,))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def get_groups_by_direction(self, direction: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM groups WHERE direction = ? ORDER BY name",
            (direction,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def add_group(self, name: str, direction: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO groups (name, direction) VALUES (?, ?)",
                (name, direction)
            )
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    # ==================== DARS SESSIYALARI ====================

    def create_session(self, subject: str, direction: str, group_name: str,
                      teacher_name: str = None, duration_minutes: int = 90,
                      created_by: int = None) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now()
        session_id = f"S{now.strftime('%Y%m%d%H%M%S')}{secrets.token_hex(3)}"
        qr_token = secrets.token_urlsafe(16)
        expires_at = now + timedelta(minutes=duration_minutes)

        days = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba",
                "Juma", "Shanba", "Yakshanba"]
        day_of_week = days[now.weekday()]

        cursor.execute("""
            INSERT INTO attendance_sessions 
            (session_id, subject, teacher_name, direction, group_name,
             session_date, day_of_week, start_time, qr_token, expires_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, subject, teacher_name, direction, group_name,
            now.date().isoformat(), day_of_week, now.strftime("%H:%M"),
            qr_token, expires_at, created_by
        ))
        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "qr_token": qr_token,
            "subject": subject,
            "direction": direction,
            "group_name": group_name,
            "day_of_week": day_of_week,
            "expires_at": expires_at.isoformat()
        }

    def get_session_by_token(self, qr_token: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance_sessions WHERE qr_token = ?", (qr_token,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "session_id": row[1],
                "subject": row[2],
                "teacher_name": row[3],
                "direction": row[4],
                "group_name": row[5],
                "session_date": row[6],
                "day_of_week": row[7],
                "start_time": row[8],
                "qr_token": row[9],
                "expires_at": row[10],
                "is_active": row[11],
                "created_by": row[12]
            }
        return None

    def get_session_by_id(self, session_id: str) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "session_id": row[1],
                "subject": row[2],
                "teacher_name": row[3],
                "direction": row[4],
                "group_name": row[5],
                "session_date": row[6],
                "day_of_week": row[7],
                "start_time": row[8],
                "qr_token": row[9],
                "expires_at": row[10],
                "is_active": row[11],
                "created_by": row[12]
            }
        return None

    def get_active_sessions(self, direction: str = None, group_name: str = None) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM attendance_sessions WHERE is_active = 1"
        params = []

        if direction:
            query += " AND direction = ?"
            params.append(direction)
        if group_name:
            query += " AND group_name = ?"
            params.append(group_name)

        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [{
            "session_id": row[1],
            "subject": row[2],
            "direction": row[4],
            "group_name": row[5],
            "session_date": row[6],
            "day_of_week": row[7],
            "qr_token": row[9]
        } for row in rows]

    def close_session(self, session_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE attendance_sessions SET is_active = 0 WHERE session_id = ?",
            (session_id,)
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    # ==================== DAVOMAT ====================

    def mark_attendance(self, user_id: int, qr_token: str) -> dict:
        session = self.get_session_by_token(qr_token)

        if not session:
            return {"success": False, "error": "Sessiya topilmadi"}

        if not session["is_active"]:
            return {"success": False, "error": "Sessiya yopilgan"}

        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            return {"success": False, "error": "QR kod muddati tugagan"}

        student = self.get_student(user_id)
        if not student:
            return {"success": False, "error": "not_registered"}

        if student["direction"] != session["direction"]:
            return {"success": False, "error": "Bu dars sizning yo'nalishingiz uchun emas"}

        if student["group_name"] != session["group_name"]:
            return {"success": False, "error": "Bu dars sizning guruhingiz uchun emas"}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM attendance_records 
            WHERE student_id = ? AND session_id = ?
        """, (user_id, session["session_id"]))

        if cursor.fetchone():
            conn.close()
            return {"success": False, "error": "Siz allaqachon davomat qildingiz"}

        cursor.execute("""
            INSERT INTO attendance_records (student_id, session_id, status)
            VALUES (?, ?, 'present')
        """, (user_id, session["session_id"]))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "subject": session["subject"],
            "session_date": session["session_date"],
            "day_of_week": session["day_of_week"]
        }

    def get_session_attendance(self, session_id: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.full_name, s.student_id, ar.status, ar.marked_at
            FROM attendance_records ar
            JOIN students s ON ar.student_id = s.user_id
            WHERE ar.session_id = ?
            ORDER BY s.full_name
        """, (session_id,))
        rows = cursor.fetchall()
        conn.close()

        return [{
            "full_name": row[0],
            "student_id": row[1],
            "status": row[2],
            "marked_at": row[3]
        } for row in rows]

    def get_student_attendance(self, user_id: int, start_date: str = None,
                               end_date: str = None) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT ses.subject, ses.session_date, ses.day_of_week,
                   COALESCE(ar.status, 'absent') as status
            FROM attendance_sessions ses
            LEFT JOIN attendance_records ar ON ses.session_id = ar.session_id 
                AND ar.student_id = ?
            JOIN students st ON st.direction = ses.direction 
                AND st.group_name = ses.group_name
            WHERE st.user_id = ?
        """
        params = [user_id, user_id]

        if start_date:
            query += " AND ses.session_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND ses.session_date <= ?"
            params.append(end_date)

        query += " ORDER BY ses.session_date DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [{
            "subject": row[0],
            "date": row[1],
            "day": row[2],
            "status": row[3]
        } for row in rows]

    # ==================== HISOBOTLAR ====================

    def get_weekly_report(self, direction: str, group_name: str,
                         week_start: str = None) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if not week_start:
            today = datetime.now()
            week_start = (today - timedelta(days=today.weekday())).date().isoformat()

        week_end = (datetime.fromisoformat(week_start) + timedelta(days=6)).date().isoformat()

        students = self.get_students_by_group(direction, group_name)

        cursor.execute("""
            SELECT session_id, subject, session_date, day_of_week
            FROM attendance_sessions
            WHERE direction = ? AND group_name = ?
            AND session_date BETWEEN ? AND ?
            ORDER BY session_date
        """, (direction, group_name, week_start, week_end))
        sessions = cursor.fetchall()

        report = {
            "direction": direction,
            "group_name": group_name,
            "week_start": week_start,
            "week_end": week_end,
            "sessions": [{
                "session_id": s[0],
                "subject": s[1],
                "date": s[2],
                "day": s[3]
            } for s in sessions],
            "students": []
        }

        for student in students:
            student_data = {
                "full_name": student["full_name"],
                "student_id": student["student_id"],
                "attendance": {}
            }

            for session in sessions:
                cursor.execute("""
                    SELECT status FROM attendance_records
                    WHERE student_id = ? AND session_id = ?
                """, (student["user_id"], session[0]))
                result = cursor.fetchone()
                student_data["attendance"][session[0]] = result[0] if result else "absent"

            report["students"].append(student_data)

        conn.close()
        return report

    def get_attendance_stats(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance_sessions")
        total_sessions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE status = 'present'")
        total_present = cursor.fetchone()[0]

        conn.close()

        return {
            "total_students": total_students,
            "total_sessions": total_sessions,
            "total_present": total_present
        }

    # ==================== FEEDBACK XABARLAR (USER -> REKTOR) ====================

    def save_feedback(self, user_id: int, user_name: str, user_username: str,
                      message_type: str, message_text: str = None, file_id: str = None) -> int:
        """Feedback xabarni saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback_messages 
            (user_id, user_name, user_username, message_type, message_text, file_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user_name, user_username, message_type, message_text, file_id))
        conn.commit()
        msg_id = cursor.lastrowid
        conn.close()
        return msg_id

    def get_pending_feedbacks(self) -> list:
        """Javob berilmagan xabarlar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM feedback_messages 
            WHERE status = 'pending'
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [{
            "id": row[0],
            "user_id": row[1],
            "user_name": row[2],
            "user_username": row[3],
            "message_type": row[4],
            "message_text": row[5],
            "file_id": row[6],
            "status": row[7],
            "rector_reply": row[8],
            "replied_at": row[9],
            "created_at": row[10]
        } for row in rows]

    def get_all_feedbacks(self, limit: int = 50) -> list:
        """Barcha xabarlar (javob berilgan va berilmagan)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM feedback_messages 
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [{
            "id": row[0],
            "user_id": row[1],
            "user_name": row[2],
            "user_username": row[3],
            "message_type": row[4],
            "message_text": row[5],
            "file_id": row[6],
            "status": row[7],
            "rector_reply": row[8],
            "replied_at": row[9],
            "created_at": row[10]
        } for row in rows]

    def get_feedback_by_id(self, msg_id: int) -> dict:
        """ID bo'yicha xabar olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback_messages WHERE id = ?", (msg_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "user_name": row[2],
                "user_username": row[3],
                "message_type": row[4],
                "message_text": row[5],
                "file_id": row[6],
                "status": row[7],
                "rector_reply": row[8],
                "replied_at": row[9],
                "created_at": row[10]
            }
        return None

    def reply_feedback(self, msg_id: int, reply_text: str) -> bool:
        """Xabarga javob berish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE feedback_messages 
            SET status = 'replied', rector_reply = ?, replied_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (reply_text, msg_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    def get_user_feedbacks(self, user_id: int) -> list:
        """User ning xabarlari"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM feedback_messages 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        return [{
            "id": row[0],
            "message_text": row[5],
            "status": row[7],
            "rector_reply": row[8],
            "replied_at": row[9],
            "created_at": row[10]
        } for row in rows]

    def count_pending_feedbacks(self) -> int:
        """Javob kutayotgan xabarlar soni"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedback_messages WHERE status = 'pending'")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_feedback_stats(self) -> dict:
        """Feedback statistikasi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM feedback_messages")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedback_messages WHERE status = 'pending'")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedback_messages WHERE status = 'replied'")
        replied = cursor.fetchone()[0]

        conn.close()

        return {
            "total": total,
            "pending": pending,
            "replied": replied
        }