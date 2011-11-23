    # Keep in mind: An EC answers the question, How much of this
    # region connects to a specified amount of the other region?

    # An X or P with an N is as good as a U.  To conclude known-absence,
# we need to know about the missing part, but we can never get it.
#
# Edges going into this module are specific observations.  Edges
# coming out are guesses at reality.
# 
# All ECs w/out N reduce to Xx, because we don't know which region
# was injected and whether more than necessary or too little was injected:
#
# Note: CoCoMac curators DO know which region was injected; the Access
# DB has this info.

# The lowercase part of the ECs that use this dict in the same pass
# refer to the same other region (which has an RC to the other region
# in the desired bmap).

# A = desired source (or target)
# B = old target (or source)
# C = old source (or target) to which A has an RC

# Answering the question, How should we update our tentative
# conclusion -- that ___ amount of A connects to ___ amount of B --
# given that ___ amount of C connects to ___ amount of B?

# Because one of our regions has been injected, we are always missing
# some information: specifically, whether we needed to inject as much
# of the region as we did to see the observed amount of dye in the
# other region.  We must ignore this shortcoming.

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
#
# (9) Cp and Pc are better than Xx.  But C > X > P.  And when Xx is
# the best representation of what we know, use that.
#
# (10) Anything partnered with an N that's not C implies the
# unconsidered part has an unknown amount of connection.  For example,
# if part of a region connects, and the other part doesn't, we say Pc,
# not Pn.
#
#
# The following reductions can be made:
#
# Present: Any combinations of C, P, and X.
# Absent: C with N.
# Unknown: N with P or X.

# SO:
#    
# If ever you have an S to a region with a Present EC, you're gonna
# stay present.  The only way to be absent is to have RCs only to
# things that are absent.  An RC of O leads to Unknown unless EC is Absent.
#
# IL:
#
# I stays the same.  For L, present --> unknown, absent --> absent,
#    unknown --> unknown


so_ec_merge = {'B': {'S': {'Present': 'Present',
                           'Absent': 'Absent',
                           'Unknown': 'Unknown'
                           }
                     'O': {'Present': 'Unknown',
                           'Absent': 'Absent',
                           'Unknown': 'Unknown'
                           }
                     }
               'Present': {'S': {'Present': 'Present',
                                 'Absent': 'Present',
                                 'Unknown': 'Present'
                                 }
                      'O': {'Nc': 'Nc',
                            'Nx': 'Nx',
                            'Np': 'Np',
                            'Cn': 'Nc',
                            'Xn': 'U',
                            'Xx': 'U',
                            'Pn': 'U'
                            }
                      }
               'Nx': {'S': {'Nc': 'Nx',
                            'Nx': 'U', # Could be different part injected
                            'Np': 'U', # Could be different part injected
                            'Cn': 'Nx',
                            'Xn': 'Xn', # This much is true.
                            'Xx': 'Px',
                            'Pn': 'Pn', # This much is true.
                            }
                      'O': {'Nc': 'Nx',
                            'Nx': 'U', 
                            'Np': 'U',
                            'Cn': 'Nx',
                            'Xn': 'U',
                            'Xx': 'U',
                            'Pn': 'U',
                            }
                      }
               'Np': {'S': {'Nc': 'Np',
                            'Nx': 'U',
                            'Np': 'U',
                            'Cn': 'Np',
                            'Xn': 'Pn',
                            'Xx': 'Px',
                            'Pn': 'Pn',
                            }
                      'O': {'Nc': 'Np',
                            'Nx': 'U', 
                            'Np': 'U',
                            'Cn': 'Np',
                            'Xn': 'U',
                            'Xx': 'U',
                            'Pn': 'U'
                            }
                      }
               'Cn': {'S': {'Nc': 'Cn',
                            'Nx': 'Nx',
                            'Np': 'Np',
                            'Cn': 'Cn',
                            'Xn': 'Xn',
                            'Xx': 'Px',
                            'Pn': 'Pn'
                            }
                      'O': {'Nc': 'Cn',
                            'Nx': 'Nx', 
                            'Np': 'Np',
                            'Cn': 'Cn',
                            'Xn': 'U',
                            'Xx': 'U',
                            'Pn': 'U'
                            }
                      }
               'Xn': {'S': {'Nc': 'Xn',
                            'Nx': 'Xn',
                            'Np': 'Xn',
                            'Cn': 'Xn',
                            'Xn': 'Xn',
                            'Xx': 'Px',
                            'Pn': 'Xn'
                            }
                      'O': {'Nc': '',
                            'Nx': '', 
                            'Np': '',
                            'Cn': '',
                            'Xn': '',
                            'Xx': '',
                            'Pn': ''
                            }
                      }
