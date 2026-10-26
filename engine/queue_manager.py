"""
engine/queue_manager.py
================================================================================
Quản lý hàng đợi tác vụ bền vững (Durable Job Queue):
- Cơ chế Lease tránh tranh chấp tác vụ
- Khả năng tự phục hồi khi mất điện / khởi động lại máy
- Retry có kiểm soát; chuyển sang NEEDS_ATTENTION khi quá số lần thử
================================================================================
"""

import uuid
import json
import datetime
from typing import Optional, Dict, Any, List
from engine.database import get_connection, log_event

class QueueManager:
    """Điều phối hàng đợi công việc."""

    @staticmethod
    def enqueue(sku: str, job_type: str, payload: Optional[Dict[str, Any]] = None) -> int:
        """Đưa tác vụ mới vào hàng đợi."""
        now = datetime.datetime.now().isoformat()
        payload_str = json.dumps(payload or {}, ensure_ascii=False)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jobs (sku, job_type, status, attempt_count, payload_json, created_at, updated_at)
                VALUES (?, ?, 'QUEUED', 0, ?, ?, ?)
            """, (sku, job_type, payload_str, now, now))
            job_id = cursor.lastrowid
            conn.commit()

        log_event(sku, "JOB_ENQUEUED", {"job_id": job_id, "type": job_type})
        return job_id

    @staticmethod
    def claim_next_job(worker_id: str = "local_worker", lease_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """
        Nhận tác vụ tiếp theo để xử lý (Atomic claim với Lease).
        Tự động nhận diện cả các job hết hạn lease (bị treo/crash).
        """
        now = datetime.datetime.now()
        now_str = now.isoformat()
        lease_expire_time = (now + datetime.timedelta(seconds=lease_seconds)).isoformat()
        lease_token = f"{worker_id}_{uuid.uuid4().hex[:8]}"

        with get_connection() as conn:
            cursor = conn.cursor()

            # 1. Tìm job ở trạng thái QUEUED hoặc RUNNING nhưng đã quá hạn lease
            cursor.execute("""
                SELECT id, sku, job_type, payload_json, attempt_count
                FROM jobs
                WHERE status = 'QUEUED' 
                   OR (status = 'RUNNING' AND lease_expires_at < ?)
                ORDER BY id ASC
                LIMIT 1
            """, (now_str,))
            row = cursor.fetchone()

            if not row:
                return None

            job_id = row["id"]
            attempts = row["attempt_count"] + 1

            # 2. Khóa tác vụ bằng lease token
            cursor.execute("""
                UPDATE jobs
                SET status = 'RUNNING',
                    lease_token = ?,
                    lease_expires_at = ?,
                    attempt_count = ?,
                    updated_at = ?
                WHERE id = ?
            """, (lease_token, lease_expire_time, attempts, now_str, job_id))
            conn.commit()

        log_event(row["sku"], "JOB_CLAIMED", {"job_id": job_id, "worker": worker_id, "attempt": attempts})

        return {
            "id": job_id,
            "sku": row["sku"],
            "job_type": row["job_type"],
            "payload": json.loads(row["payload_json"]) if row["payload_json"] else {},
            "attempt_count": attempts,
            "lease_token": lease_token
        }

    @staticmethod
    def complete(job_id: int, result: Optional[Dict[str, Any]] = None):
        """Đánh dấu tác vụ hoàn thành thành công."""
        now = datetime.datetime.now().isoformat()
        res_str = json.dumps(result or {}, ensure_ascii=False)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs
                SET status = 'DONE',
                    result_json = ?,
                    updated_at = ?,
                    lease_token = NULL,
                    lease_expires_at = NULL
                WHERE id = ?
            """, (res_str, now, job_id))
            
            cursor.execute("SELECT sku, job_type FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            conn.commit()

        if row:
            log_event(row["sku"], "JOB_COMPLETED", {"job_id": job_id, "type": row["job_type"]})

    @staticmethod
    def fail(job_id: int, error_message: str, max_attempts: int = 3):
        """Xử lý tác vụ bị lỗi. Tự động chuyển NEEDS_ATTENTION nếu quá số lần thử."""
        now = datetime.datetime.now().isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sku, job_type, attempt_count FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if not row:
                return

            sku = row["sku"]
            attempts = row["attempt_count"]
            next_status = 'NEEDS_ATTENTION' if attempts >= max_attempts else 'QUEUED'

            cursor.execute("""
                UPDATE jobs
                SET status = ?,
                    error_message = ?,
                    updated_at = ?,
                    lease_token = NULL,
                    lease_expires_at = NULL
                WHERE id = ?
            """, (next_status, error_message, now, job_id))
            conn.commit()

        log_event(sku, "JOB_FAILED", {
            "job_id": job_id,
            "error": error_message,
            "attempts": attempts,
            "status": next_status
        })

    @staticmethod
    def recover_expired_leases() -> int:
        """Thu hồi các job bị treo khi ứng dụng hoặc máy bị tắt đột ngột."""
        now_str = datetime.datetime.now().isoformat()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs
                SET status = 'QUEUED',
                    lease_token = NULL,
                    lease_expires_at = NULL,
                    updated_at = ?
                WHERE status = 'RUNNING' AND lease_expires_at < ?
            """, (now_str, now_str))
            recovered_count = cursor.rowcount
            conn.commit()

        if recovered_count > 0:
            log_event(None, "LEASES_RECOVERED", {"count": recovered_count})
        return recovered_count

    @staticmethod
    def get_stats() -> Dict[str, int]:
        """Thống kê trạng thái hàng đợi."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) as count FROM jobs GROUP BY status")
            rows = cursor.fetchall()
            return {r["status"]: r["count"] for r in rows}
