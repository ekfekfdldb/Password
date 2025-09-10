# app/ui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from app.store import Vault
from app.utils import json_prompt_defaults, CLIPBOARD_CLEAR_SEC, AUTO_LOCK_MIN
from app.generator import generate, GenOptions

def setup_theme():
    style = ttk.Style()
    try: style.theme_use("clam")
    except: pass

    primary = "#C7D4E4"; bg = "#f7f9fc"; fg = "#333"

    style.configure("TFrame", background=bg)
    style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10), cursor="arrow")
    style.configure("TCheckbutton", cursor="arrow")
    style.configure("TButton", background=primary, foreground="#000000",
                    padding=6, font=("Segoe UI", 10, "bold"), cursor="arrow")
    style.map("TButton", background=[("active", "#357ABD")])

    style.configure("Treeview", background="white", foreground=fg,
                    fieldbackground="white", rowheight=28, cursor="arrow")
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    background="#e0e6ef", cursor="arrow")
    style.map("Treeview.Heading", background=[])

    # 카드
    style.configure("Card.TFrame", background="white", relief="groove", borderwidth=1)
    style.configure("Muted.TLabel", background="white", foreground="#667085", font=("Segoe UI", 9))
    style.configure("CardTitle.TLabel", background="white", foreground="#1F2937", font=("Segoe UI", 14, "bold"))
    style.configure("CardButton.TButton", padding=6, font=("Segoe UI", 10), cursor="arrow")


