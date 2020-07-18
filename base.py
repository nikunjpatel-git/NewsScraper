from hindustan_times import HindustanTimes


if __name__ == '__main__':
    num_pages = 1
    while True:
        try:
            num_pages = int(input("Enter the number of max pages to scrap: "))
            break
        except ValueError:
            print("Please enter an integer....")

    ht = HindustanTimes(num_pages)
    ht.extract()
