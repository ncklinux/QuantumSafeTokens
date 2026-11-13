import os
import sys
from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("IBM_QUANTUM_TOKEN")

if not API_KEY or API_KEY == "PASTE_YOUR_IBM_CLOUD_API_KEY_HERE":
    print("Error: Please put your IBM Cloud API key in the .env file.")
    sys.exit(1)

print("Connecting to IBM Quantum Platform...")

try:
    # Save credentials locally (stored in ~/.qiskit/qiskit-ibm.json)
    # Both 'ibm_cloud' and 'ibm_quantum_platform' point to the cloud portal
    QiskitRuntimeService.save_account(
        channel="ibm_cloud",
        token=API_KEY,
        set_as_default=True,
        overwrite=True
    )

    # Initialize the service
    service = QiskitRuntimeService()
    print("Authenticated successfully!\n")

    # Fetch available backends (real quantum QPUs)
    backends = service.backends()
    print("Available Quantum Computers on your account:")
    print("-" * 50)
    for b in backends:
        status = b.status()
        print(f" - Name: {b.name:<16} | Pending Jobs: {status.pending_jobs:<3} | Operational: {status.operational}")
    print("-" * 50)

    # Check least busy processor
    least_busy = service.least_busy(operational=True, simulator=False)
    print(f"\nRecommended QPU for deployment (Least busy): {least_busy.name}")

except Exception as e:
    print(f"Connection failed: {e}")
