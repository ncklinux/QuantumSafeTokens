import os
import sys
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

load_dotenv()

class QuantumRandomGenerator:
    def __init__(self, use_real_hardware=False):
        """
        Initializes the QRNG generator.
        :param use_real_hardware: If True, executes on IBM's physical QPUs.
                                  If False, uses local simulation.
        """
        self.use_real_hardware = use_real_hardware
        self.backend = None

        if self.use_real_hardware:
            print("Connecting to IBM Quantum cloud...")
            service = QiskitRuntimeService()
            # Select least busy operational real quantum computer
            self.backend = service.least_busy(operational=True, simulator=False)
            print(f"Target Hardware Selected: {self.backend.name}")
        else:
            from qiskit_aer import AerSimulator
            self.backend = AerSimulator()
            print("Running locally on Quantum Simulator (AerSimulator)")

    def get_quantum_random_bytes(self, num_bytes=16):
        """
        Creates an 8-qubit Hadamard circuit and samples 'num_bytes' measurements.
        Each shot produces 8 random bits = 1 true quantum random byte.
        """
        # Build 8-qubit superposition circuit
        qc = QuantumCircuit(8, 8)
        qc.h(range(8))
        qc.measure(range(8), range(8))

        if self.use_real_hardware:
            # Transpile circuit for the hardware architecture
            pm = generate_preset_pass_manager(backend=self.backend, optimization_level=1)
            isa_circuit = pm.run(qc)

            # Submit batch job to SamplerV2
            print(f"Submitting job ({num_bytes} shots) to cloud queue...")
            sampler = Sampler(self.backend)
            job = sampler.run([isa_circuit], shots=num_bytes)
            print(f"Job ID: {job.job_id()} | Waiting for results...")
            
            result = job.result()
            # Read measured bitstrings from classical register 'c'
            pub_result = result[0]
            data_bin = pub_result.data
            creg_name = list(data_bin.keys())[0]
            bitstrings = data_bin[creg_name].get_bitstrings()
        else:
            # Fast local simulator
            job = self.backend.run(qc, shots=num_bytes, memory=True)
            bitstrings = job.result().get_memory()

        # Convert 8-bit quantum strings (e.g. '10110010') to integer bytes (0-255)
        return [int(b, 2) for b in bitstrings]


def generate_quantum_api_key(qrng, length_bytes=16):
    """Generates a secure hex API key for IT Admin / Cloud Access."""
    raw_bytes = bytes(qrng.get_quantum_random_bytes(length_bytes))
    return f"sk_live_quantum_{raw_bytes.hex()}"


def generate_quantum_otp(qrng):
    """Generates a 6-digit SMS verification code for E-Commerce checkout."""
    b = qrng.get_quantum_random_bytes(3)
    val = (b[0] << 16) | (b[1] << 8) | b[2]
    return f"{val % 1_000_000:06d}"


# Run test
if __name__ == "__main__":
    print("=" * 55)
    print("QuantumSafeTokens - True Randomness Generator")
    print("=" * 55)

    # Change to use_real_hardware=True whenever you want to test on IBM Cloud QPUs!
    # Set to False for instant (0.1s) local testing.
    USE_HARDWARE = False

    qrng = QuantumRandomGenerator(use_real_hardware=USE_HARDWARE)

    print("\n[1] Generating Quantum SMS Checkout OTP...")
    otp = generate_quantum_otp(qrng)
    print(f"Verified Customer OTP: {otp}")

    print("\n[2] Generating Quantum Admin Cloud API Key...")
    api_key = generate_quantum_api_key(qrng, length_bytes=16)
    print(f"Admin API Token: {api_key}")

    print("\n" + "=" * 55)
    print("All quantum tokens successfully generated!")
    print("=" * 55)
