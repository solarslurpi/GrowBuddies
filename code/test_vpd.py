from vpdbuddy_code import vpdBuddy


def callback(dict):
    # values in dict
    print(f"{dict}")


def main():
    my_vpd = vpdBuddy(callback, manage=True)
    my_vpd.start()


if __name__ == "__main__":
    main()
