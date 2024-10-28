import m5
import os
from m5.objects import *

# Create the system
system = System()
system.clk_domain = SrcClockDomain(clock="2GHz", voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('1GB')]

# Use an out-of-order CPU model for ILP analysis
system.cpu = X86O3CPU()

# Superscalar Configuration
system.cpu.decodeWidth = 4
system.cpu.issueWidth = 4
system.cpu.dispatchWidth = 4
system.cpu.commitWidth = 4
system.cpu.fetchWidth = 4

# Add a branch predictor
system.cpu.branchPred = BiModeBP()

# Set up the memory bus
system.membus = SystemXBar()

# Attach CPU caches to the memory bus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Create interrupt controller for the CPU and connect to the memory bus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Configure memory controller with DDR3 and connect to the bus
mem_ctrl = MemCtrl()
mem_ctrl.dram = DDR3_1600_8x8()
mem_ctrl.dram.range = system.mem_ranges[0]
mem_ctrl.port = system.membus.mem_side_ports
system.mem_ctrl = mem_ctrl

# Connect the system port to the memory bus
system.system_port = system.membus.cpu_side_ports

# Define the path to the different benchmark binaries
binary_paths = {
    "integer_test": "/Users/cristbhandari/gem5/configs/sample/bm_test/integer_test",
    "floating_point_test": "/Users/cristbhandari/gem5/configs/sample/bm_test/fp_test",
    "memory_test": "/Users/cristbhandari/gem5/configs/sample/bm_test/memory_test"
}

# Choose a benchmark to run
benchmark = "memory_test"  # Run the memory benchmark

# Validate the chosen binary path
binary_path = binary_paths.get(benchmark)
if not binary_path or not os.path.isfile(binary_path):
    raise FileNotFoundError(f"Binary not found at: {binary_path}")

# Set up the workload using the SE mode-compatible binary
system.workload = SEWorkload.init_compatible(binary_path)

# Set up a process for running the selected benchmark program
benchmark_process = Process()
benchmark_process.cmd = [binary_path]
system.cpu.workload = benchmark_process
system.cpu.createThreads()

# Instantiate the system and prepare for simulation
root = Root(full_system=False, system=system)
m5.instantiate()

# Start simulation and display initial message
print(f"Starting simulation with the '{benchmark}' program on a superscalar processor.")
exit_event = m5.simulate()

# Display simulation exit information
print(f"Simulation completed at tick {m5.curTick()} due to: {exit_event.getCause()}")
