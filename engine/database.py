"""
engine/database.py
================================================================================
Quản lý cơ sở dữ liệu bền vững (SQLite WAL Mode):
- Lưu trữ Products, Jobs Queue, Artifacts, Journal Events
- Tiếp tục chính xác sau khi khởi động lại máy hoặc gặp lỗi
- Khóa job với cơ chế lease để tránh xử lý trùng lặp
================================================================================
"""

import sqlite3
import json
import datetime
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from config.settings import DB_PATH

@contextmanager
def get_connection():
    """Mở kết nối SQLite với cấu hình WAL Mode an toàn và tự động đóng khi hoàn tất."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Khởi tạo toàn bộ các bảng dữ liệu."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Bảng Products (Thông tin sản phẩm affiliate)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                price_vnd REAL NOT NULL,
                commission_rate REAL NOT NULL,
                commission_vnd REAL NOT NULL,
                evidence_grade TEXT DEFAULT 'B',
                claims_json TEXT,
                status TEXT DEFAULT 'DISCOVERED',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)

        # 2. Bảng Jobs (Hàng đợi công việc bền vững)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                job_type TEXT NOT NULL,
                status TEXT DEFAULT 'QUEUED',
                lease_token TEXT,
                lease_expires_at TEXT,
                attempt_count INTEGER DEFAULT 0,
                payload_json TEXT,
                result_json TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_sku ON jobs(sku);")

        # 3. Bảng Artifacts (Các sản phẩm đầu ra trung gian & hoàn chỉnh)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                file_path TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
            );
        """)

        # 4. Bảng Journal Events (Nhật ký kiểm toán không thể xóa)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT,
                event_type TEXT NOT NULL,
                details_json TEXT,
                timestamp TEXT NOT NULL
            );
        """)

        # 5. Bảng Video Metrics & Creator Analytics (Thước đo phễu chuyển đổi TikTok Shop)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                sku TEXT NOT NULL,
                angle_id TEXT,
                angle_name TEXT,
                views INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                orders INTEGER DEFAULT 0,
                ctr REAL DEFAULT 0.0,
                cvr REAL DEFAULT 0.0,
                gmv_vnd REAL DEFAULT 0.0,
                commission_vnd REAL DEFAULT 0.0,
                production_cost_vnd REAL DEFAULT 0.0,
                rpm_commission REAL DEFAULT 0.0,
                diagnosis_state TEXT DEFAULT 'LOW_VIEWS',
                decision TEXT DEFAULT 'OBSERVING',
                notes TEXT,
                platform TEXT DEFAULT 'TIKTOK_SHOP',
                posted_at TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vm_sku ON video_metrics(sku);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vm_diagnosis ON video_metrics(diagnosis_state);")

        # 6. Bảng Growth Experiments (Quản lý các giả thuyết & chu kỳ thử nghiệm có kiểm soát)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS growth_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                hypothesis TEXT NOT NULL,
                target_profit_vnd REAL DEFAULT 0.0,
                angles_planned INTEGER DEFAULT 3,
                angles_tested INTEGER DEFAULT 0,
                status TEXT DEFAULT 'TESTING',
                decision TEXT DEFAULT 'OBSERVING',
                learning_notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ge_sku ON growth_experiments(sku);")

        # 7. Bảng Market Niches (Nghiên cứu & xếp hạng ngách thị trường)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_niches (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                demand_score REAL DEFAULT 0.0,
                footage_score REAL DEFAULT 0.0,
                economics_score REAL DEFAULT 0.0,
                competition_score REAL DEFAULT 0.0,
                quality_score REAL DEFAULT 0.0,
                scalability_score REAL DEFAULT 0.0,
                total_score REAL DEFAULT 0.0,
                confidence_grade TEXT DEFAULT 'MEDIUM',
                rank INTEGER DEFAULT 0,
                selected_status TEXT DEFAULT 'CANDIDATE',
                reasoning TEXT,
                risks TEXT,
                updated_at TEXT NOT NULL
            );
        """)

        # 8. Bảng Candidate Products (Sản phẩm đại diện từng ngách)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidate_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                niche_id TEXT NOT NULL,
                title TEXT NOT NULL,
                platform TEXT NOT NULL,
                url TEXT,
                price_vnd REAL DEFAULT 0.0,
                commission_rate REAL DEFAULT 0.0,
                commission_vnd REAL DEFAULT 0.0,
                rating REAL DEFAULT 0.0,
                reviews_count INTEGER DEFAULT 0,
                demand_signal TEXT,
                competition_signal TEXT,
                footage_source TEXT,
                permission_tier TEXT DEFAULT 'unknown',
                risk_notes TEXT,
                confidence_grade TEXT DEFAULT 'MEDIUM',
                created_at TEXT NOT NULL,
                FOREIGN KEY (niche_id) REFERENCES market_niches(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cp_niche ON candidate_products(niche_id);")

        # 9. Bảng Evidence Records (Sổ đăng ký bằng chứng kiểm tra được)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value TEXT NOT NULL,
                source TEXT NOT NULL,
                observation_time TEXT NOT NULL,
                confidence TEXT NOT NULL,
                notes TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_er_entity ON evidence_records(entity_type, entity_id);")

        # 10. Bảng Audience Personas (Hồ sơ chân dung khán giả & nỗi đau thực tế)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audience_personas (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                archetype TEXT NOT NULL,
                core_demographic TEXT,
                lifestyle_context TEXT,
                primary_pains_json TEXT,
                reasons_to_follow TEXT,
                free_solutions_json TEXT,
                monetization_opportunities_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)

        # 11. Bảng Editorial Plan (Kế hoạch nội dung cân bằng: 50% Giá trị, 30% Niềm tin, 20% Bán hàng)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS editorial_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_id TEXT NOT NULL,
                video_number INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                title TEXT NOT NULL,
                hook_angle TEXT NOT NULL,
                core_pain_point TEXT NOT NULL,
                solution_type TEXT NOT NULL,
                has_affiliate_link INTEGER DEFAULT 0,
                linked_sku TEXT,
                target_kpi_pillar TEXT NOT NULL,
                primary_metric TEXT NOT NULL,
                faceless_visual_style TEXT NOT NULL,
                status TEXT DEFAULT 'PLANNED',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (persona_id) REFERENCES audience_personas(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ep_persona ON editorial_plan(persona_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ep_type ON editorial_plan(content_type);")

        conn.commit()

# Khởi tạo schema khi module được load
init_db()

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions: Products
# ─────────────────────────────────────────────────────────────────────────────

def upsert_product(
    sku: str,
    title: str,
    price_vnd: float,
    commission_rate: float,
    category: str = "Gia dụng",
    evidence_grade: str = "B",
    claims: Optional[Dict[str, Any]] = None,
    status: str = "DISCOVERED"
) -> Dict[str, Any]:
    """Tạo mới hoặc cập nhật sản phẩm."""
    now = datetime.datetime.now().isoformat()
    comm_vnd = price_vnd * commission_rate
    claims_str = json.dumps(claims or {}, ensure_ascii=False)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (sku, title, category, price_vnd, commission_rate, commission_vnd, evidence_grade, claims_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sku) DO UPDATE SET
                title=excluded.title,
                category=excluded.category,
                price_vnd=excluded.price_vnd,
                commission_rate=excluded.commission_rate,
                commission_vnd=excluded.commission_vnd,
                evidence_grade=excluded.evidence_grade,
                claims_json=excluded.claims_json,
                status=excluded.status,
                updated_at=excluded.updated_at
        """, (sku, title, category, price_vnd, commission_rate, comm_vnd, evidence_grade, claims_str, status, now, now))
        conn.commit()

    log_event(sku, "PRODUCT_UPSERTED", {"title": title, "price_vnd": price_vnd, "commission_vnd": comm_vnd})
    return get_product(sku)

def get_product(sku: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin chi tiết của một sản phẩm."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["claims"] = json.loads(res["claims_json"]) if res["claims_json"] else {}
        return res

def list_products(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Liệt kê danh sách sản phẩm."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM products WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions: Journal Events
# ─────────────────────────────────────────────────────────────────────────────

def log_event(sku: Optional[str], event_type: str, details: Optional[Dict[str, Any]] = None):
    """Ghi nhật ký sự kiện kiểm toán."""
    now = datetime.datetime.now().isoformat()
    det_str = json.dumps(details or {}, ensure_ascii=False)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO journal_events (sku, event_type, details_json, timestamp)
            VALUES (?, ?, ?, ?)
        """, (sku, event_type, det_str, now))
        conn.commit()

def get_recent_events(limit: int = 50) -> List[Dict[str, Any]]:
    """Lấy các sự kiện gần nhất."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM journal_events ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions: Artifacts
# ─────────────────────────────────────────────────────────────────────────────

def record_artifact(sku: str, artifact_type: str, file_path: str, metadata: Optional[Dict[str, Any]] = None, version: int = 1):
    """Ghi nhận một file kết quả (artifact) vào database."""
    now = datetime.datetime.now().isoformat()
    meta_str = json.dumps(metadata or {}, ensure_ascii=False)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO artifacts (sku, artifact_type, version, file_path, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sku, artifact_type, version, file_path, meta_str, now))
        conn.commit()
    log_event(sku, "ARTIFACT_CREATED", {"type": artifact_type, "file": file_path})

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions: Video Metrics & Growth Intelligence
# ─────────────────────────────────────────────────────────────────────────────

def upsert_video_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Lưu hoặc cập nhật số liệu hiệu suất của một video TikTok Shop/Shopee."""
    now = datetime.datetime.now().isoformat()
    video_id = data["video_id"]
    sku = data["sku"]
    views = int(data.get("views", 0))
    clicks = int(data.get("clicks", 0))
    orders = int(data.get("orders", 0))
    gmv_vnd = float(data.get("gmv_vnd", 0.0))
    commission_vnd = float(data.get("commission_vnd", 0.0))
    production_cost_vnd = float(data.get("production_cost_vnd", 0.0))
    
    # Tính CTR, CVR, RPM
    ctr = (clicks / views) if views > 0 else 0.0
    cvr = (orders / clicks) if clicks > 0 else 0.0
    rpm_commission = (commission_vnd / views * 1000.0) if views > 0 else 0.0

    diagnosis_state = data.get("diagnosis_state", "LOW_VIEWS")
    decision = data.get("decision", "OBSERVING")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO video_metrics (
                video_id, sku, angle_id, angle_name, views, clicks, orders,
                ctr, cvr, gmv_vnd, commission_vnd, production_cost_vnd, rpm_commission,
                diagnosis_state, decision, notes, platform, posted_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                views = excluded.views,
                clicks = excluded.clicks,
                orders = excluded.orders,
                ctr = excluded.ctr,
                cvr = excluded.cvr,
                gmv_vnd = excluded.gmv_vnd,
                commission_vnd = excluded.commission_vnd,
                production_cost_vnd = excluded.production_cost_vnd,
                rpm_commission = excluded.rpm_commission,
                diagnosis_state = excluded.diagnosis_state,
                decision = excluded.decision,
                notes = excluded.notes,
                updated_at = excluded.updated_at;
        """, (
            video_id, sku, data.get("angle_id"), data.get("angle_name"),
            views, clicks, orders, ctr, cvr, gmv_vnd, commission_vnd,
            production_cost_vnd, rpm_commission, diagnosis_state, decision,
            data.get("notes"), data.get("platform", "TIKTOK_SHOP"),
            data.get("posted_at"), now
        ))
        conn.commit()

    log_event(sku, "VIDEO_METRICS_UPDATED", {
        "video_id": video_id,
        "views": views,
        "clicks": clicks,
        "orders": orders,
        "commission_vnd": commission_vnd,
        "diagnosis_state": diagnosis_state
    })
    return get_video_metrics(video_id=video_id)

def get_video_metrics(video_id: Optional[str] = None, sku: Optional[str] = None) -> Any:
    """Lấy số liệu video theo video_id hoặc toàn bộ danh sách theo SKU."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if video_id:
            cursor.execute("SELECT * FROM video_metrics WHERE video_id = ?", (video_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        elif sku:
            cursor.execute("SELECT * FROM video_metrics WHERE sku = ? ORDER BY posted_at DESC, id DESC", (sku,))
            return [dict(r) for r in cursor.fetchall()]
        else:
            cursor.execute("SELECT * FROM video_metrics ORDER BY id DESC")
            return [dict(r) for r in cursor.fetchall()]

def upsert_growth_experiment(sku: str, hypothesis: str, target_profit_vnd: float = 0.0,
                             angles_planned: int = 3, angles_tested: int = 0,
                             status: str = "TESTING", decision: str = "OBSERVING",
                             learning_notes: str = "") -> Dict[str, Any]:
    """Tạo hoặc cập nhật chu kỳ thử nghiệm tăng trưởng cho SKU."""
    now = datetime.datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM growth_experiments WHERE sku = ?", (sku,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE growth_experiments SET
                    hypothesis = ?, target_profit_vnd = ?, angles_planned = ?,
                    angles_tested = ?, status = ?, decision = ?, learning_notes = ?,
                    updated_at = ?
                WHERE sku = ?
            """, (hypothesis, target_profit_vnd, angles_planned, angles_tested, status, decision, learning_notes, now, sku))
        else:
            cursor.execute("""
                INSERT INTO growth_experiments (
                    sku, hypothesis, target_profit_vnd, angles_planned, angles_tested,
                    status, decision, learning_notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sku, hypothesis, target_profit_vnd, angles_planned, angles_tested, status, decision, learning_notes, now, now))
        conn.commit()
    return get_sku_experiment(sku)

def get_sku_experiment(sku: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin thử nghiệm tăng trưởng của một SKU."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM growth_experiments WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        return dict(row) if row else None

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions: Sprint 1 Market Discovery
# ─────────────────────────────────────────────────────────────────────────────

def upsert_niche(niche_data: Dict[str, Any]) -> Dict[str, Any]:
    """Lưu hoặc cập nhật một ngách thị trường."""
    now = datetime.datetime.now().isoformat()
    n_id = niche_data["id"]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO market_niches (
                id, name, category, demand_score, footage_score, economics_score,
                competition_score, quality_score, scalability_score, total_score,
                confidence_grade, rank, selected_status, reasoning, risks, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                demand_score = excluded.demand_score,
                footage_score = excluded.footage_score,
                economics_score = excluded.economics_score,
                competition_score = excluded.competition_score,
                quality_score = excluded.quality_score,
                scalability_score = excluded.scalability_score,
                total_score = excluded.total_score,
                confidence_grade = excluded.confidence_grade,
                rank = excluded.rank,
                selected_status = excluded.selected_status,
                reasoning = excluded.reasoning,
                risks = excluded.risks,
                updated_at = excluded.updated_at;
        """, (
            n_id, niche_data["name"], niche_data.get("category", "Chung"),
            float(niche_data.get("demand_score", 0.0)),
            float(niche_data.get("footage_score", 0.0)),
            float(niche_data.get("economics_score", 0.0)),
            float(niche_data.get("competition_score", 0.0)),
            float(niche_data.get("quality_score", 0.0)),
            float(niche_data.get("scalability_score", 0.0)),
            float(niche_data.get("total_score", 0.0)),
            niche_data.get("confidence_grade", "MEDIUM"),
            int(niche_data.get("rank", 0)),
            niche_data.get("selected_status", "CANDIDATE"),
            niche_data.get("reasoning", ""),
            niche_data.get("risks", ""),
            now
        ))
        conn.commit()
    return get_niche(n_id)

def get_niche(niche_id: str) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết một ngách theo ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM market_niches WHERE id = ?", (niche_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def list_niches(order_by_score: bool = True) -> List[Dict[str, Any]]:
    """Liệt kê toàn bộ danh sách các ngách."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if order_by_score:
            cursor.execute("SELECT * FROM market_niches ORDER BY total_score DESC")
        else:
            cursor.execute("SELECT * FROM market_niches ORDER BY id ASC")
        return [dict(r) for r in cursor.fetchall()]

def upsert_candidate_product(prod_data: Dict[str, Any]) -> Dict[str, Any]:
    """Lưu hoặc cập nhật sản phẩm đại diện của ngách."""
    now = datetime.datetime.now().isoformat()
    sku = prod_data["sku"]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO candidate_products (
                sku, niche_id, title, platform, url, price_vnd,
                commission_rate, commission_vnd, rating, reviews_count,
                demand_signal, competition_signal, footage_source,
                permission_tier, risk_notes, confidence_grade, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sku) DO UPDATE SET
                niche_id = excluded.niche_id,
                title = excluded.title,
                platform = excluded.platform,
                url = excluded.url,
                price_vnd = excluded.price_vnd,
                commission_rate = excluded.commission_rate,
                commission_vnd = excluded.commission_vnd,
                rating = excluded.rating,
                reviews_count = excluded.reviews_count,
                demand_signal = excluded.demand_signal,
                competition_signal = excluded.competition_signal,
                footage_source = excluded.footage_source,
                permission_tier = excluded.permission_tier,
                risk_notes = excluded.risk_notes,
                confidence_grade = excluded.confidence_grade;
        """, (
            sku, prod_data["niche_id"], prod_data["title"], prod_data.get("platform", "TIKTOK_SHOP"),
            prod_data.get("url", ""), float(prod_data.get("price_vnd", 0.0)),
            float(prod_data.get("commission_rate", 0.0)),
            float(prod_data.get("commission_vnd", 0.0)),
            float(prod_data.get("rating", 0.0)),
            int(prod_data.get("reviews_count", 0)),
            prod_data.get("demand_signal", ""),
            prod_data.get("competition_signal", ""),
            prod_data.get("footage_source", ""),
            prod_data.get("permission_tier", "unknown"),
            prod_data.get("risk_notes", ""),
            prod_data.get("confidence_grade", "MEDIUM"),
            now
        ))
        conn.commit()
    return get_candidate_product(sku)

def get_candidate_product(sku: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin sản phẩm ứng viên theo SKU."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidate_products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        return dict(row) if row else None

def list_candidate_products(niche_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Liệt kê các sản phẩm ứng viên theo ngách hoặc toàn bộ."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if niche_id:
            cursor.execute("SELECT * FROM candidate_products WHERE niche_id = ? ORDER BY price_vnd ASC", (niche_id,))
        else:
            cursor.execute("SELECT * FROM candidate_products ORDER BY niche_id ASC, price_vnd ASC")
        return [dict(r) for r in cursor.fetchall()]

def record_evidence(entity_type: str, entity_id: str, metric_name: str, value: str,
                    source: str, confidence: str = "HIGH", notes: str = ""):
    """Ghi nhận một bằng chứng vào Evidence Registry."""
    now = datetime.datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO evidence_records (
                entity_type, entity_id, metric_name, value, source, observation_time, confidence, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (entity_type, entity_id, metric_name, value, source, now, confidence, notes))
        conn.commit()

def list_evidence_records(entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lấy danh sách các bằng chứng đã ghi nhận."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if entity_id:
            cursor.execute("SELECT * FROM evidence_records WHERE entity_id = ? ORDER BY id ASC", (entity_id,))
        else:
            cursor.execute("SELECT * FROM evidence_records ORDER BY id ASC")
        return [dict(r) for r in cursor.fetchall()]

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions: Audience Personas & Editorial Strategy
# ─────────────────────────────────────────────────────────────────────────────

def upsert_audience_persona(persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """Lưu hoặc cập nhật hồ sơ chân dung khán giả."""
    now = datetime.datetime.now().isoformat()
    p_id = persona_data["id"]
    pains_str = json.dumps(persona_data.get("primary_pains", []), ensure_ascii=False)
    free_sol_str = json.dumps(persona_data.get("free_solutions", []), ensure_ascii=False)
    monetize_str = json.dumps(persona_data.get("monetization_opportunities", []), ensure_ascii=False)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audience_personas (
                id, name, archetype, core_demographic, lifestyle_context,
                primary_pains_json, reasons_to_follow, free_solutions_json,
                monetization_opportunities_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                archetype = excluded.archetype,
                core_demographic = excluded.core_demographic,
                lifestyle_context = excluded.lifestyle_context,
                primary_pains_json = excluded.primary_pains_json,
                reasons_to_follow = excluded.reasons_to_follow,
                free_solutions_json = excluded.free_solutions_json,
                monetization_opportunities_json = excluded.monetization_opportunities_json,
                updated_at = excluded.updated_at;
        """, (
            p_id, persona_data["name"], persona_data.get("archetype", "SMART_CONSUMER_AND_PROBLEM_SOLVER"),
            persona_data.get("core_demographic", ""), persona_data.get("lifestyle_context", ""),
            pains_str, persona_data.get("reasons_to_follow", ""),
            free_sol_str, monetize_str, now, now
        ))
        conn.commit()
    return get_audience_persona(p_id)

def get_audience_persona(persona_id: str) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết hồ sơ khán giả theo ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audience_personas WHERE id = ?", (persona_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["primary_pains"] = json.loads(res.get("primary_pains_json") or "[]")
        res["free_solutions"] = json.loads(res.get("free_solutions_json") or "[]")
        res["monetization_opportunities"] = json.loads(res.get("monetization_opportunities_json") or "[]")
        return res

def list_audience_personas() -> List[Dict[str, Any]]:
    """Liệt kê toàn bộ danh sách hồ sơ khán giả."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audience_personas ORDER BY id ASC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["primary_pains"] = json.loads(d.get("primary_pains_json") or "[]")
            d["free_solutions"] = json.loads(d.get("free_solutions_json") or "[]")
            d["monetization_opportunities"] = json.loads(d.get("monetization_opportunities_json") or "[]")
            result.append(d)
        return result

def save_editorial_plan(plan_items: List[Dict[str, Any]], persona_id: str):
    """Lưu kế hoạch nội dung biên tập 30 video."""
    now = datetime.datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        # Xóa kế hoạch cũ của persona nếu có để cập nhật lại
        cursor.execute("DELETE FROM editorial_plan WHERE persona_id = ?", (persona_id,))
        for item in plan_items:
            cursor.execute("""
                INSERT INTO editorial_plan (
                    persona_id, video_number, content_type, title, hook_angle,
                    core_pain_point, solution_type, has_affiliate_link, linked_sku,
                    target_kpi_pillar, primary_metric, faceless_visual_style,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                persona_id, int(item["video_number"]), item["content_type"],
                item["title"], item["hook_angle"], item["core_pain_point"],
                item["solution_type"], 1 if item.get("has_affiliate_link") else 0,
                item.get("linked_sku"), item["target_kpi_pillar"],
                item["primary_metric"], item["faceless_visual_style"],
                item.get("status", "PLANNED"), now, now
            ))
        conn.commit()

def list_editorial_plan(persona_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lấy danh sách các video trong kế hoạch biên tập."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if persona_id:
            cursor.execute("SELECT * FROM editorial_plan WHERE persona_id = ? ORDER BY video_number ASC", (persona_id,))
        else:
            cursor.execute("SELECT * FROM editorial_plan ORDER BY video_number ASC")
        return [dict(r) for r in cursor.fetchall()]



