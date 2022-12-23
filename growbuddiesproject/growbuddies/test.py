from settings_code import Settings


# Define a callback function



def main():
    obj = None
    settings = Settings()
    settings.load()
    callbacks_dict = settings.get_callbacks("mistbuddy_mqtt_dict", obj)
    print(f'{callbacks_dict}')
    pass









    # func = globals().get("on_snifferbuddy_readings")
    # func("hello")
    # settings = Settings()
    # settings.load()
    # t_f = settings.get("snifferbuddy_mqtt_dict")
    # for k in t_f.keys():
    #     func = globals().get(t_f[k])
    #     func(f"{k}")

    # pass


if __name__ == "__main__":
    main()
