import websocket
import thread
import time
import smbus
import json

bus = smbus.SMBus(1)

# This is the address we setup in the Arduino Program
address = 0x04

# create the channel JSON
channel_json = json.dumps({'channel': 'DevicesChannel'})

# when the websocket client connects to the server
def on_open(ws):
    print "open"
    #create the device subscription
    device_subscription = {
        'command': 'subscribe',
        'identifier': channel_json
    }

    # send the subscription command
    ws.send(json.dumps(device_subscription))
  
# when the websocket receives a message
def on_message(ws, data):
    #print data
    # if this is a ping command
    #print json.loads(message)
    # get the JSON data
    json_data = json.loads(data)

    # if this is a ping command
    if (json_data.get('type') == 'ping'):
        #print "ping command"
        pass
    # else if this is a subscription confirmation
    elif (json_data.get('type') == 'confirm_subscription'):
        print "subscribed to: " + json_data['identifier']
    # else if this is a device message, handle it
    elif (json_data.get('identifier') == channel_json):
        handle_device_message(json_data.get('message'))
    #else log the full message
    else:
        print('message received: ' + data)

# handle a device message
def handle_device_message(message):
    # calculate the delay
    start_time = (time.time() * 1000)
    delay = int(start_time - message.get('time'))

    if (message.get('value') == 'on'):
        # send message via i2c
        send_i2c_message('on')
    elif (message.get('value') == 'off'):
        # send message via i2c
        send_i2c_message('off')
    # if there is a servo command
    elif (len(message.get('servo')) > 0):
        # send the servo command
        send_i2c_message("servo_" + message.get('servo'))

    # set the i2c delay
    i2c_delay = (time.time() * 1000) - start_time
    print message.get('value', '') + ", ws delay: " + str(delay) + "ms, i2c delay: " + str(int(i2c_delay)) + "ms"

# send an i2c message
def send_i2c_message(message):
    rest_of_string = message[1:]
    string_array = map(ord, list(rest_of_string))
    bus.write_i2c_block_data(address, ord(message[0]), string_array)

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://192.168.0.7:3000/cable",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
