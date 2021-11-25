CONFIG = {
    'controls': (
        #'Wemo',
        #'KuappiGPIO',
        #'ValloxControl',
        'AlarmControl',
        #'NetControl',
    ),
    #'sensor': 'W1Temp',
    #'sensor': 'MiTemp',
    #'sensor': 'MqttSensor',
    'sensor': 'NetSensor',
    #'mqtt_client': 'zigbee2mqtt/0x00158d00023278d1',
    #'mqtt_client_name': 'Kuappi',
    #'decision': 'FridgeDecision',
    #'decision': 'FridgeAlarmDecision',
    #'decision': 'ValloxDecision',
    'decision': 'FreezerDecision',
    #'decision': 'PassthruDecision',
    'summer_mode': False,
    'use_redis': False,
    'polling_freq': 60,
    'mitemp_addr': '58:2D:34:34:4C:3E',
    'mitemp_cache_timeout': 300,
    'gpio_pin': 22,
    'netctl_host': '0.0.0.0',
    'netctl_udp_port': 9999,
    'log_file': '/tmp/arkku.log',
    'zmq_recv_port': 8988,
    'zmq_send_port': 8989,
    'zmq_host': '192.168.1.9',
    'node_name': 'arkku',
}
