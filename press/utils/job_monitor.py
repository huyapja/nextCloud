import frappe  # type: ignore


def diagnose_stuck_jobs(include_pending=True, include_running=True, job_type=None):
    """
    Kiểm tra các job bị treo ở Pending hoặc Running

    Args:
        include_pending: Kiểm tra jobs Pending
        include_running: Kiểm tra jobs Running
        job_type: Lọc theo job_type cụ thể (None = tất cả)
    """
    print(f"{'='*60}")
    print("KIỂM TRA JOBS BỊ TREO (TẤT CẢ AGENT JOBS)")
    print(f"{'='*60}\n")

    statuses = []
    if include_pending:
        statuses.append("Pending")
    if include_running:
        statuses.append("Running")

    if not statuses:
        print("⚠️  Cần chọn ít nhất một status để kiểm tra")
        return

    filters = {"status": ["in", statuses]}
    if job_type:
        filters["job_type"] = job_type
        print(f"⚠️  Đang lọc theo job_type: {job_type}\n")

    # ===== 1. Tổng quan tất cả agent jobs =====
    print(f"{'='*60}")
    print(f"1. TỔNG QUAN TẤT CẢ AGENT JOBS ({', '.join(statuses)})")
    print(f"{'='*60}\n")

    all_jobs = frappe.get_all(
        "Agent Job",
        filters=filters,
        fields=["name", "job_type", "server", "job_id", "status", "creation", "start"],
        order_by="creation desc",
    )

    if all_jobs:
        print(f"Tìm thấy {len(all_jobs)} job(s) ({', '.join(statuses)}):\n")

        # Nhóm theo job_type
        by_type = {}
        for job_info in all_jobs:
            job_type = job_info.job_type
            if job_type not in by_type:
                by_type[job_type] = {"Pending": 0, "Running": 0, "total": 0}
            by_type[job_type][job_info.status] = (
                by_type[job_type].get(job_info.status, 0) + 1
            )
            by_type[job_type]["total"] += 1

        print("Phân bố theo job_type:")
        for job_type, counts in sorted(by_type.items()):
            pending = counts.get("Pending", 0)
            running = counts.get("Running", 0)
            total = counts["total"]
            print(
                f"  - {job_type}: {total} job(s) (Pending: {pending}, Running: {running})"
            )

        print()

        # Nhóm theo server
        by_server = {}
        for job_info in all_jobs:
            server = job_info.server
            if server not in by_server:
                by_server[server] = {"Pending": 0, "Running": 0, "total": 0}
            by_server[server][job_info.status] = (
                by_server[server].get(job_info.status, 0) + 1
            )
            by_server[server]["total"] += 1

        print("Phân bố theo server:")
        for server, counts in sorted(by_server.items()):
            pending = counts.get("Pending", 0)
            running = counts.get("Running", 0)
            total = counts["total"]
            print(
                f"  - {server}: {total} job(s) (Pending: {pending}, Running: {running})"
            )

        print()
    else:
        print(f"✓ Không có job nào ({', '.join(statuses)})\n")
        return

    # ===== 2. Chi tiết một số jobs quan trọng =====
    print(f"{'='*60}")
    print("2. CHI TIẾT CÁC JOBS (Lấy mẫu)")
    print(f"{'='*60}\n")

    # Lấy mẫu từ mỗi job_type
    sample_jobs = []
    seen_types = set()

    for job_info in all_jobs[:50]:  # Giới hạn để không quá nhiều
        if job_info.job_type not in seen_types or len(sample_jobs) < 10:
            sample_jobs.append(job_info)
            seen_types.add(job_info.job_type)
            if len(sample_jobs) >= 10:
                break

    if sample_jobs:
        print(f"Hiển thị {len(sample_jobs)} job(s) mẫu:\n")

        for job_info in sample_jobs:
            job = frappe.get_doc("Agent Job", job_info.name)

            status_icon = (
                "⚠️"
                if job.status == "Pending"
                else "🔄" if job.status == "Running" else "✓"
            )
            print(f"{status_icon} {job.job_type}: {job.name} ({job.status})")
            print(f"  Server: {job.server}")
            print(f"  Job ID: {job.job_id or 'Chưa có'}")
            print(f"  Created: {job.creation}")
            print(f"  Started: {job.start or 'N/A'}")

            # Phân tích theo status
            if job.status == "Pending":
                if not job.job_id:
                    print(
                        f"  ⚠️  PRESS SERVER - Chưa có job_id → chưa được gửi đến agent"
                    )
                else:
                    print(f"  ⚠️  AGENT SERVER - Đã có job_id nhưng vẫn Pending")

            # Tính thời gian
            if job.start:
                start_time = (
                    frappe.utils.get_datetime(job.start)
                    if isinstance(job.start, str)
                    else job.start
                )
                now = frappe.utils.now_datetime()
                if isinstance(now, str):
                    now = frappe.utils.get_datetime(now)
                duration = now - start_time
                hours = duration.total_seconds() / 3600
                print(f"  Đã chạy: {hours:.2f} giờ")
                if hours > 2:
                    print(f"  ⚠️  ĐÃ CHẠY QUÁ LÂU!")
            elif job.status == "Pending" and job.job_id:
                created_time = (
                    frappe.utils.get_datetime(job.creation)
                    if isinstance(job.creation, str)
                    else job.creation
                )
                now = frappe.utils.now_datetime()
                if isinstance(now, str):
                    now = frappe.utils.get_datetime(now)
                duration = now - created_time
                hours = duration.total_seconds() / 3600
                print(f"  Đã Pending: {hours:.2f} giờ")
                if hours > 1:
                    print(f"  ⚠️  ĐÃ PENDING QUÁ LÂU!")

            # Kiểm tra reference
            if job.reference_doctype and job.reference_name:
                print(f"  Reference: {job.reference_doctype} > {job.reference_name}")

            print()
    else:
        print("Không có job nào để hiển thị\n")

    # ===== 3. Kiểm tra các jobs đã chạy quá lâu =====
    print(f"{'='*60}")
    print("3. JOBS ĐÃ CHẠY/PENDING QUÁ LÂU")
    print(f"{'='*60}\n")

    long_jobs = []
    for job_info in all_jobs:
        job = frappe.get_doc("Agent Job", job_info.name)

        if job.status == "Running" and job.start:
            start_time = (
                frappe.utils.get_datetime(job.start)
                if isinstance(job.start, str)
                else job.start
            )
            now = frappe.utils.now_datetime()
            if isinstance(now, str):
                now = frappe.utils.get_datetime(now)
            duration = now - start_time
            hours = duration.total_seconds() / 3600
            if hours > 1:
                long_jobs.append((job, hours, "running"))
        elif job.status == "Pending" and job.job_id:
            created_time = (
                frappe.utils.get_datetime(job.creation)
                if isinstance(job.creation, str)
                else job.creation
            )
            now = frappe.utils.now_datetime()
            if isinstance(now, str):
                now = frappe.utils.get_datetime(now)
            duration = now - created_time
            hours = duration.total_seconds() / 3600
            if hours > 1:
                long_jobs.append((job, hours, "pending"))

    if long_jobs:
        print(f"Tìm thấy {len(long_jobs)} job(s) đã chạy/pending > 1 giờ:\n")
        for job, hours, job_status in sorted(
            long_jobs, key=lambda x: x[1], reverse=True
        )[:10]:
            print(f"  ⚠️  {job.job_type}: {job.name}")
            print(f"     Status: {job.status}, Đã {job_status}: {hours:.2f} giờ")
            print(f"     Server: {job.server}")
    else:
        print("✓ Không có job nào chạy/pending quá lâu\n")

    # ===== Tổng kết =====
    print(f"{'='*60}")
    print("TỔNG KẾT")
    print(f"{'='*60}\n")

    print(f"Tổng số jobs: {len(all_jobs)}")
    print(f"  - Pending: {len([j for j in all_jobs if j.status == 'Pending'])}")
    print(f"  - Running: {len([j for j in all_jobs if j.status == 'Running'])}")
    print(f"  - Jobs quá lâu: {len(long_jobs)}")

    print(f"\n{'='*60}")


