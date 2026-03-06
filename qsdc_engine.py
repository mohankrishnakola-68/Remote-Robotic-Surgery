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
        
    def eavesdrop(self, qc: QuantumCircuit):
        """
        Simulate an eavesdropping attempt which collapses the quantum state.
        """
        if random.random() < self.eavesdrop_probability:
            # Eavesdropper measures the qubit in transit (qubit 0)
            qc.measure_all()
            return True
        return False

    def decode(self, qc: QuantumCircuit):
        """
        Decode the quantum state back into classical bits.
        """
        qc.cx(0, 1)
        qc.h(0)
        qc.measure_all()
        
        result = self.simulator.run(qc, shots=1).result()
        counts = result.get_counts()
        
        # Get the first (and only) measurement result
        measured_string = list(counts.keys())[0]
        
        # Provide logic to clean up any space delimiters that Qiskit sometimes adds
        measured_string = measured_string.replace(' ', '')
        
        # Using little-endian by default in Qiskit, so [::-1] 
        measured_bits = measured_string[::-1] 
        return measured_bits[:2] # ensure exactly 2 bits

    def transmit_data(self, data_stream: str):
        """
        Simulate the transmission of a binary string, detecting any eavesdropping.
        Returns the received string and a boolean indicating if security was breached.
        """
        # Pad with leading '0' if odd length
        if len(data_stream) % 2 != 0:
            data_stream = '0' + data_stream 
            
        received_stream = ""
        security_breach = False
        
        # Process 2 bits at a time
        for i in range(0, len(data_stream), 2):
            bit_pair = data_stream[i:i+2]
            
            # Encode classical bits into entangled qubit states
            qc = self.encode(bit_pair)
            
            # Simulate transit & potential eavesdropping interception
            if self.eavesdrop(qc):
                security_breach = True
                
            if not security_breach:
                # Decode quantum states back to classical representation
                decoded_pair = self.decode(qc)
                received_stream += decoded_pair
            else:
                # If breached, the entangled state is destroyed; transmission aborted / corrupted
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
