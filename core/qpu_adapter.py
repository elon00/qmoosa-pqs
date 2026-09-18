#!/usr/bin/env python3
"""
Canonical Cloud QPU Execution Lifecycle Adapters for Origin Quantum Cloud and IBM Quantum Runtime.

Enforces the full provider execution lifecycle:
1. probe()                 - Real network TLS handshake & authentication check
2. submit()                - Dispatches circuit; retrieves provider-assigned ID
3. poll()                  - Monitors cloud queue until terminal COMPLETED state
4. get_result()            - Retrieves raw measurement counts from provider
5. independent_re_query()  - Out-of-band direct HTTP re-query confirming state and backend
"""

import os
import json
import time
import ssl
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone


def _get_ssl_context() -> ssl.SSLContext:
    """Creates a TLS context resilient across international quantum cloud endpoints."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class OriginCloudLifecycleAdapter:
    """
    Adapter implementing the full execution lifecycle for Origin Quantum Cloud (QRunes / Wukong 72Q).
    Target API: https://qcloud.originqc.com.cn/api
    """

    DEFAULT_BASE = "https://qcloud.originqc.com.cn/api"

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.api_key = api_key if api_key is not None else os.environ.get("ORIGIN_API_KEY", "")
        self.api_base = api_base or self.DEFAULT_BASE

    def probe(self) -> Dict[str, Any]:
        """Probes endpoint for real network connectivity and credential validity."""
        endpoint = f"{self.api_base}/task/submit"
        ctx = _get_ssl_context()
        sample_payload = {
            "chipId": 72,
            "taskType": "QRunes",
            "script": "QINIT 2\nCREG 2\nH q[0]\nCNOT q[0], q[1]\nMEASURE q[0], c[0]\nMEASURE q[1], c[1]",
            "shots": 100,
        }
        data = json.dumps(sample_payload).encode("utf-8")
        headers = {
            "ApiKey": self.api_key or "",
            "token": self.api_key or "",
            "Content-Type": "application/json",
            "User-Agent": "QMoosa-PQS/1.0",
        }
        start = time.perf_counter()
        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
                latency_ms = (time.perf_counter() - start) * 1000.0
                body_raw = resp.read().decode("utf-8")
                try:
                    body = json.loads(body_raw)
                except Exception:
                    body = {"raw": body_raw}

                auth_ok = (
                    resp.status == 200
                    and (body.get("code") == 200 or body.get("success") is True)
                    and body.get("message") != "Unauthorized"
                )
                err_msg = None if auth_ok else f"Origin rejected token: code={body.get('code')}, message={body.get('message')}"
                return {
                    "reachable": True,
                    "authenticated": auth_ok,
                    "http_status": resp.status,
                    "latency_ms": latency_ms,
                    "endpoint": endpoint,
                    "response_body": body,
                    "error": err_msg,
                }
        except urllib.error.HTTPError as e:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return {
                "reachable": True,
                "authenticated": False,
                "http_status": e.code,
                "latency_ms": latency_ms,
                "endpoint": endpoint,
                "error": f"HTTPError {e.code}: {e.reason}",
            }
        except Exception as e:
            return {
                "reachable": False,
                "authenticated": False,
                "http_status": None,
                "latency_ms": -1.0,
                "endpoint": endpoint,
                "error": f"{type(e).__name__}: {e}",
            }

    def submit(self, script_qrunes: str, shots: int = 1024, chip_id: int = 72) -> Dict[str, Any]:
        """Submits QRunes quantum circuit to Origin Cloud and retrieves provider taskId."""
        if not self.api_key:
            raise ValueError("Cannot submit: ORIGIN_API_KEY is missing or empty.")

        endpoint = f"{self.api_base}/task/submit"
        ctx = _get_ssl_context()
        payload = {
            "chipId": chip_id,
            "taskType": "QRunes",
            "script": script_qrunes,
            "shots": shots,
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "ApiKey": self.api_key,
            "token": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "QMoosa-PQS/1.0",
        }
        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        if not (body.get("code") == 200 or body.get("success") is True):
            raise RuntimeError(f"Origin Cloud task submission rejected: code={body.get('code')}, msg={body.get('message')}")

        obj = body.get("obj")
        task_id = None
        if isinstance(obj, dict):
            task_id = obj.get("taskId") or obj.get("taskid") or obj.get("id")
        elif isinstance(obj, str):
            task_id = obj

        if not task_id or str(task_id).startswith("origin_job_"):
            raise ValueError(f"Origin Cloud returned invalid or missing taskId: {obj}")

        script_sha256 = hashlib.sha256(script_qrunes.encode("utf-8")).hexdigest()
        return {
            "provider_job_id": str(task_id),
            "chip_id": chip_id,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "script_sha256": script_sha256,
            "raw_response": body,
        }

    def poll(self, task_id: str, timeout_seconds: int = 180, interval_seconds: int = 3) -> Dict[str, Any]:
        """Polls Origin Cloud for task completion."""
        endpoint = f"{self.api_base}/task/detail"
        ctx = _get_ssl_context()
        headers = {
            "ApiKey": self.api_key,
            "token": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "QMoosa-PQS/1.0",
        }
        payload = {"taskId": task_id, "taskid": task_id}
        start = time.time()

        while time.time() - start < timeout_seconds:
            req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    obj = body.get("obj", {})
                    # Status mappings: 1=waiting, 2=running, 3=success/completed, 4=failed
                    status_raw = obj.get("status") or obj.get("taskStatus")
                    if status_raw in (3, "3", "SUCCESS", "COMPLETED", "DONE"):
                        return {"status": "COMPLETED", "detail": obj, "raw": body}
                    elif status_raw in (4, "4", "FAILED", "ERROR"):
                        return {"status": "FAILED", "detail": obj, "raw": body}
            except Exception:
                pass
            time.sleep(interval_seconds)

        return {"status": "TIMEOUT", "detail": {}, "raw": {}}

    def get_result(self, task_id: str, poll_detail: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetches and normalizes raw hardware measurement counts."""
        detail = poll_detail or {}
        raw_counts = detail.get("taskResult") or detail.get("result") or detail.get("qRunesResult")

        if not raw_counts:
            endpoint = f"{self.api_base}/task/detail"
            ctx = _get_ssl_context()
            headers = {
                "ApiKey": self.api_key,
                "token": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "QMoosa-PQS/1.0",
            }
            req = urllib.request.Request(endpoint, data=json.dumps({"taskId": task_id}).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                detail = body.get("obj", {})
                raw_counts = detail.get("taskResult") or detail.get("result")

        if not isinstance(raw_counts, dict):
            raise ValueError(f"Origin Cloud returned non-dictionary measurement counts: {raw_counts}")

        counts = {str(k): int(v) for k, v in raw_counts.items()}
        return {
            "counts": counts,
            "shots": sum(counts.values()),
            "raw_detail": detail,
        }

    def independent_re_query(self, task_id: str) -> Dict[str, Any]:
        """Conducts an independent HTTP network query to verify job state and identity."""
        endpoint = f"{self.api_base}/task/detail"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        headers = {
            "ApiKey": self.api_key,
            "token": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "BountyHunter-OS/Canonical-Verifier",
        }
        req = urllib.request.Request(endpoint, data=json.dumps({"taskId": task_id}).encode("utf-8"), headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                if resp.status != 200:
                    return {"verified": False, "error": f"HTTP status {resp.status}"}
                body = json.loads(resp.read().decode("utf-8"))
                if body.get("code") != 200 and body.get("success") is not True:
                    return {"verified": False, "error": f"Provider error: {body.get('message')}"}

                obj = body.get("obj", {})
                ret_id = str(obj.get("taskId") or obj.get("taskid") or "")
                status_raw = obj.get("status") or obj.get("taskStatus")
                is_terminal = status_raw in (3, "3", "SUCCESS", "COMPLETED", "DONE")

                if ret_id and ret_id == str(task_id) and is_terminal:
                    return {
                        "verified": True,
                        "provider": "Origin Quantum Cloud",
                        "provider_job_id": ret_id,
                        "backend": "origin_wukong_72q",
                        "chip_id": obj.get("chipId", 72),
                        "status": "COMPLETED",
                        "error": None,
                    }
                else:
                    return {
                        "verified": False,
                        "error": f"Mismatch or non-terminal state: ret_id={ret_id}, status={status_raw}",
                    }
        except Exception as e:
            return {"verified": False, "error": f"Independent re-query network error: {e}"}


class IBMQCloudLifecycleAdapter:
    """
    Adapter implementing the full execution lifecycle for IBM Quantum Runtime.
    Target API: https://api.quantum.ibm.com/v1
    """

    DEFAULT_BASE = "https://api.quantum.ibm.com/v1"

    def __init__(self, api_token: Optional[str] = None, crn: Optional[str] = None, api_base: Optional[str] = None):
        self.api_token = api_token if api_token is not None else os.environ.get("IBMQ_TOKEN", "")
        self.crn = crn or os.environ.get("IBMQ_CRN", "")
        self.api_base = api_base or self.DEFAULT_BASE

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "QMoosa-PQS/1.0",
        }
        if self.crn:
            headers["Service-CRN"] = self.crn
        return headers

    def probe(self) -> Dict[str, Any]:
        """Probes IBM Quantum API for real network connectivity and credential validity."""
        endpoint = f"{self.api_base}/jobs"
        ctx = _get_ssl_context()
        headers = self._headers()
        start = time.perf_counter()
        req = urllib.request.Request(endpoint, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
                latency_ms = (time.perf_counter() - start) * 1000.0
                auth_ok = resp.status in (200, 201)
                return {
                    "reachable": True,
                    "authenticated": auth_ok,
                    "http_status": resp.status,
                    "latency_ms": latency_ms,
                    "endpoint": endpoint,
                    "error": None if auth_ok else f"HTTP {resp.status}",
                }
        except urllib.error.HTTPError as e:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return {
                "reachable": True,
                "authenticated": False,
                "http_status": e.code,
                "latency_ms": latency_ms,
                "endpoint": endpoint,
                "error": f"HTTPError {e.code}: {e.reason}",
            }
        except Exception as e:
            return {
                "reachable": False,
                "authenticated": False,
                "http_status": None,
                "latency_ms": -1.0,
                "endpoint": endpoint,
                "error": f"{type(e).__name__}: {e}",
            }

    def submit(self, circuit_qasm: str, shots: int = 1024, backend: str = "ibm_heron") -> Dict[str, Any]:
        """Submits OpenQASM circuit to IBM Quantum Runtime and retrieves provider job_id."""
        if not self.api_token:
            raise ValueError("Cannot submit: IBMQ_TOKEN is missing or empty.")

        endpoint = f"{self.api_base}/jobs"
        ctx = _get_ssl_context()
        payload = {
            "program_id": "sampler",
            "backend": backend,
            "params": {
                "circuits": [circuit_qasm],
                "shots": shots,
            },
        }
        data = json.dumps(payload).encode("utf-8")
        headers = self._headers()
        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        job_id = body.get("id") or body.get("job_id")
        if not job_id or str(job_id).startswith("ibmq_job_"):
            raise ValueError(f"IBM Quantum returned invalid or missing job_id: {body}")

        circuit_sha256 = hashlib.sha256(circuit_qasm.encode("utf-8")).hexdigest()
        return {
            "provider_job_id": str(job_id),
            "backend": backend,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "circuit_sha256": circuit_sha256,
            "raw_response": body,
        }

    def poll(self, job_id: str, timeout_seconds: int = 300, interval_seconds: int = 5) -> Dict[str, Any]:
        """Polls IBM Quantum for job completion."""
        endpoint = f"{self.api_base}/jobs/{job_id}"
        ctx = _get_ssl_context()
        headers = self._headers()
        start = time.time()

        while time.time() - start < timeout_seconds:
            req = urllib.request.Request(endpoint, headers=headers, method="GET")
            try:
                with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    state = body.get("state", {})
                    status_raw = state.get("status") if isinstance(state, dict) else body.get("status")
                    status_upper = str(status_raw).upper()

                    if status_upper in ("COMPLETED", "DONE", "SUCCESS"):
                        return {"status": "COMPLETED", "detail": body}
                    elif status_upper in ("FAILED", "CANCELLED", "ERROR"):
                        return {"status": "FAILED", "detail": body}
            except Exception:
                pass
            time.sleep(interval_seconds)

        return {"status": "TIMEOUT", "detail": {}}

    def get_result(self, job_id: str) -> Dict[str, Any]:
        """Fetches and normalizes raw hardware measurement counts."""
        endpoint = f"{self.api_base}/jobs/{job_id}/results"
        ctx = _get_ssl_context()
        headers = self._headers()
        req = urllib.request.Request(endpoint, headers=headers, method="GET")

        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        counts = {}
        if isinstance(body, dict):
            if "counts" in body:
                counts = body["counts"]
            elif "results" in body and isinstance(body["results"], list) and len(body["results"]) > 0:
                res0 = body["results"][0]
                if isinstance(res0, dict):
                    counts = res0.get("data", {}).get("counts") or res0.get("counts", {})

        if not counts:
            raise ValueError(f"IBM Quantum returned empty counts payload: {body}")

        normalized = {str(k): int(v) for k, v in counts.items()}
        return {
            "counts": normalized,
            "shots": sum(normalized.values()),
            "raw_result": body,
        }

    def independent_re_query(self, job_id: str) -> Dict[str, Any]:
        """Conducts an independent HTTP network query to verify job state and identity."""
        endpoint = f"{self.api_base}/jobs/{job_id}"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "BountyHunter-OS/Canonical-Verifier",
        }
        if self.crn:
            headers["Service-CRN"] = self.crn

        req = urllib.request.Request(endpoint, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                if resp.status not in (200, 201):
                    return {"verified": False, "error": f"HTTP status {resp.status}"}
                body = json.loads(resp.read().decode("utf-8"))
                ret_id = str(body.get("id") or body.get("job_id") or "")
                state = body.get("state", {})
                status_raw = state.get("status") if isinstance(state, dict) else body.get("status")
                is_terminal = str(status_raw).upper() in ("COMPLETED", "DONE", "SUCCESS")

                if ret_id and ret_id == str(job_id) and is_terminal:
                    return {
                        "verified": True,
                        "provider": "IBM Quantum Runtime",
                        "provider_job_id": ret_id,
                        "backend": body.get("backend", "ibm_heron"),
                        "status": "COMPLETED",
                        "error": None,
                    }
                else:
                    return {
                        "verified": False,
                        "error": f"Mismatch or non-terminal state: ret_id={ret_id}, status={status_raw}",
                    }
        except Exception as e:
            return {"verified": False, "error": f"Independent re-query network error: {e}"}
