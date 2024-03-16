import json
from time import time
import os

def HTTPParse(request, cl,Reading, datafile):
        rlines=request.decode().splitlines()
        outdict=dict(zip(["Verb","URL","Lang"], rlines[0].split()))
        for i in rlines[1:-1]:
            outdict[i.split(":")[0].strip()]=i.split(":")[1].strip()
        
        if outdict['Verb'] == "GET":
            print("It's a GET request")
            if outdict['URL']!="/favicon.ico":
                htmlresponse = wp_receive(outdict['URL'],cl,Reading,datafile)
                if htmlresponse:
                    cl.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.sendall(htmlresponse)
                    cl.close()
            
        elif outdict['Verb'] == "PUT":
            print ("It's a PUT request")
        else:
            print ("It's a " + outdict['Verb'] + " request")


def wp_receive(request,client,dataline,datafile):
    pagedir={"/sensors.json":[wp_sensors,dataline],"/history.json":[wp_history,datafile],"/wipelogfile.yes":[wp_wipelog,datafile]}
    response = wp_NotFound
    responseparameter="Null"
    for key in pagedir:
        if key in request:
            response = pagedir[key][0]
            responseparameter=pagedir[key][1]
            break
    html=response(responseparameter,client)
    return html

def wp_sensors(dataline,client):
    html=json.dumps(dataline)
    return html

def wp_history(datafile,client):
    # Send the file in 1024-bytes chunks.
    with open(datafile, "rb") as f:
        while read_bytes := f.read(1024):
            client.sendall(read_bytes)
        client.close()
    return
        
def wp_wipelog(datafile,client):
    os.remove(datafile)
    with open(datafile, 'a') as f:
        pass
    return

def wp_NotFound(responseparameter,client):
    html="""
        <!DOCTYPE html>
            <html>
                <head> <title>Pico W</title> </head>
                <body> <h1>Water Fill</h1>
                <h2>Not Found!</h2>
        </body></html>
    """
    return html
