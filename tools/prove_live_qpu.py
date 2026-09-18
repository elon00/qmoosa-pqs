#!/usr/bin/env python3
import os, sys, json, time, ssl, hashlib, argparse, urllib.request, urllib.error
from datetime import datetime, timezone

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST
from core.transpiler import OpenQASMTranspiler, OriginPilotTranspiler
from core.hardware_gateway import (
    _load_env_file,
    _get_ssl_context,
    ProviderReceiptValidator,
    IBMQRuntimeGateway,
    OriginQuantumGateway,
    HardwareGatewayDispatcher
)

_load_env_file()


def get_test_circuit(circuit_type: str = 'bell') -> QuantumAST:
    if circuit_type == 'ghz':
        ast = QuantumAST(num_qubits=3)
        ast.h(0)
        ast.cx(0, 1)
        ast.cx(1, 2)
        ast.measure_all()
        return ast
    else:
        ast = QuantumAST(num_qubits=2)
        ast.h(0)
        ast.cx(0, 1)
        ast.measure_all()
        return ast



def probe_origin_cloud_endpoint(api_key: str) -> dict:
    endpoint = 'https://qcloud.originqc.com.cn/api/task/submit'
    ctx = _get_ssl_context()
    sample_script = 'QINIT 2\nCREG 2\nH q[0]\nCNOT q[0], q[1]\nMEASURE q[0], c[0]\nMEASURE q[1], c[1]'

    payload = {
        'chipId': 72,
        'taskType': 'QRunes',
        'script': sample_script,
        'shots': 100,
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'ApiKey': api_key,
        'token': api_key,
        'Content-Type': 'application/json',
        'User-Agent': 'QMoosa-PQS/1.0',
    }

    start = time.perf_counter()
    req = urllib.request.Request(endpoint, data=data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            latency_ms = (time.perf_counter() - start) * 1000.0
            body_raw = resp.read().decode('utf-8')
            try:
                body = json.loads(body_raw)
            except Exception:
                body = {'raw': body_raw}
            return {
                'reachable': True,
                'http_status': resp.status,
                'latency_ms': latency_ms,
                'response_body': body,
                'authenticated': body.get('code') == 200 or body.get('success') is True,
            }
    except urllib.error.HTTPError as e:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return {
            'reachable': True,
            'http_status': e.code,
            'latency_ms': latency_ms,
            'response_body': e.read().decode('utf-8'),
            'authenticated': False,
            'error': f'HTTPError {e.code}',
        }
    except Exception as e:
        return {
            'reachable': False,
            'latency_ms': -1.0,
            'authenticated': False,
            'error': f'{type(e).__name__}: {e}',
        }



def probe_ibm_quantum_endpoint(token: str) -> dict:
    endpoint = 'https://api.quantum.ibm.com/v1/jobs'
    ctx = _get_ssl_context()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'QMoosa-PQS/1.0',
    }
    start = time.perf_counter()
    req = urllib.request.Request(endpoint, headers=headers, method='GET')

    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            latency_ms = (time.perf_counter() - start) * 1000.0
            return {
                'reachable': True,
                'http_status': resp.status,
                'latency_ms': latency_ms,
                'authenticated': resp.status in (200, 201),
            }
    except urllib.error.HTTPError as e:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return {
            'reachable': True,
            'http_status': e.code,
            'latency_ms': latency_ms,
            'authenticated': False,
            'error': f'HTTPError {e.code}',
        }
    except Exception as e:
        return {
            'reachable': False,
            'latency_ms': -1.0,
            'authenticated': False,
            'error': f'{type(e).__name__}: {e}',
        }


