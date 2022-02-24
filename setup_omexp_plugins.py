from setuptools import setup, find_packages

setup(
    name="opensesame-omexp-plugins",
    version = '1.0.0',
    description = "Oticon Medical Experiment Platform (OMEXP) plugins for OpenSesame",

    url = 'https://github.com/elus-om/BRM_OMEXP',

    author = 'Eleonora Sulas & Pierre-Yves Hasan',
    author_email = 'elus@oticonmedical.com',

    license = 'GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        # Status
        'Development Status :: 5 - Production/Stable',

        # Audience
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',

        # License
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Python version support
        'Programming Language :: Python :: 3.6.8',
    ],

    keywords='opensesame omexp',

    
    # OpenSesame packages are installed as auxiliary data
    data_files = [
        ('share/opensesame_plugins/adaptive_init', [
            'plugins/adaptive_init/info.yaml',
            'plugins/adaptive_init/adaptive_init.png',
            'plugins/adaptive_init/adaptive_init.py',
            'plugins/adaptive_init/adaptive_init_large.png',
        ]),

        ('share/opensesame_plugins/adaptive_next', [
            'plugins/adaptive_next/info.yaml',
            'plugins/adaptive_next/adaptive_next.png',
            'plugins/adaptive_next/adaptive_next.py',
            'plugins/adaptive_next/adaptive_next_large.png',
        ]),

        ('share/opensesame_plugins/calibration', [
            'plugins/calibration/info.yaml',
            'plugins/calibration/calibration.png',
            'plugins/calibration/calibration.py',
            'plugins/calibration/calibration_large.png',
            'plugins/calibration/libcalibration.py',
            'plugins/calibration/other/asio.png',
            'plugins/calibration/other/pause.png',
            'plugins/calibration/other/play.png',
            'plugins/calibration/other/play_base.png',
            'plugins/calibration/other/speak.png',
            'plugins/calibration/other/white_noise.wav',
        ]),

        ('share/opensesame_plugins/mixer', [
            'plugins/mixer/info.yaml',
            'plugins/mixer/mixer.png',
            'plugins/mixer/mixer.py',
            'plugins/mixer/mixer_large.png',
            'plugins/mixer/libmixer.py',
            'plugins/mixer/libqt.py',
            'plugins/mixer/mixer.md',
        ]),

        ('share/opensesame_plugins/lsl_start', [
            'plugins/lsl_start/info.yaml',
            'plugins/lsl_start/lsl_start.png',
            'plugins/lsl_start/lsl_start.py',
            'plugins/lsl_start/lsl_start_large.png',
            'plugins/lsl_start/libmixer.py',
        ]),

        ('share/opensesame_plugins/lsl_message', [
            'plugins/lsl_message/info.yaml',
            'plugins/lsl_message/lsl_message.png',
            'plugins/lsl_message/lsl_message.py',
            'plugins/lsl_message/lsl_message_large.png',
        ]),

        ('share/opensesame_plugins/lsl_stop', [
            'plugins/lsl_stop/info.yaml',
            'plugins/lsl_stop/lsl_stop.png',
            'plugins/lsl_stop/lsl_stop.py',
            'plugins/lsl_stop/lsl_stop_large.png',
        ]),      
        
       
    ]

)