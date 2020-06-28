import datetime
import csv

# Server-wide orders. Will be sent via email each day at a specific time.
class Order:
    def __init__(self, order_type):
        super().__init__()
        self.order_type = order_type # Type of coffee being packaged for the order.
        self.number = 0 # Number of cups fulfilled in the order.
        now = datetime.datetime.now()
        self.start_time = now.strftime("%Y-%m-%d %H:%M") # Time at which this order began production.
        self.end_time = ""
        self.num_boxes = 0
        self.current_box_count = 0
        

    def end_order(self):
        now = datetime.datetime.now()
        self.end_time = now.strftime("%Y-%m-%d %H:%M")

class DailyOrders:
    def __init__(self):
        super().__init__()
        self.orders = list() # Server-wide list of cups.
        self.number = 0
        self.num_boxes = 0

        # Default box count is 24.
        self.box_count = 24

    def alter_box_count(self, new_count):
        print(f' * Box Count Change: Old Size({self.box_count}) -> New Size({new_count})')
        self.box_count = new_count

    def add_order(self, order_type):
        # If there is an order, end the previous order and add a new order.
        order_status = " * Order Change: "
        if self.orders:
            self.orders[-1].end_order()

            order_status += f'Old order({self.orders[-1].order_type}) -> '
        else:
            order_status += "No older order -> "
        order = Order(order_type) # creating an order will give it a start time.
        self.orders.append(order)
        order_status += f'New order({self.orders[-1].order_type})'
        print(order_status)

    def add_cup(self):
        if (not self.orders):
            self.add_order('No Order Selected')

        self.orders[-1].number += 1
        self.number += 1
        self.orders[-1].current_box_count += 1
        
        # Record a new box finished if enough cups have entered a box.
        # if (self.orders[-1].number % self.box_count == 0 and self.orders[-1].number > 0):
        #     self.add_box()
        if (self.orders[-1].current_box_count == self.box_count):
            self.add_box()

        file = open("production_info.csv", 'a', newline='')
        writer = csv.writer(file, delimiter=',')
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.orders[-1].order_type, self.orders[-1].number])
        file.close()

    def get_current_box_cups(self):
        return self.orders[-1].current_box_count

    def add_box(self):
        self.orders[-1].num_boxes += 1
        self.orders[-1].current_box_count -= self.box_count
        self.num_boxes += 1
        file = open("box_info.csv", 'a', newline='')
        writer = csv.writer(file, delimiter=',')
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.orders[-1].order_type, self.box_count, self.orders[-1].num_boxes])
        file.close()

    # Takes the last order in the order array and ends it.
    def end_orders(self):
        self.orders[-1].end_order()

    # Returns the last order in the order array.
    def get_current_order(self):
        if (not self.orders):
            self.add_order('No Order Selected')
        return self.orders[-1]

class OrderManager():

    def __init__(self):
        super().__init__()

    def generate_report(self, daily_order: DailyOrders):
        report = f'Orders for {datetime.datetime.now().strftime("%m-%d-%Y")}:\n'
        for order in daily_order.orders:
            report += f'{order.order_type} production began at {(order.start_time)[-5:]} and ended at {(order.end_time)[-5:]}, producing {order.number} cups.\n'
        return report

    def condense_report(self, daily_order: DailyOrders):
        with open("production_history.csv", "a", newline='') as file:
            writer = csv.writer(file, delimiter=',')
            for order in daily_order.orders:
                writer.writerow([datetime.datetime.now().strftime("%m-%d-%Y"), order.order_type, order.number, (order.start_time)[-5:], (order.end_time)[-5:]])
            file.close()
        with open("production_info.csv", "r+") as file:
            file.truncate(0)
            file.close()