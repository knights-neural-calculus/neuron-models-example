# originally copied from
# https://gist.github.com/giuseppebonaccorso/60ce3eb3a829b94abf64ab2b7a56aaef

#%%

import matplotlib.pyplot as plt
import numpy as np

from scipy.integrate import odeint

# * consts

# Set random seed (for reproducibility)
np.random.seed(1000)

# Average potassium channel conductance per unit area (mS/cm^2)
gK = 224.0

# Average sodium channel conductance per unit area (mS/cm^2)
gNa = 112.0

# Average leak channel conductance per unit area (mS/cm^2)
gL = 0.5

# Membrane capacitance per unit area (uF/cm^2)
Cm = 1.0

# Potassium potential (mV)
E_K = -90.0

# Sodium potential (mV)
E_Na = 60.0

# Leak potential (mV)
E_L = -70.0

# Time values
tmin = 0
# tmax = 150
# tmax = 500
tmax = 1150
dt = 0.01

# * funcs

# Potassium ion-channel rate functions

def alpha_n(Vm):
	anv = 95.0
	return ( anv - Vm )/( np.exp( ( anv - Vm ) / 11.8 ) - 1)

def beta_n(Vm):
	return 0.025 * np.exp( - Vm / 22.222 )

# Sodium ion-channel rate functions

def alpha_m(Vm):
	amv = 75.5
	return 40 * ( amv - Vm ) / ( np.exp( ( amv - Vm ) / 13.5 ) - 1)

def beta_m(Vm):
	return 1.2262 * np.exp( - Vm  / 42.248 )

# leak channel rate values

def alpha_h(Vm):
	return 0.0035 * np.exp( - Vm / 24.186 )

def beta_h(Vm):
	return -0.017 * ( Vm + 51.25 ) / ( np.exp( - ( Vm + 51.25 ) / 5.2 ) - 1 )
  
# n, m, and h steady-state values

def n_inf(Vm=0.0):
	return alpha_n(Vm) / (alpha_n(Vm) + beta_n(Vm))

def m_inf(Vm=0.0):
	return alpha_m(Vm) / (alpha_m(Vm) + beta_m(Vm))

def h_inf(Vm=0.0):
	return alpha_h(Vm) / (alpha_h(Vm) + beta_h(Vm))
  





def compute(
		stim,
		# State (Vm, n, m, h)
		IC = np.array([
			-69.83,
			0.0, # 0.052934217620864, 
			0.0, # 0.317681167579781,
		]),
		T = np.linspace(tmin, tmax, (tmax-tmin)//dt), 
		bln_plot = True
	):

	# Compute derivatives
	def compute_derivatives(y, t0):
		dy = np.zeros((3,))
		
		Vm = y[0]
		n = y[1]
		h = y[2]
		
		# dVm/dt
		GK = (gK / Cm) * np.power(n, 2.0)
		GL = gL / Cm
		
		dy[0] = (
			(stim(t0) / Cm) 		# stimulus current
			- (GK * (Vm - E_K)) 	# potassium
			- ( (gNa / Cm) * np.power( m_inf(Vm), 3.0 ) * h * (Vm - E_Na)) 	# sodium
			- (GL * (Vm - E_L))		# leak
		)
		
		# dn/dt
		dy[1] = (alpha_n(Vm) * (1.0 - n)) - (beta_n(Vm) * n)
		
		# dh/dt
		dy[2] = (alpha_h(Vm) * (1.0 - h)) - (beta_h(Vm) * h)
		
		return dy

	# Solve ODE system
	Vy = odeint(compute_derivatives, IC, T)

	
	if bln_plot:
		Idv = [stim(t) for t in T]
		
		# fig, ax = plt.subplots(figsize=(12, 7))
		# ax.plot(T, Idv, 'r-')
		# ax.set_xlabel('Time (ms)')
		# ax.set_ylabel(r'Current density (uA/$cm^2$)')
		# ax.set_title('Stimulus (Current density)')

		# Neuron potential
		fig, ax = plt.subplots(figsize=(12, 7))
		ax.plot(T, Vy[:, 0], 'b-')
		ax.set_xlabel('Time (ms)')
		ax.set_ylabel('Vm (mV)')
		ax.set_title('Neuron potential with two spikes')
		plt.grid()

		ax.plot(T, [x - 57.5 for x in Idv], 'r-')

		# plt.show()
	
	return (T, Vy)

#%%
