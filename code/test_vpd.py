from vpdbuddy_code import vpdBuddy


def callback(dict):
    # values in dict
    print(f"-> IN CALLBACK  {dict}")


def main():
    my_vpd = vpdBuddy(callback, manage=False)
    my_vpd.start()


if __name__ == "__main__":
    main()
