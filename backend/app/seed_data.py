import datetime
from sqlalchemy.orm import Session
from app.models import Incident, ActivityBaseline, RecurrenceGroup
from app.constants import TECH_DEBT_RECURRENCE_THRESHOLD

def seed_database(db: Session):
    """
    Clears existing tables and seeds 8 realistic historical incidents, baselines, and technical debt groups.
    """
    # 1. Clear existing data
    db.query(Incident).delete()
    db.query(ActivityBaseline).delete()
    db.query(RecurrenceGroup).delete()
    db.commit()

    now = datetime.datetime.utcnow()

    # 2. Historical Incidents
    historical_incidents = [
        # Incident 1: /login DB Timeout (Resolved Past Fix #1)
        Incident(
            created_at=now - datetime.timedelta(days=7),
            service="auth-service",
            endpoint="/login",
            error_type="DatabaseTimeoutError",
            error_message="Connection to Postgres pool timed out after 3000ms waiting for available client",
            stack_trace="Traceback (most recent call last):\n  File \"/app/auth/db.py\", line 42, in get_user\n    conn = pool.get_connection(timeout=3.0)\n  File \"/app/db/pool.py\", line 110, in get_connection\n    raise DatabaseTimeoutError(\"Pool exhausted\")",
            category="Database",
            root_cause="DB connection pool max_connections limit was set to 10 under high concurrent login traffic, causing queue starvation.",
            fix_description="Increased HikariCP/AsyncPG max pool size to 50 connections and added context manager auto-close on auth sessions.",
            fix_pr_url="https://github.com/org/auth-service/pull/402",
            status="RESOLVED",
            resolution_verified=True
        ),

        # Incident 2: /login Auth Token Expired Exception (Resolved #2)
        Incident(
            created_at=now - datetime.timedelta(days=5),
            service="auth-service",
            endpoint="/login",
            error_type="JWTVerificationError",
            error_message="Signature verification failed on refresh token payload due to clock skew",
            stack_trace="Traceback (most recent call last):\n  File \"/app/auth/jwt.py\", line 88, in verify_token\n    jwt.decode(token, SECRET_KEY, algorithms=[\"HS256\"])\n  File \"/usr/local/lib/python3.10/jwt/api_jwt.py\", line 140, in decode\n    raise ExpiredSignatureError(\"Signature has expired\")",
            category="Authentication",
            root_cause="Server NTP synchronization drift caused 45-second clock skew between auth worker nodes and token issuer.",
            fix_description="Added 60s clock leeway tolerance to PyJWT decode configuration and enabled systemd-timesyncd daemon.",
            fix_pr_url="https://github.com/org/auth-service/pull/415",
            status="RESOLVED",
            resolution_verified=True
        ),

        # Incident 3: /login Rate Limiter Memory Exhaustion (Resolved #3 - 3rd /login incident!)
        Incident(
            created_at=now - datetime.timedelta(days=3),
            service="auth-service",
            endpoint="/login",
            error_type="RedisConnectionError",
            error_message="OOM command not allowed when used memory > 'maxmemory' in Redis rate limiter instance",
            stack_trace="Traceback (most recent call last):\n  File \"/app/middleware/ratelimit.py\", line 19, in check_rate_limit\n    redis.setex(key, 60, 1)\n  File \"/app/redis/client.py\", line 55, in setex\n    raise ResponseError(\"OOM command not allowed\")",
            category="Memory",
            root_cause="Redis key eviction policy was set to noeviction instead of volatile-lru, causing IP rate-limit keys to fill RAM.",
            fix_description="Updated redis.conf maxmemory-policy to volatile-lru and enabled key TTL compression.",
            fix_pr_url="https://github.com/org/auth-service/pull/428",
            status="RESOLVED",
            resolution_verified=True
        ),

        # Incident 4: /checkout Payment Gateway ConnectionRefused (Resolved #4)
        Incident(
            created_at=now - datetime.timedelta(days=2),
            service="payment-service",
            endpoint="/checkout",
            error_type="ConnectionRefusedError",
            error_message="HTTP/1.1 POST https://api.stripe.com/v1/charges failed with Connection Refused",
            stack_trace="Traceback (most recent call last):\n  File \"/app/payment/stripe_client.py\", line 34, in charge\n    res = httpx.post(STRIPE_URL, data=payload, timeout=5.0)\n  File \"/usr/local/lib/python3.10/httpx/_transports/default.py\", line 220, in handle_request\n    raise ConnectError(\"Connection refused\")",
            category="Network",
            root_cause="Egress NAT Gateway elastic IP was temporarily throttled by upstream firewall.",
            fix_description="Configured dual multi-region NAT gateways with automated fallback route tables.",
            fix_pr_url="https://github.com/org/payment-service/pull/189",
            status="RESOLVED",
            resolution_verified=True
        ),

        # Incident 5: /user/profile NullPointer on Avatar URL (Resolved #5)
        Incident(
            created_at=now - datetime.timedelta(days=4),
            service="user-service",
            endpoint="/user/profile",
            error_type="NullPointerError",
            error_message="Cannot read property 'avatar_url' of undefined in profile payload transformer",
            stack_trace="TypeError: Cannot read properties of null (reading 'avatar_url')\n    at transformProfile (/app/dist/transformers/user.js:14:22)\n    at getProfileHandler (/app/dist/controllers/user.js:80:12)",
            category="Frontend/Backend API",
            root_cause="Legacy user records created prior to v2 migration missing default S3 avatar image placeholder.",
            fix_description="Added Nullish Coalescing operator `user.avatar_url ?? DEFAULT_AVATAR` in user payload DTO serializer.",
            fix_pr_url="https://github.com/org/user-service/pull/94",
            status="RESOLVED",
            resolution_verified=True
        ),

        # Incident 6: /reports/export OutOfMemory Heap Error (Resolved #6)
        Incident(
            created_at=now - datetime.timedelta(days=6),
            service="analytics-service",
            endpoint="/reports/export",
            error_type="OutOfMemoryError",
            error_message="JavaScript heap out of memory during PDF generation of 50,000 row CSV export",
            stack_trace="FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory\n 1: 0xb83d00 node::Abort() [/usr/local/bin/node]",
            category="Memory",
            root_cause="Puppeteer HTML-to-PDF renderer buffering entire 50k dataset directly in memory before writing to disk stream.",
            fix_description="Refactored PDF report generator to use Node.js Transform stream chunks and worker threads.",
            fix_pr_url="https://github.com/org/analytics-service/pull/312",
            status="RESOLVED",
            resolution_verified=True
        ),

        # Incident 7: /search Elasticsearch Shard Failure (Resolved #7)
        Incident(
            created_at=now - datetime.timedelta(days=1),
            service="search-service",
            endpoint="/search",
            error_type="ElasticsearchShardError",
            error_message="[products_v3][0] Primary shard failed: OutOfDirectMemoryError",
            stack_trace="org.elasticsearch.index.engine.EngineException: OutOfDirectMemoryError\n  at org.elasticsearch.index.engine.InternalEngine.flush(InternalEngine.java:1102)",
            category="Database",
            root_cause="Unbounded aggregation query on unindexed string fields flooded lucene index memory.",
            fix_description="Set `indices.breaker.fielddata.limit: 40%` in ES cluster config and added doc_values indexing.",
            fix_pr_url="https://github.com/org/search-service/pull/77",
            status="RESOLVED",
            resolution_verified=True
        ),

        # Incident 8: /login DB Timeout (ACTIVE OPEN DUPLICATE of Incident 1!)
        Incident(
            created_at=now - datetime.timedelta(minutes=15),
            service="auth-service",
            endpoint="/login",
            error_type="DatabaseTimeoutError",
            error_message="Connection to Postgres pool timed out after 3000ms waiting for available client during peak load",
            stack_trace="Traceback (most recent call last):\n  File \"/app/auth/db.py\", line 42, in get_user\n    conn = pool.get_connection(timeout=3.0)\n  File \"/app/db/pool.py\", line 110, in get_connection\n    raise DatabaseTimeoutError(\"Pool exhausted\")",
            category="Database",
            root_cause=None,
            fix_description=None,
            fix_pr_url=None,
            status="OPEN",
            resolution_verified=False
        ),
    ]

    for inc in historical_incidents:
        db.add(inc)
    db.commit()

    # 3. Activity Baselines for Silent Failure Detection
    baselines = [
        ActivityBaseline(
            service_endpoint="payment-service:/checkout",
            expected_rate=120.0, # 120 reqs/5min expected
            window=300, # 5 min window
            last_seen_at=now, # Active now by default
            anomaly_threshold=0.8
        ),
        ActivityBaseline(
            service_endpoint="auth-service:/login",
            expected_rate=450.0,
            window=300,
            last_seen_at=now,
            anomaly_threshold=0.8
        ),
        ActivityBaseline(
            service_endpoint="user-service:/profile",
            expected_rate=200.0,
            window=300,
            last_seen_at=now,
            anomaly_threshold=0.8
        ),
    ]
    for b in baselines:
        db.add(b)
    db.commit()

    # 4. Recurrence Groups for Technical Debt Tracking
    # Signature pattern: service:endpoint:error_type
    # /login has 3 occurrences (Incident 1, Incident 2, Incident 3 + Incident 8)
    recurrence_groups = [
        RecurrenceGroup(
            signature="auth-service:/login:DatabaseTimeoutError",
            occurrence_count=2,
            first_seen=now - datetime.timedelta(days=7),
            last_seen=now - datetime.timedelta(minutes=15),
            flagged_as_debt=False,
            recommendation="Monitor DB pool saturation on auth-service."
        ),
        RecurrenceGroup(
            signature="auth-service:/login:MULTIPLE_ERRORS",
            occurrence_count=4,
            first_seen=now - datetime.timedelta(days=7),
            last_seen=now - datetime.timedelta(minutes=15),
            flagged_as_debt=True,
            recommendation="CRITICAL TECH DEBT: Endpoint /login has failed 4 times across Database, JWT, and Redis rate limiters. High structural fragility detected!"
        ),
        RecurrenceGroup(
            signature="payment-service:/checkout:ConnectionRefusedError",
            occurrence_count=1,
            first_seen=now - datetime.timedelta(days=2),
            last_seen=now - datetime.timedelta(days=2),
            flagged_as_debt=False,
            recommendation="Single network glitch recorded."
        )
    ]
    for r in recurrence_groups:
        db.add(r)
    db.commit()

    return {
        "incidents_seeded": len(historical_incidents),
        "baselines_seeded": len(baselines),
        "recurrence_groups_seeded": len(recurrence_groups)
    }
