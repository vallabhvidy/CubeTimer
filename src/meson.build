pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'cube_timer_gtk'
gnome = import('gnome')

gnome.compile_resources('cube-timer',
  'cube-timer.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'cube-timer.in',
  output: 'cube-timer',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

cube_timer_gtk_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'timerlabel.py',
  'timer.py',
  'scramble.py',
  'score.py',
  'utils.py',
  'timercontroller.py',
  'preferences.py'
]

install_data(cube_timer_gtk_sources, install_dir: moduledir)