def force_poll_and_fix_stuck_jobs():
    """
    Force poll và fix TẤT CẢ agent jobs bị stuck (cả Pending và Running)
    Áp dụng cho TẤT CẢ job types
    """
    print(f"{'='*60}")
    print("FORCE POLL TẤT CẢ AGENT JOBS (PENDING + RUNNING)")
    print(f"{'='*60}\n")

    # Import lại để đảm bảo
    try:
        from press.press.doctype.agent_job.agent_job import poll_pending_jobs_server
    except ImportError:
        import importlib

        agent_job_module = importlib.import_module(
            "press.press.doctype.agent_job.agent_job"
        )
        poll_pending_jobs_server = agent_job_module.poll_pending_jobs_server

    # Poll tất cả servers có jobs đang Pending hoặc Running (KHÔNG phân biệt job_type)
    servers_with_jobs = frappe.get_all(
        "Agent Job",
        filters={"status": ["in", ["Pending", "Running"]]},  # ← TẤT CẢ job types
        fields=["server", "server_type"],
        distinct=True,
    )

    print(f"Tìm thấy {len(servers_with_jobs)} server(s) có jobs Pending/Running\n")

    total_polled = 0
    for server_info in servers_with_jobs:
        server = frappe._dict(
            {
                "server": server_info.server,
                "server_type": server_info.get("server_type", "Server"),
            }
        )

        # Đếm số jobs trên server này (TẤT CẢ job types)
        job_count = frappe.db.count(
            "Agent Job",
            {"server": server_info.server, "status": ["in", ["Pending", "Running"]]},
        )

        print(
            f"→ Polling server: {server_info.server} ({job_count} jobs - TẤT CẢ job types)..."
        )
        try:
            poll_pending_jobs_server(
                server
            )  # ← Function này poll TẤT CẢ jobs trên server
            frappe.db.commit()
            print(f"✓ Đã poll server {server_info.server} ({job_count} jobs)")
            total_polled += job_count
        except Exception as e:
            print(f"✗ Lỗi khi poll {server_info.server}: {e}")
            import traceback

            traceback.print_exc()

    print(
        f"\n✓ Hoàn thành! Đã poll {total_polled} jobs từ {len(servers_with_jobs)} server(s)"
    )
    print("\n→ Kiểm tra lại bằng: diagnose_stuck_jobs()")