# ----------------- 로그인/초기 생성 -----------------
class LoginFrame(ttk.Frame):
    def __init__(self, master, vault, on_unlocked):
        super().__init__(master)
        self.vault = vault
        self.on_unlocked = on_unlocked

        setup_theme()

        # 루트 레이아웃
        self.grid(row=0, column=0, sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # 그림자/카드
        shadow = ttk.Frame(self, style="TFrame")
        shadow.place(relx=0.5, rely=0.5, anchor="center", x=3, y=3)
        card = ttk.Frame(self, style="Card.TFrame", padding=18)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # 제목/부제
        header = ttk.Frame(card, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text="접속을 위해 잠금을 해제하세요", style="CardTitle.TLabel",anchor="center")
        title.grid(row=0, column=0, sticky="ew")

        subtitle = ttk.Label(card, text="마스터 비밀번호는 분실 시 복구할 수 없습니다.", style="Muted.TLabel",anchor="center")
        subtitle.grid(row=1, column=0, sticky="ew", pady=(6, 12))

        # 입력영역
        form = ttk.Frame(card, style="Card.TFrame")
        form.grid(row=2, column=0, sticky="ew")
        form.columnconfigure(0, weight=1)

        CARD_BG = "white"

        tk.Label(form, text="마스터 비밀번호", bg=CARD_BG, fg="#333", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="ew", pady=(0, 0))

        # 👁/커스텀 스타일 없이 기본 Entry만 사용
        self.entry1 = ttk.Entry(form, show="•", width=34)
        self.entry1.grid(row=1, column=0, sticky="ew")
        self.entry1.focus_set()

        # 액션 버튼
        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(0, weight=1)
        submit = ttk.Button(actions, text="확인", style="CardButton.TButton", command=self._ok)
        submit.grid(row=0, column=0, sticky="ew")

        # Enter로 제출
        self.bind_all("<Return>", lambda e: self._ok())

        # 도움말 버튼: 창 우상단(X 아래) 고정
        self.help_btn = tk.Button(
            self.master,
            text="?",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            fg="white",
            bg="#81A4CF",
            activebackground="#6d95c7",
            cursor="hand2",
            command=self._show_help,
            bd=0,
            highlightthickness=0,
            padx=5,  # 좌우 여백
            pady=0   # 상하 여백
        )

        # 첫 배치(윈도우가 그려진 뒤)
        self.after(0, self._place_help_btn)
        # 리사이즈 때 재배치 (안전 바인딩)
        self._cfg_bind_id = self.master.bind("<Configure>", self._place_help_btn, add="+")
        # 프레임 파괴 시 정리
        self.bind("<Destroy>", self._cleanup_help_btn, add="+")

    # 우상단 위치 고정
    def _place_help_btn(self, *args):
        if getattr(self, "help_btn", None) and self.help_btn.winfo_exists():
            w = self.master.winfo_width() or self.master.winfo_reqwidth()
            x = max(0, w - 34)  # 오른쪽 여백 감안(버튼 폭 포함)
            self.help_btn.place(x=x, y=8)

    # 바인딩/버튼 정리
    def _cleanup_help_btn(self, *args):
        try:
            if hasattr(self, "_cfg_bind_id"):
                self.master.unbind("<Configure>", self._cfg_bind_id)
        except Exception:
            pass
        try:
            if getattr(self, "help_btn", None) and self.help_btn.winfo_exists():
                self.help_btn.destroy()
        except Exception:
            pass

    def _show_help(self):
        tips = (
            "• 마스터 비밀번호는 분실 시 복구할 수 없습니다.\n"
            "• 12자 이상 복잡한 비밀번호 권장.\n"
            "• 앱은 로컬에서만 동작합니다.\n"
            "• 일정 시간 미사용 시 자동 잠금.\n"
            "• 복사한 비밀번호는 잠시 후 클립보드에서 자동 삭제됩니다."
        )
        messagebox.showinfo("도움말", tips, parent=self)

    def _ok(self):
        pw = self.entry1.get().strip()
        if not pw:
            messagebox.showerror("오류", "비밀번호를 입력하세요.", parent=self)
            return
        if not self.vault.unlock(pw):
            messagebox.showerror("오류", "잠금 해제 실패(비밀번호 불일치).", parent=self)
            return
        # 전환 전에 도움말 버튼 정리
        self._cleanup_help_btn()
        self.on_unlocked()


# ----------------- 속성 보기 다이얼로그 -----------------
class DetailDialog(tk.Toplevel):
    """속성 창 (비밀번호 보기/숨기기 버튼을 입력칸 내부에 표시, 전체 폭 축소)"""
    def __init__(self, master, vault: Vault, entry_id: int):
        super().__init__(master)
        self.vault = vault
        self.entry_id = entry_id
        self.title("속성")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._last_clip = None

        display, fields = self.vault.get_entry(entry_id)
        username = fields.get("username", "")
        password = fields.get("password", "")
        notes    = fields.get("notes", "")

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        # 제목
        title = ttk.Label(frm, text=display, font=("Segoe UI", 12, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        ENTRY_W = 32
        BTN_W   = 8

        # 사용자명
        ttk.Label(frm, text="사용자명").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=(0, 6))
        self.user_var = tk.StringVar(value=username)
        user_ent = ttk.Entry(frm, textvariable=self.user_var, width=ENTRY_W, state="readonly")
        user_ent.grid(row=1, column=1, sticky="we", pady=(0, 6))
        ttk.Button(frm, text="복사", width=BTN_W,
                   command=lambda: self._copy(self.user_var.get(), "사용자명")).grid(row=1, column=2, sticky="w", pady=(0, 6))

        # 비밀번호
        ttk.Label(frm, text="비밀번호").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=(0, 6))
        pw_frame = ttk.Frame(frm)
        pw_frame.grid(row=2, column=1, sticky="we", pady=(0, 6))
        pw_frame.columnconfigure(0, weight=1)

        self.pw_var = tk.StringVar(value=password)
        self.pw_shown = False
        self.pw_entry = ttk.Entry(pw_frame, textvariable=self.pw_var, width=ENTRY_W, show="•")
        self.pw_entry.grid(row=0, column=0, sticky="we")

        # 보기/숨기기 버튼 (엔트리 내부 오른쪽에 배치)
        btn_show = tk.Button(pw_frame, text="👁", width=2, relief="flat", cursor="hand2",
                             command=self._toggle_pw)
        btn_show.grid(row=0, column=0, sticky="e", padx=(0, 2))

        # 복사 버튼
        ttk.Button(frm, text="복사", width=BTN_W,
                   command=lambda: self._copy(self.pw_var.get(), "비밀번호")).grid(row=2, column=2, sticky="w", pady=(0, 6))

        # 메모
        ttk.Label(frm, text="메모").grid(row=3, column=0, sticky="ne", padx=(0, 8), pady=(0, 6))
        self.notes = tk.Text(frm, width=ENTRY_W+2, height=6)
        self.notes.insert("1.0", notes)
        self.notes.configure(state="disabled")
        self.notes.grid(row=3, column=1, sticky="we", pady=(0, 6))
        ttk.Label(frm, text="").grid(row=3, column=2, sticky="w")

        # 닫기 버튼
        ttk.Button(frm, text="닫기", command=self.destroy, width=BTN_W).grid(
            row=4, column=2, sticky="e", pady=(10, 0)
        )

        # 컬럼 리사이즈
        frm.columnconfigure(0, weight=0)
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=0)

        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        self._center_to_parent()

    def _center_to_parent(self):
        try:
            px = self.master.winfo_rootx()
            py = self.master.winfo_rooty()
            pw = self.master.winfo_width()
            ph = self.master.winfo_height()
            w  = self.winfo_reqwidth()
            h  = self.winfo_reqheight()
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"+{max(0,x)}+{max(0,y)}")
        except Exception:
            pass

    def _toggle_pw(self):
        self.pw_shown = not self.pw_shown
        self.pw_entry.configure(show="" if self.pw_shown else "•")

    def _copy(self, text: str, label: str):
        self.clipboard_clear()
        self.clipboard_append(text or "")
        self._last_clip = text or ""
        messagebox.showinfo("복사됨", f"{label}을(를) 클립보드에 복사했습니다.\n{CLIPBOARD_CLEAR_SEC}초 후 자동 삭제됩니다.")
        self.after(CLIPBOARD_CLEAR_SEC * 1000, self._clear_clip_if_same)

    def _clear_clip_if_same(self):
        try:
            cur = self.clipboard_get()
        except Exception:
            cur = None
        if cur == self._last_clip:
            self.clipboard_clear()
            self._last_clip = None


