CONFIG = {
    'controls': (
        #'Wemo',
        'KuappiGPIO',
        #'ValloxControl',
    ),
    #'sensor': 'W1Temp',
    #'sensor': 'MiTemp',
    'sensor': 'MqttSensor',
    'mqtt_client': 'zigbee2mqtt/0x00158d00023278d1',
    'decision': 'FridgeDecision',
    #'decision': 'ValloxDecision',
    'use_redis': True,
    'polling_freq': 60,
    'mitemp_addr': '58:2D:34:34:4C:3E',
    'mitemp_cache_timeout': 300,
    'log_file': '/tmp/kuappi.log',
}
