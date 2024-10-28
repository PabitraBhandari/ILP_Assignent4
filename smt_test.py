import os
import m5
from m5.objects import *

# Path to the benchmark binaries
integer_benchmark = "/Users/cristbhandari/gem5/configs/sample/bm_test/integer_test"
floating_point_benchmark = "/Users/cristbhandari/gem5/configs/sample/bm_test/fp_test"

# Create the system
system = System()
system.multi_thread = True  # Enable multi-threading support
system.clk_domain = SrcClockDomain(clock="2GHz", voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Set up an SMT-capable CPU
system.cpu = X86O3CPU()
system.cpu.numThreads = 2  # Enable two threads for SMT

# Configure superscalar properties and SMT
system.cpu.fetchWidth = 4
system.cpu.decodeWidth = 4
system.cpu.issueWidth = 4
system.cpu.commitWidth = 4
system.cpu.squashWidth = 4

# Memory and bus setup
system.membus = SystemXBar()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Set up interrupt controller for x86 with proper connections
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# For the second hardware thread (SMT)
system.cpu.interrupts[1].pio = system.membus.mem_side_ports
system.cpu.interrupts[1].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[1].int_responder = system.membus.mem_side_ports

# Create memory controller and connect to the bus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect the system port to the memory bus
system.system_port = system.membus.cpu_side_ports

# Set up workloads with multiple threads and unique PIDs
process_1 = Process()
process_1.cmd = [integer_benchmark]
process_1.pid = 100  # Assign a unique PID to the first process

process_2 = Process()
process_2.cmd = [floating_point_benchmark]
process_2.pid = 101  # Assign a different PID to the second process

# Assign the processes to different threads
system.workload = SEWorkload.init_compatible(integer_benchmark)
system.cpu.workload = [process_1, process_2]
system.cpu.createThreads()

# Root and simulation instantiation
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting SMT simulation with integer and floating-point benchmarks...")
exit_event = m5.simulate(1_000_000_000)
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

# Dump statistics
m5.stats.dump()
m5.stats.reset()