# ----------------- 메인 윈도우 -----------------
class MainFrame(ttk.Frame):
    def __init__(self, master, vault, switch_to_login):
        super().__init__(master, padding=12)
        self.vault = vault
        self.switch_to_login = switch_to_login
        setup_theme()
        self._idle_after_id = None

        # 테마/스타일
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("TButton", padding=6)
        style.configure("Treeview", rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.map("TButton", foreground=[("active", "!disabled", "black")])

        # 메뉴바
        menubar = tk.Menu(self.master)
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label="잠금", command=self._lock_now)
        m_file.add_separator()
        m_file.add_command(label="종료", command=self.master.destroy)
        menubar.add_cascade(label="파일", menu=m_file)


        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label="정보", command=self._about)
        menubar.add_cascade(label="도움말", menu=m_help)
        self.master.config(menu=menubar)

        # 상단: 좌 버튼 / 우 검색
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew")
        left_btns = ttk.Frame(top); left_btns.pack(side="left")
        ttk.Button(left_btns, text="추가", command=self.add_entry).pack(side="left")
        ttk.Button(left_btns, text="수정", command=self.edit_entry).pack(side="left", padx=(6,0))
        ttk.Button(left_btns, text="삭제", command=self.delete_entry).pack(side="left", padx=(6,0))

        right_search = ttk.Frame(top); right_search.pack(side="right")
        ttk.Label(right_search, text="검색").pack(side="left", padx=(0,6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(right_search, textvariable=self.search_var, width=26).pack(side="left")

        # 리스트
        self.tree = ttk.Treeview(self, columns=("display","updated"), show="headings", height=16)
        self.tree.heading("display", text="이름")
        self.tree.heading("updated", text="업데이트")
        self.tree.column("display", width=380)
        self.tree.column("updated", width=220, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8,0))

        scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=1, column=1, sticky="ns")
        self.tree.tag_configure("oddrow", background="#f7f7f9")
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.bind("<Double-1>", lambda e: self.open_detail())

        self.rowconfigure(1, weight=1); self.columnconfigure(0, weight=1)
        self.refresh()

        for seq in ("<KeyPress>", "<Button-1>", "<Motion>", "<MouseWheel>"):
            self.master.bind_all(seq, self._reset_idle_timer, add="+")
        self._reset_idle_timer()

    def _lock_now(self):
        self.vault.lock()
        self.switch_to_login()

    # ----- 목록/검색 -----
    def refresh(self):
        keyword = (self.search_var.get() or "").strip()
        for i in self.tree.get_children(): self.tree.delete(i)
        rows = self.vault.search_entries(keyword) if keyword else self.vault.list_entries()
        for idx, row in enumerate(rows):
            tag = "oddrow" if idx % 2 else "evenrow"
            self.tree.insert("", "end", iid=str(row["id"]), values=(row["display"], row["updated_at"]), tags=(tag,))

    def _select_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("알림", "항목을 선택하세요.")
            return None
        return int(sel[0])

    # ----- CRUD -----
    def add_entry(self):
        display = simpledialog.askstring("항목 이름", "표시할 이름(예: 사이트/계정명):", parent=self)
        if not display: return
        fields = json_prompt_defaults()
        fields["username"] = simpledialog.askstring("사용자명", "사용자명:", parent=self) or ""
        fields["password"] = simpledialog.askstring("비밀번호", "비밀번호:", parent=self, show="*") or ""
        fields["url"] = simpledialog.askstring("URL", "로그인 URL(선택):", parent=self) or ""
        fields["notes"] = simpledialog.askstring("메모", "메모(선택):", parent=self) or ""
        self.vault.add_entry(display, fields); self.refresh()

    def edit_entry(self):
        entry_id = self._select_id()
        if entry_id is None: return
        display, fields = self.vault.get_entry(entry_id)
        new_display = simpledialog.askstring("이름", "표시 이름:", initialvalue=display, parent=self)
        if new_display is None: return
        username = simpledialog.askstring("사용자명", "사용자명:", initialvalue=fields.get("username",""), parent=self) or ""
        password = simpledialog.askstring("비밀번호", "비밀번호:", initialvalue=fields.get("password",""), parent=self, show="*") or ""
        url = simpledialog.askstring("URL", "URL:", initialvalue=fields.get("url",""), parent=self) or ""
        notes = simpledialog.askstring("메모", "메모:", initialvalue=fields.get("notes",""), parent=self) or ""
        self.vault.update_entry(entry_id, new_display, {
            "username": username, "password": password, "url": url, "notes": notes
        })
        self.refresh()

    def delete_entry(self):
        entry_id = self._select_id()
        if entry_id is None: return
        if messagebox.askyesno("삭제", "정말 삭제할까요?"):
            self.vault.delete_entry(entry_id); self.refresh()

    def open_detail(self):
        entry_id = self._select_id()
        if entry_id is None: return
        DetailDialog(self.master, self.vault, entry_id)

    # ----- 자동 잠금 -----
    def _reset_idle_timer(self, *_):
        if self._idle_after_id:
            self.after_cancel(self._idle_after_id)
        self._idle_after_id = self.after(int(AUTO_LOCK_MIN * 60 * 1000), self._lock_now)

    # ----- 정보 -----
    def _about(self):
        from .version import __app_name__, __version__, __copyright__
        messagebox.showinfo("정보", f"{__app_name__} {__version__}\n{__copyright__}")
