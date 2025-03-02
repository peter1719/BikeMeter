import time
import json
import random
import threading
import paho.mqtt.client as mqtt

class BikeSimulator:
    def __init__(self, device_id, mqtt_client, stop_event):
        self.device_id = device_id
        self.mqtt_client = mqtt_client
        self.current_speed = random.uniform(10, 30)  # 初始速度
        self.target_speed = random.uniform(10, 30)   # 目標速度
        self.stop_event = stop_event
        self.speed_change_interval = random.uniform(3, 8)  # 每隔3-8秒改變目標速度
        self.last_target_change = time.time()

    def update_target_speed(self):
        """更新目標速度"""
        current_time = time.time()
        if current_time - self.last_target_change > self.speed_change_interval:
            self.target_speed = random.uniform(10, 30)
            self.last_target_change = current_time
            self.speed_change_interval = random.uniform(3, 8)

    def generate_data(self):
        """生成平滑變化的速度數據"""
        self.update_target_speed()
        
        # 平滑地向目標速度靠近
        speed_diff = self.target_speed - self.current_speed
        # 每次更新速度的 5%
        adjustment = speed_diff * 0.05
        self.current_speed += adjustment
        
        data = {
            "timestamp": int(time.time() * 1000),
            "device_id": self.device_id,
            "speed": round(self.current_speed, 2)
        }
        return data

    def publish_data(self, topic):
        data = self.generate_data()
        self.mqtt_client.publish(topic, json.dumps(data))
        print(f"Published data from {self.device_id}: {data}")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def simulate_bike(device_id, mqtt_client, stop_event):
    simulator = BikeSimulator(device_id, mqtt_client, stop_event)
    topic = f"bike/{device_id}/data"
    while not stop_event.is_set():
        simulator.publish_data(topic)
        time.sleep(0.3)  # 每台腳踏車每 0.3 秒發送一次數據

def keyboard_interrupt_handler(stop_event):
    try:
        while True:
            time.sleep(0.1)  # 減少 CPU 使用率
    except KeyboardInterrupt:
        print("\nGracefully shutting down...")
        stop_event.set()

def main(bike_count=10):
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.connect("localhost", 1883, 60)

    mqtt_client.loop_start()

    stop_event = threading.Event()
    
    # 建立監聽中斷的線程
    interrupt_thread = threading.Thread(target=keyboard_interrupt_handler, args=(stop_event,))
    interrupt_thread.daemon = True
    interrupt_thread.start()

    threads = []
    for i in range(bike_count):
        device_id = f"bike_{i+1:03d}"
        thread = threading.Thread(target=simulate_bike, args=(device_id, mqtt_client, stop_event))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nGracefully shutting down...")
    finally:
        stop_event.set()
        mqtt_client.loop_stop()
        print("Simulation ended.")

if __name__ == "__main__":
    main(bike_count=1)