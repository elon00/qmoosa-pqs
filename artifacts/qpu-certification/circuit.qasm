# Origin Pilot / QPanda QRunes Specification
# Compiled via QMoosa-PQ Synthesis Engine
import pyqpanda as pq

def run_origin_pilot_circuit():
    machine = pq.CPUQVM()
    machine.init_qvm()
    q = machine.qAlloc_many(2)
    c = machine.cAlloc_many(2)
    prog = pq.QProg()

    prog << pq.H(q[0])
    prog << pq.CNOT(q[0], q[1])
    prog << pq.Measure(q[0], c[0])
    prog << pq.Measure(q[1], c[1])

    # Run on Origin Pilot Virtual Machine
    result = machine.directly_run(prog)
    print('Origin Pilot Execution Result:', result)
    machine.finalize()
    return result

if __name__ == '__main__':
    run_origin_pilot_circuit()