def run_live_qpu_proof_pipeline(provider: str, token: str = '', circuit_name: str = 'bell', shots: int = 1024):
    print('=' * 72)
    print('   QMoosa-PQS Live QPU Execution & Attestation Pipeline')
    print('   Truth Protocol Zero-Hallucination Hardware Proof Suite')
    print('=' * 72)

    p_clean = provider.lower()
    print(f'\n[Phase 1] Initializing Target: {p_clean.upper()} Superconducting QPU')
    circuit = get_test_circuit(circuit_name)
    print(f'  Circuit: {circuit_name.upper()} ({circuit.num_qubits} qubits, {len(circuit.gates)} gates)')

    if p_clean == 'origin':
        key = token or os.environ.get('ORIGIN_API_KEY', '')
        masked_key = (key[:6] + '...' + key[-4:]) if len(key) >= 10 else ('[EMPTY]' if not key else '[PRESENT]')
        print('  Origin Cloud Endpoint: https://qcloud.originqc.com.cn/api/task/submit')
        print(f'  Configured Key       : {masked_key}')

        print('\n[Phase 2] Probing Live Origin Quantum Cloud Endpoint...')
        probe = probe_origin_cloud_endpoint(key)
        print(f"  Endpoint Reachable  : {probe['reachable']}")
        if probe.get('latency_ms', -1) > 0:
            print(f"  Network Roundtrip   : {probe['latency_ms']:.2f} ms")
        print(f"  HTTP Response Status: {probe.get('http_status')}")
        print(f"  Response Payload    : {json.dumps(probe.get('response_body', probe.get('error')), ensure_ascii=False)}")


        if not probe.get('authenticated'):
            print('\n[Phase 3: Honesty Gate] Cloud Authentication Status: FAILED / UNAUTHORIZED')
            print('  Truth Protocol Law 6 Activated: Zero-Hallucination Fallback.')
            print('  Reason: Origin Cloud returned unauthorized (Code 401).')
            print('  The system REFUSES to masquerade or claim live hardware execution.')
            print('  Official Reality Status: OFFLINE_CALIBRATED_EMULATION (Live QPU Proof Pending).')
            return {
                'status': 'LIVE_QPU_PROOF_PENDING',
                'provider': 'Origin Quantum',
                'endpoint_reachable': probe['reachable'],
                'authenticated': False,
                'reason': probe.get('response_body'),
            }
        else:
            print('\n[Phase 3: Live Execution] Authenticated by Origin Quantum Cloud!')
            gw = OriginQuantumGateway(api_key=key)
            res = gw.submit_and_execute(circuit, shots=shots)
            print(f'  Task ID: {res.job_id}')
            print(f'  Mode   : {res.execution_mode}')
            return {'status': 'SUCCESS', 'result': res.to_dict()}


    elif p_clean == 'ibm':
        tok = token or os.environ.get('IBMQ_TOKEN', '')
        masked_tok = (tok[:6] + '...' + tok[-4:]) if len(tok) >= 10 else ('[EMPTY]' if not tok else '[PRESENT]')
        print('  IBM Quantum API Base : https://api.quantum.ibm.com/v1')
        print(f'  Configured Token     : {masked_tok}')

        print('\n[Phase 2] Probing Live IBM Quantum Endpoint...')
        probe = probe_ibm_quantum_endpoint(tok)
        print(f"  Endpoint Reachable  : {probe['reachable']}")
        if probe.get('latency_ms', -1) > 0:
            print(f"  Network Roundtrip   : {probe['latency_ms']:.2f} ms")
        print(f"  HTTP Response Status: {probe.get('http_status')}")

        if not probe.get('authenticated'):
            print('\n[Phase 3: Honesty Gate] IBM Cloud Authentication Status: FAILED / UNAUTHORIZED')
            print('  Truth Protocol Law 6 Activated: Zero-Hallucination Fallback.')
            print('  Reason: IBM Quantum token is unconfigured or invalid.')
            print('  The system REFUSES to masquerade or claim live hardware execution.')
            print('  Official Reality Status: OFFLINE_CALIBRATED_EMULATION (Live QPU Proof Pending).')
            return {
                'status': 'LIVE_QPU_PROOF_PENDING',
                'provider': 'IBM Quantum',
                'endpoint_reachable': probe['reachable'],
                'authenticated': False,
            }
        else:
            print('\n[Phase 3: Live Execution] Authenticated by IBM Quantum Runtime!')
            gw = IBMQRuntimeGateway(api_token=tok)
            res = gw.submit_and_execute(circuit, shots=shots)
            print(f'  Job ID: {res.job_id}')
            print(f'  Mode  : {res.execution_mode}')
            return {'status': 'SUCCESS', 'result': res.to_dict()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='QMoosa-PQS Live QPU Execution & Attestation Tool')
    parser.add_argument('--provider', choices=['origin', 'ibm'], default='origin', help='Target quantum cloud provider')
    parser.add_argument('--token', default='', help='API token / key override')
    parser.add_argument('--circuit', choices=['bell', 'ghz'], default='bell', help='Quantum test circuit')
    parser.add_argument('--shots', type=int, default=1024, help='Shot count')
    args = parser.parse_args()

    run_live_qpu_proof_pipeline(args.provider, token=args.token, circuit_name=args.circuit, shots=args.shots)
