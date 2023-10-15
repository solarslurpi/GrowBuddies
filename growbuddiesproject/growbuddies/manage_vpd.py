from pid_handler_code import PIDHandler

MistBuddy_PID_config = "MistBuddy_PID_config"

def main():
    pid_handler = PIDHandler(MistBuddy_PID_config)
    pid_handler.start()


if __name__ == "__main__":
    main()