from pid_handler_code import PIDHandler

PID_config = "StomaBuddy_PID_config"

def main():
    pid_handler = PIDHandler(PID_config)
    pid_handler.start()


if __name__ == "__main__":
    main()
