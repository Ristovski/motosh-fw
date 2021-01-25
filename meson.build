project('motosh', 'c',
    version : '0.1',
    default_options : ['warning_level=3'])
compiler = meson.get_compiler('c')

stm32_family = get_option('mcu').split('STM32')[1]
add_global_arguments(['-DSTM32' + stm32_family], language: 'c')

common_include_dirs = []
common_include_dirs += 'build/'
common_include_dirs += 'include/'

subdir('thirdparty')

fw_sources = [
    'src/main.c',
]

stm32l0_c_args = [
    '-mthumb',
    '-fdata-sections',
    '-ffunction-sections',
]

stm32l0_link_args = [
    '--static',
    '-T' + meson.current_source_dir() + '/stm32l0xx8.ld',
    '-L' + meson.current_source_dir() + '/thirdparty/libopencm3/lib/',
    '-nostartfiles',
    '-nostdlib',
    '-lgcc',
    #'-fno-exceptions',
    '--specs=nosys.specs',
    '--specs=nano.specs',
    '-Wl,--gc-sections',
]

elf = executable('motosh',
        [fw_sources],
        c_args: [stm32l0_c_args],
        link_args: [stm32l0_link_args],
        include_directories: [common_include_dirs],
        dependencies: [libopencm32_l0_dep],
        install : false)

objcopy = find_program('objcopy')
gen_fw = custom_target('fw',
        input: elf,
        output: ['motosh.bin'],
        command: [objcopy, '-Obinary', '@INPUT@', '@OUTPUT@'],
        depends: elf,
        build_by_default: true,
        install: true,
        install_dir: meson.current_source_dir() + '/sim/fw/')

renode = find_program('renode', required: false)
if renode.found()
    run_target('sim', command: ['sim.sh', 'motosh.bin'], depends: [gen_fw])
else
    # Graceful error message instead of a missing run_target or hard dependency
    run_target('sim', command: ['echo', 'Error: \'renode\' not found! Run \'ninja reconfigure\' after installing!'])
endif

conf_data = configuration_data()
conf_data.set('MCU', get_option('mcu'))
conf_data.set('version', meson.project_version())
conf_data.set('project', meson.project_name())
configure_file(input : 'include/config.h.in',
               output : 'config.h',
               configuration : conf_data)