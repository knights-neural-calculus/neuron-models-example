'''
Hodgkin-Huxley neuron model
'''

#%%

import numpy as np
# import mpmath as mp
import sympy as sym
from scipy.integrate import odeint

from neuro_models.util import *

# Average potassium, sodium, leak channel conductance per unit area (mS/cm^2)
_g_K, _g_Na, _g_L = sym.symbols('g_K g_Na g_L')
# Average potassium, sodium, leak potentials (mV)
_E_K, _E_Na, _E_L = sym.symbols('E_K E_Na E_L')
# capacitance of membrane, applied current
_C_m, _I_A = sym.symbols('C_m I_A')
# membrane voltage, potassium gating var, sodium gating var, leak gating var
_V_m, _n, _m, _h = sym.symbols('V_m n m h')


# rate funcs
_alpha_n, _beta_n, _alpha_n, _beta_n, _alpha_n, _beta_n = sym.symbols('alpha_n beta_n alpha_n beta_n alpha_n beta_n')
# steady states
_n_inf, _m_inf, _h_inf = sym.symbols('n_inf m_inf h_inf')


HH_consts = {
	_g_K : 36.0,
	_g_Na : 120.0,
	_g_L : 0.3,
	_E_K : -77.0,
	_E_Na : 50.0,
	_E_L : -54.4,
	_C_m : 1.0,
}


# Potassium ion-channel rate functions
_alpha_n = - 0.01 * ( _V_m + 55.0 )/( sym.exp(-( _V_m + 55.0 )/10)-1)
_beta_n = 0.125 * sym.exp(-( _V_m + 65.0 )/80)

# Sodium ion-channel rate functions
_alpha_m = -0.1 * ( _V_m + 40.0 ) / ( sym.exp(-(_V_m + 40.0)/10)-1 )
_beta_m = 4 * sym.exp(-( _V_m + 65 )/18)

# leak channel rate values
_alpha_h = 0.07 * sym.exp( -( _V_m + 65 )/20 )
_beta_h = 1.0 / (sym.exp(-( _V_m + 35 )/10)+1)


# n, m, and h steady-state values
_n_inf = _alpha_n / ( _alpha_n + _beta_n )
_m_inf = _alpha_m / ( _alpha_m + _beta_m )
_h_inf = _alpha_h / ( _alpha_h + _beta_h )
  

# Erisir model expressions

# currents
_I_K = _g_K * (_n ** 4.0) * ( _V_m - _E_K )
_I_Na = _g_Na * ( _m ** 3.0 ) * _h * (_V_m - _E_Na)
_I_L = _g_L * (_V_m - _E_L)

# diffeqs

HH_dv_dt = ( _I_A - _I_K - _I_Na - _I_L ) / _C_m
HH_dn_dt = ( _alpha_n * ( 1.0 - _n ) ) - ( _beta_n * _n )
HH_dm_dt = ( _alpha_m * ( 1.0 - _m ) ) - ( _beta_m * _m)
HH_dh_dt = ( _alpha_h * ( 1.0 - _h ) ) - ( _beta_h * _h )

# Rate Function Constants (RFC)
rfc = {
	'an_1' :  95.0,
	'an_2' :  11.8,
	
	'bn_1' :  0.025,
	'bn_2' :  22.222,
	
	'am_1' :  75.0,
	'am_2' :  40.0,
	'am_3' :  13.5,
	
	'bm_1' :  1.2262,
	'bm_2' :  42.248,
	
	'ah_1' :  0.0035,
	'ah_2' :  24.186,
	
	'bh_1' :  -0.017,
	'bh_2' :  51.25,
	'bh_3' :  5.2,
}


def get_model_HH():
	return NM_model(
		name_in = 'Hodgkin-Huxley model',
		model_naming_in = [
			'voltage / dt',
			'K gate rate / dt',
			'Na gate rate / dt',
			'leak gate rate / dt',
		],
		model_expr_in = [
			HH_dv_dt,
			HH_dn_dt,
			HH_dm_dt,
			HH_dh_dt,
		],
		lst_vars_in = [ _V_m, _n, _m, _h ],
		dict_syms = HH_consts,
		stim_in = (_I_A, None),
		dict_units = None,
		steady_in = np.array([
			-65.0, 
			0.052934217620864, 
			0.596111046346827,
			0.317681167579781,
		])
	)

