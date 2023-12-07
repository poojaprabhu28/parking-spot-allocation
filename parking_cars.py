import random
import helpers
import logging

logging.getLogger().setLevel(logging.INFO)

""" Define Parking Lot attributes """
class ParkingLot:
    def __init__(self, total_sq_footage, spot_size):
        self.total_sq_footage = total_sq_footage
        self.spot_size = spot_size
        """ calculate number of cars of specific spot size that can be parked """
        self.total_spots_count = total_sq_footage // spot_size

        """ Create an array with total number of spots"""
        self.parking_lot_arr = [None] * self.total_spots_count

    # check if parking is available
    def is_spot_available(self, spot):
        return self.parking_lot_arr[spot] is None

    # Park the car if spot is available
    def park_car(self, spot, license_plate):
        if self.is_spot_available(spot):
            self.parking_lot_arr[spot] = license_plate
            return True
        else:
            return False
            
""" Define car attributes """
class Car:
    def __init__(self, license_plate):
        self.license_plate = license_plate

    # magic method to display license plate while fetching string output
    def __str__(self):
        return f"Car with license plate {self.license_plate}"
    
    # method to park the car if space is available, else reject it
    def park(self, parking_lot, spot):
        success = parking_lot.park_car(spot, self.license_plate)
        if success:
            return (f"{self} parked successfully in spot {spot+1}", True)
        else:
            return (f"{self} could not be parked in spot {spot+1}, trying another spot", False)


def main():
    try:
        # use user input values
        total_sq_footage = int(input("Enter parking lot area (default 2000 sq. feet): ") or "2000")
        spot_size = int(input("Enter area of the standard car to be parked (default 96 sq. feet): ") or "96")
        car_count = int(input("Enter number of cars to be parked (default 30): ") or "30")
        bucket_name = input("Enter name of AWS s3 bucket in your account: ") or "parking-lot-data"

        parking_lot = ParkingLot(total_sq_footage, spot_size)
        # generate random license plate numbers for car count provided
        cars = [Car(f"{random.randint(1000000, 9999999)}") for car in range(car_count)]
        parked_cars = []

        # assign parking spaces to cars at random
        while cars and None in parking_lot.parking_lot_arr:
            car = cars[0]
            spot_to_park = random.randint(0, parking_lot.total_spots_count - 1)
            status, is_parked = car.park(parking_lot, spot_to_park)

            if not is_parked and None in parking_lot.parking_lot_arr:
                # car not parked yet
                logging.info(status)
                continue
            elif None not in parking_lot.parking_lot_arr:
                # parking lot is full
                logging.info("Parking lot is full")
                break
                
            # car parked successfully
            logging.info(status)

            # append details of parked cars
            car_details = {
                "parking_number" : spot_to_park+1,
                "license" : car.license_plate
            }
            parked_cars.append(car_details)
            # remove car instance once parked
            cars.pop(0)

        # store parked car data in a json file
        file_name = helpers.store_data_to_file(parked_cars)

        # upload file to s3 bucket
        response = helpers.upload_to_s3_bucket(file_name, bucket_name)
        if response == "error":
            logging.error("File upload failed")
        else:
            response = helpers.delete_local_file(file_name)
            if response == "error":
                logging.error("Couldn't delete file")
            else:
                logging.info("deleted file")

        # cars not parked
        for car in cars:
            print(f"Car {car.license_plate} is not parked")
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()
