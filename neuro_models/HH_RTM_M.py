'''
Reduced Traub-Miles neuron model with added M-current
'''
#%%

import numpy as np
import sympy as sym
from scipy.integrate import odeint
from copy import deepcopy

from neuro_py.neuro_models.util import *

# Average potassium, sodium, leak, M-current channel conductance per unit area (mS/cm^2)
_g_K, _g_Na, _g_L, _g_M = sym.symbols('g_K g_Na g_L g_M')
# Average potassium, sodium, leak potentials (mV)
_E_K, _E_Na, _E_L = sym.symbols('E_K E_Na E_L')
# capacitance of membrane, applied current
_C_m, _I_A = sym.symbols('C_m I_A')
# membrane voltage, potassium gating var, leak gating var
_V_m, _n, _h, _w = sym.symbols('V_m n h w')


# rate funcs
_alpha_n, _beta_n, _alpha_n, _beta_n, _alpha_n, _beta_n = sym.symbols('alpha_n beta_n alpha_n beta_n alpha_n beta_n')
# steady states
_n_inf, _m_inf, _h_inf = sym.symbols('n_inf m_inf h_inf')


RTM_consts = {
	_C_m : 1.0,
	_E_Na : 50.0,
	_E_K : -100.0,
	_E_L : -67.0,
	_g_Na : 100.0,
	_g_K : 80.0,
	_g_L : 0.1,
	_g_M : 0.4,
}



# Sodium ion-channel rate functions
_alpha_m = 0.32 * ( 54.0 + _V_m ) / ( 1 - sym.exp( -1 * ( _V_m + 54.0 ) / 4.0 ) )
_beta_m = 0.28 * ( 27.0 + _V_m ) / ( sym.exp( ( _V_m + 27.0 ) / 5.0 ) - 1 )

# leak channel rate values
_alpha_h = 0.128 * sym.exp( - ( _V_m + 50.0 ) / 18 )
_beta_h = 4.0 / ( 1 + sym.exp( -1.0 * ( _V_m + 27.0 ) / 5.0 ))

# Potassium ion-channel rate functions
_alpha_n = 0.032 * ( 52.0 + _V_m ) / ( 1 - sym.exp( -1 * ( _V_m + 52.0 ) / 5.0 ))
_beta_n = 0.5 * sym.exp( - ( _V_m + 57.0 ) / 40.0 )


# n, m, and h steady-state values
_n_inf = _alpha_n / ( _alpha_n + _beta_n )
_m_inf = _alpha_m / ( _alpha_m + _beta_m )
_h_inf = _alpha_h / ( _alpha_h + _beta_h )

_w_inf = 1 / ( 1 + sym.exp( -1 * ( _V_m + 35.0) / 10.0 ) )
_tau_w = 400 / ( 3.3 * sym.exp( ( _V_m + 35.0) / 20.0 ) + sym.exp( -1 * ( _V_m + 35.0) / 20.0 ) )

# Wang-Buzsaki model expressions

# currents
_I_K = _g_K * ( _n ** 4.0) * ( _V_m - _E_K )
_I_Na = _g_Na * ( _m_inf ** 3.0 ) * _h * (_V_m - _E_Na)
_I_L = _g_L * (_V_m - _E_L)
_I_M = _g_M * _w * ( _V_m - _E_K )

# diffeqs

RTM_dv_dt = ( _I_A - _I_K - _I_Na - _I_L - _I_M) / _C_m
RTM_dn_dt = ( _alpha_n * ( 1.0 - _n ) ) - ( _beta_n * _n )
RTM_dh_dt = ( _alpha_h * ( 1.0 - _h ) ) - ( _beta_h * _h )
RTM_dw_dt = ( _w_inf - _w ) / _tau_w



def get_model():
	return NM_model(
		name_in = 'Reduced Traub-Miles Model with M-current',
		model_naming_in = [
			'voltage / dt',
			'K current / dt',
			'leak current / dt',
		],
		model_expr_in = [
			RTM_dv_dt,
			RTM_dn_dt,
			RTM_dh_dt,
			RTM_dw_dt,
		],
		lst_vars_in = [ _V_m, _n, _h, _w ],
		dict_syms = deepcopy(RTM_consts),
		stim_sym_in = _I_A,
		dict_units = None,
	)