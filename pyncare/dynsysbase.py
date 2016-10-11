#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File:        dynsysbase.py
    Author:      Efrain Torres-Lomas
    Email:       efrain@fisica.ugto.mx
    Github:      https://github.com/elchinot7
    Description: ToDo

"""
import numpy as np
from itertools import cycle
import sys
import orbit
import collections


class BaseDynSys(object):
    def __init__(self,
                 model=None,
                 model_pars=[],
                 var_names=None,  # Dictionary
                 Ndim=None,       # Int
                 orbits=None,     # orbits = [{'vars': OrderedDict([('x', -0.8), ('y', y0)]), 't': t, 'arrow_pos': [1, 100, 200], 'label': 'label0'},]
                 t=None,          # numpy.linspace
                 lines=None,      # List of strings
                 colors=None,     # Color scheme name
                 ):
        _color_schemes = {'deep': ["#4C72B0", "#55A868", "#C44E52",
                                   "#8172B2", "#CCB974", "#64B5CD"],
                          'muted': ["#4878CF", "#6ACC65", "#D65F5F",
                                    "#B47CC7", "#C4AD66", "#77BEDB"],
                          'pastel': ["#92C6FF", "#97F0AA", "#FF9F9A",
                                     "#D0BBFF", "#FFFEA3", "#B0E0E6"],
                          'bright': ["#003FFF", "#03ED3A", "#E8000B",
                                     "#8A2BE2", "#FFC400", "#00D7FF"],
                          'dark': ["#001C7F", "#017517", "#8C0900",
                                   "#7600A1", "#B8860B", "#006374"],
                          'colorblind': ["#0072B2", "#009E73", "#D55E00",
                                         "#CC79A7", "#F0E442", "#56B4E9"],
                          'black': ["k"], }
        _lines = ["-", "--", ".-", ":"]

        self.model = model

        self.model_pars = model_pars

        if Ndim is not None:
            self.Ndim = Ndim
        else:
            sys.exit("Ndim must be an positive integer")

        if var_names is None:
            self.var_names = {}
            for i in Ndim:
                name = 'x_{}'.format(str(i))
                self.var_names[name] = name
        else:
            self.var_names = var_names

        if orbits is not None:
            self.orbits = orbits
        else:
            sys.exit("The orbits settings must be defined.")

        # if t is not None:
        #     self.t = t
        # else:
        #     sys.exit("Define time as a numpy.linspace")

        if lines is None:
            self.lines = _lines
        else:
            self.lines = lines

        if colors is None:
            self.colors = _color_schemes['dark']
        else:
            if colors in ['deep', 'muted', 'pastel', 'bright', 'dark', 'colorblind', 'black']:
                self.colors = _color_schemes[colors]
            else:
                sys.exit("color scheme not defined, <colors> must be on of\n \
                         [None, 'deep', 'muted', 'pastel', 'bright', 'dark', \
                         'colorblind', 'black']")

        # If all went well, create the Orbit Objects:
        self._orbits = []  # To be filled with Orbits instances
        for orb in self.orbits:
            d0 = collections.OrderedDict()  # must be an collections.OrderedDict
            for key, value in orb['vars'].iteritems():  # fill the initial data
                d0[key] = value
            # print d0
            t = orb['t']                    # time to evolve the orbit
            label = orb['label']
            _orbit = orbit.Orbit(init_cond=d0,
                                 model=self.model,
                                 model_pars=self.model_pars,
                                 t=t,
                                 label=label)
            self._orbits.append(_orbit)          # list full of <orbit.Orbit> instances

    def __str__(self):
        return self.out_info()

    def __call__(self, *args, **kwargs):
        "Displays some specific output"
        for d in sorted(dir(self)):
            print "{}: {}". format(d, str(getattr(self, d)))

    def out_info(self):
        """Prints the state of the Dynamical System"""
        out = '\n=====================================\n'
        out += 'This is a <<{}>> object'.format(self.__class__.__name__)
        out += '\n-------------------------------------\n'
        out += 'Equations are given by function:\n\t{}'.format(self.model.__name__)
        out += '\nNdims :\n\t{}\n'.format(self.Ndim)
        out += 'List of initial conditions:\n'
        if hasattr(self, 'orbits'):
            for orb in self.orbits:
                s = ''
                for key, value in orb['vars'].iteritems():
                    s += '{}={}, '.format(key, value)
                out += '\t[{}]\n'.format(s)
        out += '\n=====================================\n'
        return out

    def plot_orbits(self, ax, vars_to_plot, colors=None, add_flow=True, **kwargs):
        if colors is None:
            colorcycler = cycle(self.colors)
        else:
            colorcycler = cycle(colors)

        for i, orb in enumerate(self._orbits):
            color = next(colorcycler)
            orb.plot_orbit(ax=ax, vars_to_plot=vars_to_plot,
                           color=color, **kwargs)
            if add_flow:
                orb.plot_flow_over_orbit(ax=ax, vars_to_plot=vars_to_plot,
                                         flow_index=self.orbits[i]['arrow_pos'],
                                         color=color, **kwargs)
        ax.legend(loc='best')
        ax.set_xlabel(self.var_names[vars_to_plot[0]])
        ax.set_ylabel(self.var_names[vars_to_plot[1]])


def test_model(init, t=None, model_pars=[]):
    '''
    This defines the dynamical system for model
    :math:`V = m^2 \phi^2/2`
    '''
    x1 = init[0]
    y1 = init[1]
    # the model equations
    x1_dot = y1
    y1_dot = -x1 - 3.0 * y1 * np.sqrt(x1**2.0 + y1**2.0)
    return [x1_dot, y1_dot]


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from collections import OrderedDict

    fig = plt.figure()
    ax = fig.add_subplot(111)

    t = np.linspace(0.0, 10.0, 500)

    var_names = {'x': r'$X$', 'y': r'$Y$'}

    orbits = [{'vars': OrderedDict([('x', 0.1), ('y', 0.2)]), 't': t, 'arrow_pos': [5, 10, -20], 'label': 'label0'},
              {'vars': OrderedDict([('x', -0.3), ('y', -0.4)]), 't': t, 'arrow_pos': [5, 10, -20], 'label': 'label1'},
              {'vars': OrderedDict([('x', 0.2), ('y', -0.6)]), 't': t, 'arrow_pos': [5, 10, -20], 'label': 'label2'},
              {'vars': OrderedDict([('x', 0.4), ('y', 0.3)]), 't': t, 'arrow_pos': [5, 10, -50], 'label': 'label3'},
              {'vars': OrderedDict([('x', 0.5), ('y', 0.6)]), 't': t, 'arrow_pos': [5, 10, -50], 'label': 'label4'},
              ]

    dynsys = BaseDynSys(model=test_model,
                        model_pars=[],
                        var_names=var_names,
                        Ndim=2,
                        orbits=orbits,
                        colors='bright',)
    print dynsys
    print 'The list of generated Orbits instances:\n', dynsys._orbits
    dynsys.plot_orbits(ax=ax, vars_to_plot=['x', 'y'], linewidth=2)

    plt.show()
