# The lowercase part of the ECs that use this dict in the same pass
# refer to the same other region (which has an RC to the other region
# in the desired bmap).

# A = desired source (or target)
# B = old target (or source)
# C = old source (or target) to which A has an RC

# Answering the question, How should we update our tentative
# conclusion -- that ___ amount of A connects to ___ amount of B --
# given that ___ amount of C connects to ___ amount of B?

# Notes:
# (1) For 'B' at least, lowercase EC doesn't matter.
#
# (2) Tentative conclusion will never be 'Nn'.
#
# (3) 'Nn' doesn't make any sense (it's like saying 'Uu').  Disallow it.
#
# (4) We're not gonna have a 'U' at the beginning.
#
# (5) And we'll never have a 'u'.
#
# (6) When you've got a 'U', it doesn't matter what the lowercase EC is.
#
# (7) Keep Nc as Nc and Cn as Cn.  Unlike other pairs w/ N, these are
# equivalent.
#
# (8) RC=S should never result in a U.

so_ec_merge = {'B': {'S': {'Nc': 'Nc',
                           'Nx': 'Nx',
                           'Np': 'Np',
                           'Cn': 'Cn',
                           'Cc': 'Cc',
                           'Cx': 'Cx',
                           'Cp': 'Cp',
                           'Xn': 'Xn',
                           'Xc': 'Xc',
                           'Xx': 'Xx',
                           'Xp': 'Xp',
                           'Pn': 'Pn',
                           'Pc': 'Pc',
                           'Px': 'Px',
                           'Pp': 'Pp',
                           }
                     'O': {'Nc': 'Nc',
                           'Nx': 'Nx',
                           'Np': 'Np',
                           'Cn': 'Cn',
                           'Cc': 'Cc',
                           'Cx': 'Cx',
                           'Cp': 'Cp',
                           'Xn': 'U',
                           'Xc': 'U',
                           'Xx': 'U',
                           'Xp': 'U',
                           'Pn': 'U',
                           'Pc': 'U',
                           'Px': 'U',
                           'Pp': 'U',
                           }
                     }
               'Nc': {'S': {'Nc': 'Nc',
                            'Nx': 'Nx',
                            'Np': 'Np',
                            'Cn': 'Nc',
                            'Cc': 'Pc',
                            'Cx': 'Px',
                            'Cp': 'Pp',
                            'Xn': 'Pn',
                            'Xc': 'Pc',
                            'Xx': 'Px',
                            'Xp': 'Pp',
                            'Pn': 'Pn',
                            'Pc': 'Pc',
                            'Px': 'Px',
                            'Pp': 'Pp',
                            }
                      'O': {'Nc': 'Nc',
                            'Nx': 'Nx',
                            'Np': 'Np',
                            'Cn': 'Nc',
                            'Cc': 'Pc',
                            'Cx': 'Px',
                            'Cp': 'Pp',
                            'Xn': 'U',
                            'Xc': 'U',
                            'Xx': 'U',
                            'Xp': 'U',
                            'Pn': 'U',
                            'Pc': 'U',
                            'Px': 'U',
                            'Pp': 'U',
                            }
                      }
               'Nx': {'S': {'Nc': 'Nx',
                            'Nx': 'U', # Could be different part injected
                            'Np': 'U', # Could be different part injected
                            'Cn': 'Nx',
                            'Cc': 'Pc',
                            'Cx': 'Px',
                            'Cp': 'Pp',
                            'Xn': 'Pn', # This much is true.
                            'Xc': 'Pc',
                            'Xx': 'Px',
                            'Xp': 'Pp',
                            'Pn': 'Pn', # This much is true.
                            'Pc': 'Pc',
                            'Px': 'Px',
                            'Pp': 'Pp',
                            }
                      'O': {'Nc': '',
                            'Nx': '',
                            'Np': '',
                            'Cn': '',
                            'Cc': '',
                            'Cx': '',
                            'Cp': '',
                            'Xn': '',
                            'Xc': '',
                            'Xx': '',
                            'Xp': '',
                            'Pn': '',
                            'Pc': '',
                            'Px': '',
                            'Pp': '',
                            }
                      }
