#!/usr/bin/env python
# encoding: utf-8
# Daniel Edwards, 23.09.2012

"""
Support for GObject Introspection.
"""
from waflib.Node import Node
from waflib.Task import Task
from waflib.Configure import conf
from waflib.TaskGen import taskgen_method, before_method, after_method, feature


class gir_scanner (Task):
    run_str = 'g-ir-scanner --warn-all ${GIR_QUIET} ${GIR_NS_ST:GIR_NS} ${GIR_NSV_ST:GIR_NSV} ${GIR_PROG_ST:GIR_PROG} ${GIR_PROG_ARGS_ST:GIR_PROG_ARGS} ${GIR_LIBPATH_ST:GIR_LIBPATHS} ${GIR_LIBRARY_ST:GIR_LIBRARIES} ${GIR_INCLUDE_ST:GIR_INCLUDES} ${GIR_CPP_INCLUDE_ST:GIR_CPP_INCLUDES} ${GIR_CPP_DEFINE_ST:GIR_CPP_DEFINES} ${GIR_PKG_ST:GIR_PKGS} ${GIR_TGT_ST:TGT} ${SRC}'
    color = 'BLUE'

class gir_compiler (Task):
    run_str = 'g-ir-compiler ${GIR_TGT_ST:TGT} ${SRC}'
    color = 'BLUE'


def configure (cfg):
    cfg.gir_configure ()

@conf
def gir_configure (cfg):
    cfg.env ['GIR_NS_ST'] = '--namespace=%s'
    cfg.env ['GIR_NSV_ST'] = '--nsversion=%s'
    cfg.env ['GIR_PROG_ST'] = '--program=%s'
    cfg.env ['GIR_PROG_ARGS_ST'] = '--program-args=%s'
    cfg.env ['GIR_LIBPATH_ST'] = '-L%s'
    cfg.env ['GIR_LIBRARY_ST'] = '-l%s'
    cfg.env ['GIR_INCLUDE_ST'] = '-i%s'
    cfg.env ['GIR_CPP_INCLUDE_ST'] = '-I%s'
    cfg.env ['GIR_CPP_DEFINE_ST'] = '-D%s'
    cfg.env ['GIR_PKG_ST'] = '--pkg=%s'
    cfg.env ['GIR_TGT_ST'] = '--output=%s'


@feature ('gir')
def gir_parse_args_method (tsg):
    setattr (tsg, 'gir_namespace', getattr (tsg, 'gir_namespace', 'Unknown'))
    setattr (tsg, 'gir_nsversion', getattr (tsg, 'gir_nsversion', '0.1'))
    setattr (tsg, 'gir_filename', '%s-%s' % (tsg.gir_namespace, tsg.gir_nsversion))
    setattr (tsg, 'gir_libpaths', getattr (tsg, 'gir_libpaths', []) + ['.'])
    setattr (tsg, 'gir_libraries', getattr (tsg, 'gir_libraries', []))
    setattr (tsg, 'gir_includes', getattr (tsg, 'gir_includes', []))
    setattr (tsg, 'gir_cpp_includes', getattr (tsg, 'gir_cpp_includes', []))
    setattr (tsg, 'gir_cpp_defines', getattr (tsg, 'gir_cpp_defines', []))
    setattr (tsg, 'gir_pkgs', getattr (tsg, 'gir_pkgs', []))
    setattr (tsg, 'gir_source', getattr (tsg, 'gir_source', []))

    setattr (tsg, 'gir_quiet', getattr (tsg, 'gir_quiet', True))

    use_set = getattr (tsg, 'use', set ())
    if type (use_set) is not list: use_set = set ([use_set])
    tsg.gir_libraries = list (set (tsg.gir_libraries) | use_set)

@feature ('gir')
@after_method ('gir_parse_args_method')
def gir_scanner_method (tsg):
    inputs = tsg.gir_source

    t = tsg.create_task ('gir_scanner')
    t.set_inputs (inputs)
    t.set_outputs (tsg.path.find_or_declare (tsg.gir_filename + '.gir'))

    t.env ['GIR_NS'] = [tsg.gir_namespace]
    t.env ['GIR_NSV'] = [tsg.gir_nsversion]
    if getattr (tsg, 'gir_program', None):
        t.env ['GIR_PROGRAM'] = tsg.gir_program
        t.env ['GIR_PROGRAM_ARGS'] = tgs.gir_program_args
    t.env ['GIR_LIBPATHS'] = tsg.gir_libpaths
    t.env ['GIR_LIBRARIES'] = tsg.gir_libraries
    t.env ['GIR_INCLUDES'] = tsg.gir_includes
    t.env ['GIR_CPP_INCLUDES'] = tsg.gir_cpp_includes
    t.env ['GIR_CPP_DEFINES'] = tsg.gir_cpp_defines
    t.env ['GIR_PKGS'] = tsg.gir_pkgs
    if tsg.gir_quiet:
        t.env ['GIR_QUIET'] = '--quiet'

@feature ('gir')
@after_method ('gir_scanner_method')
def gir_compiler_method (tsg):
    t = tsg.create_task ('gir_compiler')
    t.set_inputs (tsg.path.find_resource (tsg.gir_filename + '.gir'))
    t.set_outputs (tsg.path.find_or_declare (tsg.gir_filename + '.typelib'))


# vim: set ft=python :
