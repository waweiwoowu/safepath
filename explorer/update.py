import time
from database import UpdateTrafficAccidentData


def update_traffic_accident_data(count=1):
    print("Start updating 'TrafficAccident' table.")
    print()
    start_time = time.time()
    for i in range(count):
        print(f"Round {i} has started. Collecting data...")
        round_start_time = time.time()
        update = UpdateTrafficAccidentData()
        round_end_time = time.time()
        round_execution_time = round_end_time - round_start_time
        print(f"{update.number_of_data} records were successfully added to the database!")
        print(f"Round Execution Time: {round_execution_time/60:.2f} minutes")
        print()
    end_time = time.time()
    execution_time = end_time - start_time
    print()
    print("Finished!")
    print(f"Total Execution Time: {execution_time/60:.2f} minutes ({execution_time/60/60:.2f} hours)")


if __name__ == "__main__":
    update_traffic_accident_data()