def auto_fix_stuck_jobs():
    """
    Tự động fix các jobs bị stuck - chạy từ scheduler
    Không có print statements để không spam logs
    """
    try:
        from press.press.doctype.agent_job.agent_job import poll_pending_jobs_server
        from press.utils import log_error

        # Poll tất cả servers có jobs Pending/Running
        servers_with_jobs = frappe.get_all(
            "Agent Job",
            filters={"status": ["in", ["Pending", "Running"]]},
            fields=["server", "server_type"],
            distinct=True,
        )

        if not servers_with_jobs:
            return

        fixed_count = 0

        for server_info in servers_with_jobs:
            try:
                server = frappe._dict(
                    {
                        "server": server_info.server,
                        "server_type": server_info.get("server_type", "Server"),
                    }
                )

                # Poll server
                poll_pending_jobs_server(server)
                frappe.db.commit()
                fixed_count += 1

            except Exception as e:
                log_error(
                    "Auto Fix Stuck Jobs Error", server=server_info.server, error=str(e)
                )
                frappe.db.rollback()

        if fixed_count > 0:
            frappe.logger().info(f"Auto fixed stuck jobs on {fixed_count} server(s)")

    except Exception as e:
        from press.utils import log_error

        log_error("Auto Fix Stuck Jobs Error", error=str(e))
        frappe.db.rollback()


@frappe.whitelist()
def quick_fix_all_stuck_jobs():
    """
    Quick fix tất cả stuck jobs - có thể gọi từ UI hoặc API
    """
    try:
        from press.press.doctype.agent_job.agent_job import poll_pending_jobs_server

        servers_with_jobs = frappe.get_all(
            "Agent Job",
            filters={"status": ["in", ["Pending", "Running"]]},
            fields=["server", "server_type"],
            distinct=True,
        )

        if not servers_with_jobs:
            return {
                "status": "success",
                "message": "Không có jobs nào cần fix",
                "servers_polled": 0,
            }

        fixed_count = 0
        errors = []

        for server_info in servers_with_jobs:
            server = frappe._dict(
                {
                    "server": server_info.server,
                    "server_type": server_info.get("server_type", "Server"),
                }
            )

            try:
                poll_pending_jobs_server(server)
                frappe.db.commit()
                fixed_count += 1
            except Exception as e:
                errors.append(f"{server_info.server}: {str(e)}")
                frappe.db.rollback()

        return {
            "status": "success",
            "servers_polled": fixed_count,
            "total_servers": len(servers_with_jobs),
            "errors": errors if errors else None,
        }

    except Exception as e:
        frappe.log_error(f"Quick fix stuck jobs error: {e}")
        return {"status": "error", "message": str(e)}
