CONFIG = {
    'controls': (
        #'Wemo',
        'KuappiGPIO',
        #'ValloxControl',
    ),
    'sensor': 'W1Temp',
    #'sensor': 'MiTemp',
    'decision': 'FridgeDecision',
    #'decision': 'ValloxDecision',
    'use_redis': True,
    'polling_freq': 60,
    'mitemp_addr': '58:2D:34:34:4C:3E',
    'mitemp_cache_timeout': 300,
    'log_file': '/tmp/kuappi.log',
}
