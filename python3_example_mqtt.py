#!/usr/bin/python3
import time
import io, json    # Needed for exporting payloads to json file
import argparse
import logging
import base64
import binascii
import http.client 

import paho.mqtt.client as mqtt  # mqtt library

class mqttStoreForward:
        
    isConnected = False                 # Checks ethernet connection
    lora_client = mqtt.Client() 
    packet = None                       # Will carry msg payload, empty to begin with
    jsonFilePath = 'packetStorage.json' # Input desired json file name here or leave default                      
    payloadData = None                  # Sets the payload data empty

    # Touch json file if it does not exist
    def __init__(self):
        try:
            # Create the file if it does not exist.
            with open(self.jsonFilePath, 'x') as file:
                pass
        except FileExistsError:
            pass

    # Connects LoRa client to localhost
    def setLoraClient(self):
        self.lora_client.connect("127.0.0.1")

    # Callback function initiated on on_connect for LoRa client
    def loraOnConnect(self, client, userdata, flags, rc):
        print("LoRa Client Connection : " + str(rc))
        self.lora_client.subscribe("lora/+/up", qos=0)
        self.isConnected = True

    # Callback function initiated on on_disconnect property for both clients
    def onDisconnect(self, client, userdata, rc):
        self.isConnected = False
        print("The connection has failed.")
  
    # Helper function: append the received packet to the JSON file.
    def store_packet(self):
        # First, try to read the existing contents.
        try:
            with open(self.jsonFilePath, 'r') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
        
        # Append the new packet.
        data.append(self.packet)
        
        # Write the updated list back to file.
        with open(self.jsonFilePath, 'w') as f:
            json.dump(data, f, indent=4)
        print("Stored packet to file.")

    # Callback function initiated on on_message
    def onMessage(self, client, userdata, msg):
        try:
            self.packet = json.loads(msg.payload)
        except json.JSONDecodeError:
            print("Received payload is not valid JSON.")
            return

        print("Received packet:")
        print(self.packet)
        # Append the packet to the JSON file.
        self.store_packet()
        
    def setVals(self):
        self.lora_client.on_connect = self.loraOnConnect
        self.lora_client.on_message = self.onMessage
        self.lora_client.on_disconnect = self.onDisconnect

    # Creates an infinite loop needed for paho mqtt loop-forever()
    def runLoop(self):
        while True:
            time.sleep(1)

    # Creates the event loop and new thread that initializes the paho mqtt loops for both clients
    def startLoop(self):
        self.lora_client.loop_start()

def main():
    instance = mqttStoreForward()       # Creates instance of class
    instance.startLoop()
    # Need to call setVals first because they won't connect to the callbacks if the setClient functions are called first
    instance.setVals()
    instance.setLoraClient()            # Connects to localhost
    
    instance.runLoop()

if __name__ == "__main__":
    main()
