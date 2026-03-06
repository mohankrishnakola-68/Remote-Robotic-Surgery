"""
Quantum Secure Direct Communication (QSDC) Engine
Simulates encoding haptic and control data into quantum states to ensure zero-latency interception detection.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import random

class QSDCEngine:
    def __init__(self, eavesdrop_probability=0.0):
        self.simulator = AerSimulator()
        self.eavesdrop_probability = eavesdrop_probability

    def _create_bell_pair(self):
        """Create an entangled Bell pair (EPR pair)."""
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        return qc

    def encode(self, bit_pair: str):
        """
        Encode a pair of classical bits ('00', '01', '10', '11') using Superdense Coding.
        """
        qc = self._create_bell_pair()
        
        # Apply gates based on the classical bit pair to be sent
        if bit_pair == '01':
            qc.x(0)
        elif bit_pair == '10':
            qc.z(0)
        elif bit_pair == '11':
            qc.z(0)
            qc.x(0)
            
        return qc
        
    def check_eavesdrop(self):
        """
        Determine stochastically whether an eavesdropper intercepts this transmission.
        NOTE: We do NOT apply measure_all() to the main circuit here — doing so would
        collapse the state before decode() runs (double-measurement bug).
        Instead we record the breach flag and abort decoding on the caller side.
        """
        return random.random() < self.eavesdrop_probability

    def decode(self, qc: QuantumCircuit):
        """
        Decode the quantum state back into classical bits.
        The circuit must NOT have been measured before this call.
        """
        qc.cx(0, 1)
        qc.h(0)
        qc.measure_all()

        result = self.simulator.run(qc, shots=1).result()
        counts  = result.get_counts()

        measured_string = list(counts.keys())[0]
        measured_string = measured_string.replace(' ', '')   # strip Qiskit space delimiters
        measured_bits   = measured_string[::-1]              # little-endian → big-endian
        return measured_bits[:2]                             # exactly 2 bits

    def transmit_data(self, data_stream: str):
        """
        Issue 1 & 2 — Latency + Security:
        Transmit a binary string through the simulated QSDC channel.
        Returns (received_bits, security_breached).
        """
        # Pad to even length
        if len(data_stream) % 2 != 0:
            data_stream = '0' + data_stream

        received_stream = ""
        security_breach = False

        for i in range(0, len(data_stream), 2):
            bit_pair = data_stream[i:i+2]

            # 1. Encode into entangled quantum state
            qc = self.encode(bit_pair)

            # 2. Stochastic eavesdrop check (does NOT touch the circuit)
            if self.check_eavesdrop():
                security_breach = True

            if not security_breach:
                # 3. Decode — circuit is still in superposition, safe to measure
                decoded_pair  = self.decode(qc)
                received_stream += decoded_pair
            else:
                # Entanglement collapsed → transmission aborted
                received_stream += "XX"

        return received_stream, security_breach

def int_to_bin_str(value, bits=8):
    """Utility to convert integer to binary string."""
    return format(value, f'0{bits}b')

def bin_str_to_int(bin_str):
    """Utility to convert binary string to integer."""
    try:
        return int(bin_str, 2)
    except ValueError:
        return 0

if __name__ == "__main__":
    engine = QSDCEngine(eavesdrop_probability=0.2)
    
    # Example: Transmitting joystick X value (e.g., 180)
    test_value = 180
    test_data = int_to_bin_str(test_value)
    print(f"Original Value: {test_value} -> Binary: {test_data}")
    
    rx_data, breached = engine.transmit_data(test_data)
    
    print(f"Received Binary: {rx_data} | Security Breached: {breached}")
    if not breached:
        print(f"Decoded Value: {bin_str_to_int(rx_data)}")
