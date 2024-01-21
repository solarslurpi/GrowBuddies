#############################################################################
# SPDX-FileCopyrightText: 2024 Margaret Johnson
#
# SPDX-License-Identifier: MIT
#
#############################################################################
from pid_handler_code import PIDHandler

"""This script starts up PID Control of the vpd and CO2 within different growing locations (for example, multiple tents). The properties within growbuddies_settings.json guide the system on what actuators will be controlled.  This is decided by the 'active' key within the PID configuration.
"""


def main():
    p = PIDHandler(tune=True)
    p.start()


if __name__ == "__main__":
    main()
