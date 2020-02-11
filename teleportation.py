from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister

def H_gate(qt_circuit, qt_reg, nums):
    ''' Apply H gates to a set of qubits.
        Args:
          qt_circuit - quantum circuit;
          qt_reg - quantum register;
          nums - list of qubit numbers.
	'''
    for i in nums:
        qt_circuit.h(qt_reg[i])

def measure(qt_circuit, qt_reg, c_reg, nums):
    ''' Measurement of multiple qubits.
        Args:
          qt_circuit - quantum circuit;
          qt_reg - quantum register;
          c_reg - classical register;
          nums - list of qubit numbers.
	'''
    for i in nums:
        qt_circuit.measure(qt_reg[i], c_reg[i])

def cxIfRev(qt_circuit, q1, q2, revs=0, md=0):
    ''' CX gate. This function was needed when all connections between qubits were unidirectional.
        Args:
          qt_circuit - quantum circuit;
          q1, q2 - qubits;
          revs - revs equals 0 if the changing of the gate direction is necessary;
		  md - md equals 1 or 2 if one of the H gates applied to the second qubit is truncated.
	'''
    if revs == 0:
        qt_circuit.h(q1)
        if md != 2:
            qt_circuit.h(q2)
        qt_circuit.cx(q2, q1)
        qt_circuit.h(q1)
        if md != 1:
            qt_circuit.h(q2)
    else:
        qt_circuit.cx(q1, q2)

def cxConnect(qt_circuit, q1, q2, q3, barrs=False):
	''' CX gate between qubits that are not connected physically.
		Args:
          qt_circuit - quantum circuit;
          q1, q2 - disconnected qubits;
		  q3 - ancilla qubit which is connected to q1 and q2;
		  barrs - parameter equals True if barriers are added.
	'''
    qt_circuit.cx(q1, q3)
    if barrs:
        qt_circuit.barrier()
    cxIfRev(qt_circuit, q3, q2, 0,1)
    qt_circuit.cx(q1, q3)
    if barrs:
        qt_circuit.barrier()
    cxIfRev(qt_circuit, q3, q2, 0,2)
    if barrs:
        qt_circuit.barrier()

def telep(numq, qNum=5, revs=0, bellstate=0, barrs=False, HBase=False):
    ''' Teleportation of Bell states.
		Args:
			numq = [a,b,c,d,e] - order of computer qubits in the teleportation 
				circuit, where a is the physical qubit number which corresponds to the top 
				one of the circuit and so on;
			qNum - number of qubits in generated circuit;
       		revs=0 - there is no need to change direction of the connection 
				between c and e;
       		bellstate - the teleportated Bell state:
            	0 - (|00>+|11>)/2^0.5
            	1 - (|01>+|11>)/2^0.5
            	2 - (|00>-|11>)/2^0.5
            	3 - (|10>-|01>)/2^0.5
        	barrs - if it equals True, barriers are added;
			HBase=True - measurement in Hadamard basis.
		Returns:
			qt_circuit - quantum circuit of the teleportation;
			q_reg - quantum register;
			c_reg - classical register.
	'''
	if qNum < 5:
		qNum = 5
	
    q_reg = QuantumRegister(qNum, 'q')
    c_reg = ClassicalRegister(qNum, 'c')
    qt_circuit = QuantumCircuit(q_reg, c_reg)
    
    # a1 and а5 are disconnected, а2 and а3 are disconnected
    a1 = q_reg[numq[0]] #a
    a2 = q_reg[numq[1]] #b
    a3 = q_reg[numq[2]] #c
    a4 = q_reg[numq[3]] #d
    a5 = q_reg[numq[4]] #e
    
    # Initial state
    if bellstate // 2 == 1:
        qt_circuit.x(a1)
    qt_circuit.h(a1)
    if bellstate % 2 == 1:
        qt_circuit.x(a2)
    
    qt_circuit.cx(a1, a2)
    
    qt_circuit.h(a3)
    qt_circuit.cx(a3, a4)
    cxIfRev(qt_circuit, a3, a5, revs)
    
    if barrs:
        qt_circuit.barrier()
    # Operations after initialization
    qt_circuit.h(a2)
    if barrs:
        qt_circuit.barrier()
    cxConnect(qt_circuit, a2, a3, a4, barrs)
    if barrs:
        qt_circuit.barrier()
    qt_circuit.h(a2)
    if barrs:
        qt_circuit.barrier()
    qt_circuit.cx(a3, a4)
    qt_circuit.h(a4)
    qt_circuit.cx(a2, a4)
    qt_circuit.h(a4)
    if barrs:
        qt_circuit.barrier()
    cxIfRev(qt_circuit, a3, a5, revs)
    if barrs:
        qt_circuit.barrier()
    qt_circuit.cx(a5, a4)
    qt_circuit.cx(a1, a4)
    if barrs:
        qt_circuit.barrier()
    qt_circuit.h(a5)
    if barrs:
        qt_circuit.barrier()
    cxConnect(qt_circuit, a5, a1, a4, barrs)
    if barrs:
        qt_circuit.barrier()    
    # Measurement
    if HBase:
        H_gate(qt_circuit, q_reg, [numq[2], numq[3]])
    measure(qt_circuit, q_reg, c_reg, [numq[2], numq[3]]) # a4, a5
    
    return qt_circuit, q_reg, c_reg

def svres(counts, flname):  
	''' Write results to a file.
		Args:
			counts - dictionary with results;
			flname - a string to specify a file name.
	'''
    fl = open("res_"+flname+".py", 'w')
    fl.write("counts = { \n")
    for k in sorted(counts.keys()):
        fl.write("'%s':%d, \n" % (k, counts[k]))
    fl.write("}")
    fl.close()
