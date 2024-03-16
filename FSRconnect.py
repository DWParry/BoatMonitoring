def connect():
    import network
    import ntptime
    import socket
    from time import sleep, time
    import secrets

    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()
    wlan.active(True)
    wlan.config(pm = wlan.PM_NONE)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    wlanconnectattempt=0
    while wlan.isconnected() == False and wlanconnectattempt<5:
        print('Waiting for connection...('+str(wlanconnectattempt)+')')
        sleep(1)
        wlanconnectattempt += 1
        
    if wlan.isconnected()==True:
        ip = wlan.ifconfig()[0]
        print(f'Connected on {ip}')

        # Open a socket
        address = (ip, 80)
        connection = socket.socket()
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        connection.setblocking(0)
        connection.bind(address)
        connection.listen(1)
        print(connection)

        time_set=False
        while not(time_set):
            try:
                ntptime.settime()
                print("Time Success!!")
                time_set=True
            except OSError:
                print("Time not Set")
                sleep(5)

        return connection
    else:
        return False
