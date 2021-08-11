CONFIG = {
    'controls': (
        #'Wemo',
        'KuappiGPIO',
        #'ValloxControl',
        #'AlarmControl',
        #'NetControl',
    ),
    #'sensor': 'W1Temp',
    #'sensor': 'MiTemp',
    'sensor': 'MqttSensor',
    #'sensor': 'NetSensor',
    'mqtt_client': 'zigbee2mqtt/0x00158d00023278d1',
    'mqtt_client_name': 'Kuappi',
    'decision': 'FridgeDecision',
    #'decision': 'FridgeAlarmDecision',
    #'decision': 'ValloxDecision',
    #'decision': 'FreezerDecision',
    'summer_mode': False,
    'use_redis': True,
    'polling_freq': 60,
    'mitemp_addr': '58:2D:34:34:4C:3E',
    'mitemp_cache_timeout': 300,
    'gpio_pin': 22,
    'netctl_host': '192.168.1.99',
    'netctl_udp_port': 9999,
    'log_file': '/tmp/kuappi.log',
}
