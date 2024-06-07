import time
from database import UpdateTrafficAccidentData, UpdateEarthquakeData, \
                     UpdateAttractionData, UpdateRestaurantData


def update_traffic_accident_data(count=1):
    print("Start updating TrafficAccident table.")
    print("----------------")
    start_time = time.time()
    records = 0
    for i in range(count):
        print(f"Round {i+1} has started. (Collecting data...)")
        round_start_time = time.time()
        update = UpdateTrafficAccidentData()
        records += update.number_of_data
        round_end_time = time.time()
        round_execution_time = round_end_time - round_start_time
        print(f"{update.number_of_data} records were successfully added to the database!")
        print(f"Round Execution Time: {round_execution_time/60:.1f} minutes")
        print("----------------")
    end_time = time.time()
    execution_time = end_time - start_time
    print("Update finished!")
    print(f"{records} records were successfully added to the database!")
    print(f"Total Execution Time: {execution_time/60:.1f} minutes ({execution_time/60/60:.1f} hours)")

def update_earthquake_data(count=1):
    print("Start updating Earthquake table.")
    print("----------------")
    start_time = time.time()
    records = 0
    for i in range(count):
        print(f"Round {i+1} has started. (Collecting data...)")
        round_start_time = time.time()
        update = UpdateEarthquakeData()
        records += update.number_of_data
        round_end_time = time.time()
        round_execution_time = round_end_time - round_start_time
        print(f"{update.number_of_data} records were successfully added to the database!")
        print(f"Round Execution Time: {round_execution_time/60:.1f} minutes")
        print("----------------")
    end_time = time.time()
    execution_time = end_time - start_time
    print("Update finished!")
    print(f"{records} records were successfully added to the database!")
    print(f"Total Execution Time: {execution_time/60:.1f} minutes ({execution_time/60/60:.1f} hours)")

def updata_hotspot_data():
    print("Start updating Hotspot table.")
    print("Collecting data...")
    start_time = time.time()
    update = UpdateAttractionData()
    end_time = time.time()
    execution_time = end_time - start_time
    print("----------------")
    print("Update finished!")
    print(f"{update.number_of_data} records were successfully added to the database!")
    print(f"Total Execution Time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")

# def updata_restaurant_data():
#     print("Start updating Restaurant table.")
#     print("Collecting data...")
#     start_time = time.time()
#     update = UpdateRestaurantData()
#     end_time = time.time()
#     execution_time = end_time - start_time
#     print("----------------")
#     print("Update finished!")
#     print(f"{update.number_of_data} records were successfully added to the database!")
#     print(f"Total Execution Time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")


if __name__ == "__main__":
    # update_traffic_accident_data()
    # print()
    # update_earthquake_data()
    # updata_hotspot_data()
    # updata_restaurant_data()
    pass