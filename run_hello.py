import m5
import os
from m5.objects import *

# Create the system
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Use an out-of-order CPU model for ILP analysis
system.cpu = X86O3CPU()

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

# Define the path to the X86 'hello' binary and ensure it exists
binary_path = "/Users/cristbhandari/gem5/tests/test-progs/hello/bin/x86/linux/hello"
if not os.path.isfile(binary_path):
    raise FileNotFoundError(f"Binary not found at: {binary_path}")

# Set up the workload using the SE mode-compatible 'hello' binary
system.workload = SEWorkload.init_compatible(binary_path)

# Set up a process for running the 'hello' program
hello_process = Process()
hello_process.cmd = [binary_path]
system.cpu.workload = hello_process
system.cpu.createThreads()

# Instantiate the system and prepare for simulation
root = Root(full_system=False, system=system)
m5.instantiate()

# Start simulation and display initial message
print(f"Starting simulation with the 'hello' program located at: {binary_path}")
exit_event = m5.simulate()

# Display simulation exit information
print(f"Simulation completed at tick {m5.curTick()} due to: {exit_event.getCause()}")
