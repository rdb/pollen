from setuptools import setup

setup(
    name='pollen.',
    version='1.0.0',
    options={
        'build_apps': {
            'include_patterns': {
                'assets/**',
                'settings.prc',
                'README.md',
            },
            'package_data_dirs': {
                'simplepbr': [
                    ('simplepbr/*.vert', '', {}),
                    ('simplepbr/*.frag', '', {}),
                ],
            },
            'gui_apps': {
                'run_game': 'run_game.py',
            },
            'icons': {
                'run_game': [
                   'assets/icons/icon-512.png',
                   'assets/icons/icon-128.png',
                   'assets/icons/icon-64.png',
                   'assets/icons/icon-48.png',
                   'assets/icons/icon-32.png'
                ],
            },
            'log_filename': "$USER_APPDATA/pollen/output.log",
            'log_append': False,
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
        },
    }
)
